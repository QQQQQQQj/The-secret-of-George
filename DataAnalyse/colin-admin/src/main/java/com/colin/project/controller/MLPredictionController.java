package com.colin.project.controller;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import com.colin.common.core.controller.BaseController;
import com.colin.common.core.domain.AjaxResult;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.client.SimpleClientHttpRequestFactory;

import java.util.HashMap;
import java.util.Map;

@Controller
@RequestMapping("/project/mlPrediction")
public class MLPredictionController extends BaseController {

    private String prefix = "project/mlPrediction";

    @Value("${ml.service.url:http://localhost:6003}")
    private String mlServiceUrl;

    private RestTemplate restTemplate;
    public MLPredictionController() {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(5000);
        factory.setReadTimeout(15000);
        this.restTemplate = new RestTemplate(factory);
    }

    @GetMapping()
    public String mlPrediction() {
        return prefix + "/mlPrediction";
    }

    @GetMapping("/salesForecast")
    @ResponseBody
    public AjaxResult salesForecast(@RequestParam(defaultValue = "30") Integer days) {
        try {
            String url = mlServiceUrl + "/api/predict/sales-forecast?days=" + days;
            String response = restTemplate.getForObject(url, String.class);
            JSONObject result = JSON.parseObject(response);
            if (result.getBoolean("success")) {
                return AjaxResult.success(result.getJSONObject("data"));
            }
            return AjaxResult.error(result.getString("message"));
        } catch (Exception e) {
            return AjaxResult.error("ML服务连接失败: " + e.getMessage() + "，请确保Python ML服务已启动(端口6003)");
        }
    }

    @GetMapping("/amountForecast")
    @ResponseBody
    public AjaxResult amountForecast(@RequestParam(defaultValue = "30") Integer days) {
        try {
            String url = mlServiceUrl + "/api/predict/amount-forecast?days=" + days;
            String response = restTemplate.getForObject(url, String.class);
            JSONObject result = JSON.parseObject(response);
            if (result.getBoolean("success")) {
                return AjaxResult.success(result.getJSONObject("data"));
            }
            return AjaxResult.error(result.getString("message"));
        } catch (Exception e) {
            return AjaxResult.error("ML服务连接失败: " + e.getMessage());
        }
    }

    @GetMapping("/priceElasticity")
    @ResponseBody
    public AjaxResult priceElasticity() {
        try {
            String url = mlServiceUrl + "/api/predict/price-elasticity";
            String response = restTemplate.getForObject(url, String.class);
            JSONObject result = JSON.parseObject(response);
            if (result.getBoolean("success")) {
                return AjaxResult.success(result.getJSONObject("data"));
            }
            return AjaxResult.error(result.getString("message"));
        } catch (Exception e) {
            return AjaxResult.error("ML服务连接失败: " + e.getMessage());
        }
    }

    @GetMapping("/categoryPrice")
    @ResponseBody
    public AjaxResult categoryPrice() {
        try {
            String url = mlServiceUrl + "/api/predict/category-price";
            String response = restTemplate.getForObject(url, String.class);
            JSONObject result = JSON.parseObject(response);
            if (result.getBoolean("success")) {
                return AjaxResult.success(result.getJSONObject("data"));
            }
            return AjaxResult.error(result.getString("message"));
        } catch (Exception e) {
            return AjaxResult.error("ML服务连接失败: " + e.getMessage());
        }
    }

    @GetMapping("/shopGmv")
    @ResponseBody
    public AjaxResult shopGmv() {
        try {
            String url = mlServiceUrl + "/api/predict/shop-gmv";
            String response = restTemplate.getForObject(url, String.class);
            JSONObject result = JSON.parseObject(response);
            if (result.getBoolean("success")) {
                return AjaxResult.success(result.getJSONObject("data"));
            }
            return AjaxResult.error(result.getString("message"));
        } catch (Exception e) {
            return AjaxResult.error("ML服务连接失败: " + e.getMessage());
        }
    }

    @GetMapping("/cityGmv")
    @ResponseBody
    public AjaxResult cityGmv() {
        try {
            String url = mlServiceUrl + "/api/predict/city-gmv";
            String response = restTemplate.getForObject(url, String.class);
            JSONObject result = JSON.parseObject(response);
            if (result.getBoolean("success")) {
                return AjaxResult.success(result.getJSONObject("data"));
            }
            return AjaxResult.error(result.getString("message"));
        } catch (Exception e) {
            return AjaxResult.error("ML服务连接失败: " + e.getMessage());
        }
    }

    @GetMapping("/productHeat")
    @ResponseBody
    public AjaxResult productHeat() {
        try {
            String url = mlServiceUrl + "/api/predict/product-heat";
            String response = restTemplate.getForObject(url, String.class);
            JSONObject result = JSON.parseObject(response);
            if (result.getBoolean("success")) {
                return AjaxResult.success(result.getJSONObject("data"));
            }
            return AjaxResult.error(result.getString("message"));
        } catch (Exception e) {
            return AjaxResult.error("ML服务连接失败: " + e.getMessage());
        }
    }

    @GetMapping("/provinceSales")
    @ResponseBody
    public AjaxResult provinceSales() {
        try {
            String url = mlServiceUrl + "/api/predict/province-sales";
            String response = restTemplate.getForObject(url, String.class);
            JSONObject result = JSON.parseObject(response);
            if (result.getBoolean("success")) {
                return AjaxResult.success(result.getJSONObject("data"));
            }
            return AjaxResult.error(result.getString("message"));
        } catch (Exception e) {
            return AjaxResult.error("ML服务连接失败: " + e.getMessage());
        }
    }

    @GetMapping("/citySales")
    @ResponseBody
    public AjaxResult citySales() {
        try {
            String url = mlServiceUrl + "/api/predict/city-sales";
            String response = restTemplate.getForObject(url, String.class);
            JSONObject result = JSON.parseObject(response);
            if (result.getBoolean("success")) {
                return AjaxResult.success(result.getJSONObject("data"));
            }
            return AjaxResult.error(result.getString("message"));
        } catch (Exception e) {
            return AjaxResult.error("ML服务连接失败: " + e.getMessage());
        }
    }

    @GetMapping("/categoryTrend")
    @ResponseBody
    public AjaxResult categoryTrend(@RequestParam(defaultValue = "12") Integer futurePeriods) {
        try {
            String url = mlServiceUrl + "/api/predict/category-trend?future_periods=" + futurePeriods;
            String response = restTemplate.getForObject(url, String.class);
            JSONObject result = JSON.parseObject(response);
            if (result.getBoolean("success")) {
                return AjaxResult.success(result.getJSONObject("data"));
            }
            return AjaxResult.error(result.getString("message"));
        } catch (Exception e) {
            return AjaxResult.error("ML服务连接失败: " + e.getMessage());
        }
    }

    @GetMapping("/runAll")
    @ResponseBody
    public AjaxResult runAllPredictions(@RequestParam(defaultValue = "30") Integer salesDays) {
        try {
            String url = mlServiceUrl + "/api/predict/all?sales_days=" + salesDays;
            String response = restTemplate.getForObject(url, String.class);
            JSONObject result = JSON.parseObject(response);
            if (result.getBoolean("success")) {
                return AjaxResult.success(result.getJSONObject("data"));
            }
            return AjaxResult.error(result.getString("message"));
        } catch (Exception e) {
            return AjaxResult.error("ML服务连接失败: " + e.getMessage());
        }
    }

    @GetMapping("/serviceStatus")
    @ResponseBody
    public AjaxResult checkServiceStatus() {
        try {
            String url = mlServiceUrl + "/";
            String response = restTemplate.getForObject(url, String.class);
            JSONObject result = JSON.parseObject(response);
            return AjaxResult.success("ML服务运行正常", result);
        } catch (Exception e) {
            Map<String, Object> status = new HashMap<>();
            status.put("status", "offline");
            status.put("message", "ML服务未启动");
            status.put("url", mlServiceUrl);
            return AjaxResult.success(status);
        }
    }
}
