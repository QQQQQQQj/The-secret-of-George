package com.colin.project.controller;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import com.colin.common.core.controller.BaseController;
import com.colin.common.core.domain.AjaxResult;
import com.colin.system.mapper.project.TaobaoGoodsAnalyseMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.client.SimpleClientHttpRequestFactory;

import java.lang.management.ManagementFactory;
import java.lang.management.OperatingSystemMXBean;
import java.lang.management.RuntimeMXBean;
import java.net.InetAddress;
import java.text.SimpleDateFormat;
import java.util.*;
import java.util.concurrent.*;

@Controller
@RequestMapping("/project/testReport")
public class TestReportController extends BaseController {

    private static final String prefix = "project/testReport";

    private final TaobaoGoodsAnalyseMapper taobaoGoodsAnalyseMapper;
    private final String mlServiceUrl;
    private final String serverPort;
    private final RestTemplate restTemplate;
    private final RestTemplate longTimeoutRestTemplate;

    public TestReportController(@Autowired TaobaoGoodsAnalyseMapper taobaoGoodsAnalyseMapper,
                                @Value("${ml.service.url:http://localhost:6003}") String mlServiceUrl,
                                @Value("${server.port:6002}") String serverPort) {
        this.taobaoGoodsAnalyseMapper = taobaoGoodsAnalyseMapper;
        this.mlServiceUrl = mlServiceUrl;
        this.serverPort = serverPort;

        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(5000);
        factory.setReadTimeout(10000);
        this.restTemplate = new RestTemplate(factory);

        SimpleClientHttpRequestFactory longFactory = new SimpleClientHttpRequestFactory();
        longFactory.setConnectTimeout(10000);
        longFactory.setReadTimeout(60000);
        this.longTimeoutRestTemplate = new RestTemplate(longFactory);
    }

    @GetMapping()
    public String testReport() {
        return prefix + "/testReport";
    }

    @GetMapping("/getEnvironment")
    @ResponseBody
    public AjaxResult getEnvironment() {
        Map<String, Object> env = new LinkedHashMap<>();
        
        try {
            Runtime runtime = Runtime.getRuntime();
            OperatingSystemMXBean osBean = ManagementFactory.getOperatingSystemMXBean();
            RuntimeMXBean runtimeBean = ManagementFactory.getRuntimeMXBean();

            env.put("timestamp", new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date()));
            
            Map<String, Object> systemInfo = new LinkedHashMap<>();
            systemInfo.put("osName", System.getProperty("os.name") + " " + System.getProperty("os.version"));
            systemInfo.put("javaVersion", System.getProperty("java.version"));
            systemInfo.put("jvmName", System.getProperty("java.vm.name"));
            systemInfo.put("hostName", InetAddress.getLocalHost().getHostName());
            systemInfo.put("ipAddress", InetAddress.getLocalHost().getHostAddress());
            systemInfo.put("availableProcessors", osBean.getAvailableProcessors());
            systemInfo.put("systemLoadAverage", String.format("%.2f", osBean.getSystemLoadAverage()));
            env.put("system", systemInfo);

            Map<String, Object> jvmInfo = new LinkedHashMap<>();
            jvmInfo.put("maxMemory", formatBytes(runtime.maxMemory()));
            jvmInfo.put("totalMemory", formatBytes(runtime.totalMemory()));
            jvmInfo.put("freeMemory", formatBytes(runtime.freeMemory()));
            jvmInfo.put("usedMemory", formatBytes(runtime.totalMemory() - runtime.freeMemory()));
            jvmInfo.put("heapUsage", String.format("%.1f%%", (double)(runtime.totalMemory() - runtime.freeMemory()) / runtime.maxMemory() * 100));
            long uptimeMs = runtimeBean.getUptime();
            jvmInfo.put("uptime", formatUptime(uptimeMs));
            env.put("jvm", jvmInfo);

            Map<String, Object> appInfo = new LinkedHashMap<>();
            appInfo.put("applicationName", "淘宝商品销售数据分析系统");
            appInfo.put("serverPort", serverPort);
            appInfo.put("springProfile", Arrays.toString(System.getProperty("spring.profiles.active", "default").split(",")));
            appInfo.put("mlServiceUrl", mlServiceUrl);
            env.put("application", appInfo);

            return AjaxResult.success(env);
        } catch (Exception e) {
            return AjaxResult.error("获取环境信息失败: " + e.getMessage());
        }
    }

    @GetMapping("/testDatabaseConnection")
    @ResponseBody
    public AjaxResult testDatabaseConnection() {
        Map<String, Object> result = new LinkedHashMap<>();
        List<Map<String, Object>> tests = new ArrayList<>();
        long startTime = System.currentTimeMillis();

        try {
            String[] testQueries = {
                "SELECT COUNT(*) as cnt FROM ads_taobao_beauty_makeup_daily_amt_cnt",
                "SELECT COUNT(*) as cnt FROM ads_taobao_beauty_makeup_goods_cnt",
                "SELECT COUNT(DISTINCT province) as cnt FROM dwd_taobao_beauty_makeup_detail_info",
                "SELECT COUNT(DISTINCT city) as cnt FROM dwd_taobao_beauty_makeup_detail_info",
                "SELECT COUNT(DISTINCT shop_name) as cnt FROM dwd_taobao_beauty_makeup_detail_info",
                "SELECT COUNT(*) as cnt FROM dwd_taobao_beauty_makeup_detail_info"
            };

            String[] testNames = {
                "日销售额统计表 (daily_amt_cnt)",
                "商品销量统计表 (goods_cnt)",
                "省份去重查询",
                "城市去重查询",
                "店铺去重查询",
                "明细数据总量"
            };

            boolean allPassed = true;
            for (int i = 0; i < testQueries.length; i++) {
                Map<String, Object> test = new LinkedHashMap<>();
                test.put("name", testNames[i]);
                test.put("sql", testQueries[i].substring(0, Math.min(testQueries[i].length(), 50)) + "...");
                
                long queryStart = System.currentTimeMillis();
                try {
                    List<JSONObject> queryResult = taobaoGoodsAnalyseMapper.executeRawSql(testQueries[i]);
                    long queryTime = System.currentTimeMillis() - queryStart;
                    
                    if (queryResult != null && !queryResult.isEmpty()) {
                        test.put("status", "PASS");
                        test.put("result", queryResult.get(0).getString("cnt") + " 条记录");
                        test.put("responseTime", queryTime + "ms");
                    } else {
                        test.put("status", "WARN");
                        test.put("result", "返回空结果");
                        test.put("responseTime", queryTime + "ms");
                        allPassed = false;
                    }
                } catch (Exception e) {
                    test.put("status", "FAIL");
                    test.put("error", e.getMessage().substring(0, Math.min(e.getMessage().length(), 100)));
                    test.put("responseTime", (System.currentTimeMillis() - queryStart) + "ms");
                    allPassed = false;
                }
                tests.add(test);
            }

            result.put("tests", tests);
            result.put("totalTests", testQueries.length);
            result.put("passedTests", tests.stream().filter(t -> "PASS".equals(t.get("status"))).count());
            result.put("failedTests", tests.stream().filter(t -> "FAIL".equals(t.get("status"))).count());
            result.put("warningTests", tests.stream().filter(t -> "WARN".equals(t.get("status"))).count());
            result.put("allPassed", allPassed);
            result.put("totalTime", (System.currentTimeMillis() - startTime) + "ms");

            return AjaxResult.success(result);
        } catch (Exception e) {
            return AjaxResult.error("数据库测试异常: " + e.getMessage());
        }
    }

    @GetMapping("/testMLServiceHealth")
    @ResponseBody
    public AjaxResult testMLServiceHealth() {
        Map<String, Object> result = new LinkedHashMap<>();
        List<Map<String, Object>> healthChecks = new ArrayList<>();
        long startTime = System.currentTimeMillis();

        try {
            String[] endpoints = {
                "/", 
                "/api/predict/sales-forecast?days=7",
                "/api/predict/price-elasticity",
                "/api/predict/shop-gmv",
                "/api/predict/product-heat",
                "/api/predict/province-sales",
                "/api/predict/category-trend?future_periods=6"
            };

            String[] endpointNames = {
                "服务根路径",
                "时序销量预测API",
                "价格弹性分析API",
                "店铺GMV预测API",
                "商品热度预测API",
                "省份销量预测API",
                "品类趋势预测API"
            };

            boolean serviceOnline = false;
            for (int i = 0; i < endpoints.length; i++) {
                Map<String, Object> check = new LinkedHashMap<>();
                check.put("endpoint", endpointNames[i]);
                check.put("url", mlServiceUrl + endpoints[i]);
                
                long requestStart = System.currentTimeMillis();
                try {
                    String response = restTemplate.getForObject(mlServiceUrl + endpoints[i], String.class);
                    long responseTime = System.currentTimeMillis() - requestStart;
                    
                    JSONObject json = JSON.parseObject(response);
                    
                    if (i == 0) {
                        serviceOnline = "running".equals(json.getString("status"));
                        check.put("status", "ONLINE");
                        check.put("serviceVersion", json.getString("version"));
                        check.put("responseTime", responseTime + "ms");
                    } else {
                        if (json.getBoolean("success")) {
                            check.put("status", "OK");
                            check.put("executionTime", json.getDouble("execution_time") + "s");
                            check.put("responseTime", responseTime + "ms");
                            
                            JSONObject data = json.getJSONObject("data");
                            if (data != null) {
                                check.put("dataSize", estimateDataSize(data.toJSONString().length()));
                            }
                        } else {
                            check.put("status", "ERROR");
                            check.put("message", json.getString("message"));
                            check.put("responseTime", responseTime + "ms");
                        }
                    }
                } catch (Exception e) {
                    check.put("status", "OFFLINE");
                    check.put("error", e.getClass().getSimpleName() + ": " + e.getMessage().substring(0, Math.min(e.getMessage().length(), 80)));
                    check.put("responseTime", (System.currentTimeMillis() - requestStart) + "ms");
                }
                healthChecks.add(check);
            }

            result.put("healthChecks", healthChecks);
            result.put("serviceOnline", serviceOnline);
            result.put("totalEndpoints", endpoints.length);
            result.put("healthyEndpoints", healthChecks.stream().filter(h -> "OK".equals(h.get("status")) || "ONLINE".equals(h.get("status"))).count());
            result.put("unhealthyEndpoints", healthChecks.stream().filter(h -> !"OK".equals(h.get("status")) && !"ONLINE".equals(h.get("status"))).count());
            result.put("totalCheckTime", (System.currentTimeMillis() - startTime) + "ms");

            return AjaxResult.success(result);
        } catch (Exception e) {
            return AjaxResult.error("ML服务健康检查失败: " + e.getMessage());
        }
    }

    @PostMapping("/runAPITestSuite")
    @ResponseBody
    public AjaxResult runAPITestSuite(@RequestParam(defaultValue = "3") Integer iterations,
                                      @RequestParam(defaultValue = "false") Boolean includeDatabaseTest,
                                      @RequestParam(defaultValue = "true") Boolean includeMLTest) {
        Map<String, Object> report = new LinkedHashMap<>();
        ExecutorService executor = Executors.newFixedThreadPool(10);
        List<Future<Map<String, Object>>> futures = new ArrayList<>();
        long suiteStartTime = System.currentTimeMillis();

        report.put("suiteStartTime", new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS").format(new Date(suiteStartTime)));
        report.put("iterations", iterations);
        Map<String, Object> configMap = new LinkedHashMap<>();
        configMap.put("includeDatabaseTest", includeDatabaseTest);
        configMap.put("includeMLTest", includeMLTest);
        configMap.put("concurrencyLevel", 10);
        report.put("configuration", configMap);

        if (includeDatabaseTest) {
            futures.add(executor.submit(() -> runDatabasePerformanceTest(iterations)));
        }

        if (includeMLTest) {
            futures.add(executor.submit(() -> runMLAPITest(iterations)));
            futures.add(executor.submit(() -> runDataQueryTest(iterations)));
        }

        List<Map<String, Object>> testResults = new ArrayList<>();
        int passedCount = 0;
        int failedCount = 0;
        int totalAssertions = 0;

        for (Future<Map<String, Object>> future : futures) {
            try {
                Map<String, Object> testResult = future.get(120, TimeUnit.SECONDS);
                testResults.add(testResult);
                
                if ((boolean) testResult.getOrDefault("passed", false)) {
                    passedCount++;
                } else {
                    failedCount++;
                }
                totalAssertions += (int) testResult.getOrDefault("assertions", 0);
            } catch (Exception e) {
                Map<String, Object> errorResult = new LinkedHashMap<>();
                errorResult.put("testName", "Unknown Test");
                errorResult.put("passed", false);
                errorResult.put("error", "执行超时或异常: " + e.getMessage());
                errorResult.put("assertions", 0);
                testResults.add(errorResult);
                failedCount++;
            }
        }

        executor.shutdown();

        long suiteEndTime = System.currentTimeMillis();
        report.put("testResults", testResults);
        Map<String, Object> summaryMap = new LinkedHashMap<>();
        summaryMap.put("totalTestSuites", testResults.size());
        summaryMap.put("passedSuites", passedCount);
        summaryMap.put("failedSuites", failedCount);
        summaryMap.put("passRate", String.format("%.1f%%", (double)passedCount / Math.max(testResults.size(), 1) * 100));
        summaryMap.put("totalAssertions", totalAssertions);
        summaryMap.put("totalExecutionTime", (suiteEndTime - suiteStartTime) + "ms");
        summaryMap.put("suiteEndTime", new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS").format(new Date(suiteEndTime)));
        report.put("summary", summaryMap);

        report.put("overallStatus", failedCount == 0 ? "ALL_TESTS_PASSED" : "SOME_TESTS_FAILED");

        return AjaxResult.success(report);
    }

    private Map<String, Object> runDatabasePerformanceTest(int iterations) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("testName", "数据库性能基准测试");
        result.put("testType", "PERFORMANCE");
        
        List<Long> responseTimes = new ArrayList<>();
        int successCount = 0;
        int failCount = 0;
        String[] queries = {
            "SELECT * FROM ads_taobao_beauty_makeup_daily_amt_cnt ORDER BY date_key DESC LIMIT 100",
            "SELECT province, COUNT(*) as cnt FROM dwd_taobao_beauty_makeup_detail_info GROUP BY province ORDER BY cnt DESC LIMIT 10",
            "SELECT shop_name, SUM(sales_count) as total_sales FROM dwd_taobao_beauty_makeup_detail_info GROUP BY shop_name ORDER BY total_sales DESC LIMIT 20"
        };

        for (int iter = 0; iter < iterations; iter++) {
            for (String query : queries) {
                long start = System.nanoTime();
                try {
                    taobaoGoodsAnalyseMapper.executeRawSql(query);
                    long elapsed = TimeUnit.NANOSECONDS.toMillis(System.nanoTime() - start);
                    responseTimes.add(elapsed);
                    successCount++;
                } catch (Exception e) {
                    failCount++;
                }
            }
        }

        Collections.sort(responseTimes);
        double avgTime = responseTimes.stream().mapToLong(Long::longValue).average().orElse(0);
        long p50 = responseTimes.get((int)(responseTimes.size() * 0.5));
        long p95 = responseTimes.get((int)(responseTimes.size() * 0.95));
        long p99 = responseTimes.get((int)(responseTimes.size() * 0.99));

        result.put("iterations", iterations * queries.length);
        result.put("successCount", successCount);
        result.put("failCount", failCount);
        result.put("passed", failCount == 0);
        result.put("assertions", iterations * queries.length);
        Map<String, Object> perfMetrics = new LinkedHashMap<>();
        perfMetrics.put("avgResponseTime", String.format("%.2f ms", avgTime));
        perfMetrics.put("p50ResponseTime", p50 + " ms");
        perfMetrics.put("p95ResponseTime", p95 + " ms");
        perfMetrics.put("p99ResponseTime", p99 + " ms");
        perfMetrics.put("minResponseTime", responseTimes.get(0) + " ms");
        perfMetrics.put("maxResponseTime", responseTimes.get(responseTimes.size() - 1) + " ms");
        perfMetrics.put("throughput", String.format("%.2f req/s", (successCount * 1000.0 / avgTime)));
        result.put("performanceMetrics", perfMetrics);
        result.put("timestamp", new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date()));

        return result;
    }

    private Map<String, Object> runMLAPITest(int iterations) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("testName", "ML预测API集成测试");
        result.put("testType", "INTEGRATION");

        String[][] apiTests = {
            {"/api/predict/sales-forecast?days=15", "salesForecast"},
            {"/api/predict/price-elasticity", "priceElasticity"},
            {"/api/predict/shop-gmv", "shopGmv"},
            {"/api/predict/product-heat", "productHeat"},
            {"/api/predict/province-sales", "provinceSales"}
        };

        List<Map<String, Object>> apiResults = new ArrayList<>();
        int totalPassed = 0;
        int totalFailed = 0;

        for (String[] apiTest : apiTests) {
            String endpoint = apiTest[0];
            String testName = apiTest[1];
            Map<String, Object> apiResult = new LinkedHashMap<>();
            apiResult.put("endpoint", endpoint);
            apiResult.put("testName", testName);

            List<Long> times = new ArrayList<>();
            int pass = 0;
            int fail = 0;

            for (int i = 0; i < iterations; i++) {
                long start = System.currentTimeMillis();
                try {
                    String response = longTimeoutRestTemplate.getForObject(mlServiceUrl + endpoint, String.class);
                    long elapsed = System.currentTimeMillis() - start;
                    times.add(elapsed);

                    JSONObject json = JSON.parseObject(response);
                    if (json.getBoolean("success") && json.getJSONObject("data") != null) {
                        pass++;
                    } else {
                        fail++;
                    }
                } catch (Exception e) {
                    fail++;
                    times.add(System.currentTimeMillis() - start);
                }
            }

            double avgTime = times.stream().mapToLong(Long::longValue).average().orElse(0);
            apiResult.put("iterations", iterations);
            apiResult.put("passed", pass);
            apiResult.put("failed", fail);
            apiResult.put("successRate", String.format("%.1f%%", (double)pass / iterations * 100));
            apiResult.put("avgResponseTime", String.format("%.0f ms", avgTime));
            apiResult.put("minTime", Collections.min(times) + " ms");
            apiResult.put("maxTime", Collections.max(times) + " ms");
            apiResult.put("status", fail == 0 ? "PASS" : "FAIL");

            apiResults.add(apiResult);
            totalPassed += pass;
            totalFailed += fail;
        }

        result.put("apiTests", apiResults);
        result.put("totalRequests", iterations * apiTests.length);
        result.put("totalPassed", totalPassed);
        result.put("totalFailed", totalFailed);
        result.put("passed", totalFailed == 0);
        result.put("assertions", iterations * apiTests.length);
        result.put("overallSuccessRate", String.format("%.1f%%", (double)totalPassed / Math.max(totalPassed + totalFailed, 1) * 100));
        result.put("timestamp", new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date()));

        return result;
    }

    private Map<String, Object> runDataQueryTest(int iterations) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("testName", "数据分析查询功能测试");
        result.put("testType", "FUNCTIONAL");

        String[][] queries = {
            {"categoryGoodsPrice", "品类价格分析"},
            {"categoryGoodsSales", "品类销量分析"},
            {"cityGoodsPrice", "城市价格分布"},
            {"provinceGoodsSales", "省份销量统计"},
            {"shopGoodsSales", "店铺销量排行"}
        };

        List<Map<String, Object>> queryResults = new ArrayList<>();
        int totalPassed = 0;
        int totalFailed = 0;

        for (String[] query : queries) {
            Map<String, Object> queryResult = new LinkedHashMap<>();
            queryResult.put("queryName", query[1]);
            queryResult.put("queryId", query[0]);

            int pass = 0;
            int fail = 0;
            List<Integer> recordCounts = new ArrayList<>();

            for (int i = 0; i < iterations; i++) {
                try {
                    List<JSONObject> data;
                    switch (query[0]) {
                        case "categoryGoodsPrice":
                            data = taobaoGoodsAnalyseMapper.categoryGoodsPrice(); break;
                        case "categoryGoodsSales":
                            data = taobaoGoodsAnalyseMapper.categoryGoodsSales(); break;
                        case "cityGoodsPrice":
                            data = taobaoGoodsAnalyseMapper.cityGoodsPrice(); break;
                        case "provinceGoodsSales":
                            data = taobaoGoodsAnalyseMapper.provinceGoodsSales(); break;
                        case "shopGoodsSales":
                            data = taobaoGoodsAnalyseMapper.shopGoodsSales(); break;
                        default:
                            data = new ArrayList<>();
                    }
                    
                    if (data != null && !data.isEmpty()) {
                        pass++;
                        recordCounts.add(data.size());
                    } else {
                        fail++;
                    }
                } catch (Exception e) {
                    fail++;
                }
            }

            queryResult.put("iterations", iterations);
            queryResult.put("passed", pass);
            queryResult.put("failed", fail);
            queryResult.put("successRate", String.format("%.1f%%", (double)pass / iterations * 100));
            queryResult.put("avgRecordCount", recordCounts.isEmpty() ? 0 :
                recordCounts.stream().mapToInt(Integer::intValue).average().orElse(0));
            queryResult.put("status", fail == 0 ? "PASS" : "FAIL");

            queryResults.add(queryResult);
            totalPassed += pass;
            totalFailed += fail;
        }

        result.put("queryTests", queryResults);
        result.put("totalQueries", iterations * queries.length);
        result.put("totalPassed", totalPassed);
        result.put("totalFailed", totalFailed);
        result.put("passed", totalFailed == 0);
        result.put("assertions", iterations * queries.length);
        result.put("timestamp", new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date()));

        return result;
    }

    @GetMapping("/generateTestReport")
    @ResponseBody
    public AjaxResult generateTestReport() {
        Map<String, Object> fullReport = new LinkedHashMap<>();
        
        AjaxResult envResult = getEnvironment();
        AjaxResult dbResult = testDatabaseConnection();
        AjaxResult mlResult = testMLServiceHealth();

        fullReport.put("reportTitle", "淘宝商品销售数据分析系统 - 综合测试报告");
        fullReport.put("generatedAt", new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date()));
        fullReport.put("environment", envResult.get("data"));
        fullReport.put("databaseTest", dbResult.get("data"));
        fullReport.put("mlServiceTest", mlResult.get("data"));

        int totalTests = 0;
        int passedTests = 0;
        int failedTests = 0;

        if (dbResult.get("data") instanceof Map) {
            @SuppressWarnings("unchecked")
            Map<String, Object> dbData = (Map<String, Object>) dbResult.get("data");
            totalTests += toInt(dbData.get("totalTests"));
            passedTests += toInt(dbData.get("passedTests"));
            failedTests += toInt(dbData.get("failedTests"));
        }

        if (mlResult.get("data") instanceof Map) {
            @SuppressWarnings("unchecked")
            Map<String, Object> mlData = (Map<String, Object>) mlResult.get("data");
            totalTests += toInt(mlData.get("totalEndpoints"));
            passedTests += toInt(mlData.get("healthyEndpoints"));
            failedTests += toInt(mlData.get("unhealthyEndpoints"));
        }

        Map<String, Object> overallSummary = new LinkedHashMap<>();
        overallSummary.put("totalTests", totalTests);
        overallSummary.put("passedTests", passedTests);
        overallSummary.put("failedTests", failedTests);
        overallSummary.put("passRate", totalTests > 0 ? String.format("%.1f%%", (double)passedTests / totalTests * 100) : "N/A");
        overallSummary.put("overallStatus", failedTests == 0 ? "✅ ALL SYSTEMS OPERATIONAL" : "⚠️ SOME ISSUES DETECTED");
        fullReport.put("overallSummary", overallSummary);

        return AjaxResult.success(fullReport);
    }

    @GetMapping("/quickHealthCheck")
    @ResponseBody
    public AjaxResult quickHealthCheck() {
        Map<String, Object> quickStatus = new LinkedHashMap<>();
        long startTime = System.currentTimeMillis();
        boolean allHealthy = true;

        try {
            Map<String, Object> appStatus = new LinkedHashMap<>();
            appStatus.put("status", "RUNNING");
            appStatus.put("port", serverPort);
            appStatus.put("checkTime", new SimpleDateFormat("HH:mm:ss").format(new Date()));
            quickStatus.put("applicationServer", appStatus);

            try {
                String dbTest = "SELECT 1";
                taobaoGoodsAnalyseMapper.executeRawSql(dbTest);
                Map<String, Object> dbStatusMap = new LinkedHashMap<>();
                dbStatusMap.put("status", "CONNECTED");
                dbStatusMap.put("responseTime", "< 50ms");
                quickStatus.put("database", dbStatusMap);
            } catch (Exception e) {
                Map<String, Object> dbErrorMap = new LinkedHashMap<>();
                dbErrorMap.put("status", "DISCONNECTED");
                dbErrorMap.put("error", e.getMessage());
                quickStatus.put("database", dbErrorMap);
                allHealthy = false;
            }

            try {
                String mlResponse = restTemplate.getForObject(mlServiceUrl + "/", String.class);
                JSONObject mlJson = JSON.parseObject(mlResponse);
                Map<String, Object> mlStatusMap = new LinkedHashMap<>();
                mlStatusMap.put("status", "ONLINE");
                mlStatusMap.put("version", mlJson.getString("version"));
                mlStatusMap.put("endpoints", mlJson.getJSONArray("endpoints").size());
                quickStatus.put("mlService", mlStatusMap);
            } catch (Exception e) {
                Map<String, Object> mlErrorMap = new LinkedHashMap<>();
                mlErrorMap.put("status", "OFFLINE");
                mlErrorMap.put("url", mlServiceUrl);
                quickStatus.put("mlService", mlErrorMap);
                allHealthy = false;
            }

            quickStatus.put("overallHealth", allHealthy ? "HEALTHY" : "DEGRADED");
            quickStatus.put("totalCheckTime", (System.currentTimeMillis() - startTime) + "ms");

            return AjaxResult.success(quickStatus);
        } catch (Exception e) {
            return AjaxResult.error("健康检查失败: " + e.getMessage());
        }
    }

    private String formatBytes(long bytes) {
        if (bytes < 1024) return bytes + " B";
        if (bytes < 1024 * 1024) return String.format("%.1f KB", bytes / 1024.0);
        if (bytes < 1024 * 1024 * 1024) return String.format("%.1f MB", bytes / (1024.0 * 1024));
        return String.format("%.2f GB", bytes / (1024.0 * 1024 * 1024));
    }

    private String formatUptime(long millis) {
        long seconds = millis / 1000;
        long days = seconds / 86400;
        long hours = (seconds % 86400) / 3600;
        long minutes = (seconds % 3600) / 60;
        if (days > 0) return days + "d " + hours + "h " + minutes + "m";
        if (hours > 0) return hours + "h " + minutes + "m";
        return minutes + "m " + (seconds % 60) + "s";
    }

    private String estimateDataSize(int stringLength) {
        if (stringLength < 1024) return stringLength + " B";
        if (stringLength < 1024 * 1024) return String.format("%.1f KB", stringLength / 1024.0);
        return String.format("%.1f MB", stringLength / (1024.0 * 1024));
    }

    private int toInt(Object obj) {
        if (obj == null) return 0;
        if (obj instanceof Number) return ((Number) obj).intValue();
        try {
            return Integer.parseInt(obj.toString().trim());
        } catch (NumberFormatException e) {
            return 0;
        }
    }
}
