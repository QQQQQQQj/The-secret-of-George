# -*- coding: utf-8 -*-
"""
淘宝商品销售数据分析系统 - 自动化测试套件
功能: API接口测试 | 数据库连接验证 | ML服务健康检查 | 性能基准测试
生成详细测试报告 (HTML/JSON格式)
"""

import sys
import os
import json
import time
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

if sys.platform == 'win32':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class TestResult:
    def __init__(self, test_name, test_type):
        self.test_name = test_name
        self.test_type = test_type
        self.start_time = time.time()
        self.end_time = None
        self.passed = False
        self.error = None
        self.details = {}
        self.response_time = 0
        
    def finish(self, passed, error=None, details=None):
        self.end_time = time.time()
        self.response_time = (self.end_time - self.start_time) * 1000
        self.passed = passed
        self.error = error
        self.details = details or {}
        
    def to_dict(self):
        return {
            'testName': self.test_name,
            'testType': self.test_type,
            'passed': self.passed,
            'responseTime': round(self.response_time, 2),
            'error': self.error,
            'details': self.details,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        }

class AutomatedTestSuite:
    def __init__(self):
        self.base_url = "http://localhost:6002"
        self.ml_url = "http://localhost:6003"
        self.results = []
        self.session = requests.Session()
        self.session.timeout = 30
        
    def log(self, message, level='INFO'):
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        colors = {'INFO': Colors.BLUE, 'SUCCESS': Colors.GREEN, 'ERROR': Colors.RED, 'WARN': Colors.YELLOW}
        color = colors.get(level, Colors.RESET)
        print(f"{color}[{timestamp}] [{level}]{Colors.RESET} {message}")
        
    def test_application_server(self):
        """测试应用服务器连通性"""
        result = TestResult("应用服务器连通性", "CONNECTIVITY")
        try:
            resp = self.session.get(f"{self.base_url}/login")
            if resp.status_code in [200, 302]:
                result.finish(True, details={'statusCode': resp.status_code, 'server': 'Spring Boot'})
                self.log(f"✓ 应用服务器正常 - 状态码: {resp.status_code}", 'SUCCESS')
            else:
                result.finish(False, error=f"异常状态码: {resp.status_code}")
                self.log(f"✗ 应用服务器异常 - 状态码: {resp.status_code}", 'ERROR')
        except Exception as e:
            result.finish(False, error=str(e))
            self.log(f"✗ 应用服务器无法连接 - {e}", 'ERROR')
        self.results.append(result)
        return result

    def test_ml_service_root(self):
        """测试ML服务根路径"""
        result = TestResult("ML服务根路径检测", "ML_SERVICE")
        try:
            resp = self.session.get(f"{self.ml_url}/", timeout=10)
            data = resp.json()
            if data.get('status') == 'running':
                result.finish(True, details={
                    'version': data.get('version'),
                    'endpoints_count': len(data.get('endpoints', []))
                })
                self.log(f"✓ ML服务在线 - 版本: {data.get('version')}, 端点数: {len(data.get('endpoints', []))}", 'SUCCESS')
            else:
                result.finish(False, error="服务状态异常")
                self.log("✗ ML服务状态异常", 'ERROR')
        except Exception as e:
            result.finish(False, error=str(e))
            self.log(f"✗ ML服务离线 - {e}", 'ERROR')
        self.results.append(result)
        return result

    def test_sales_forecast_api(self):
        """测试时序销量预测API"""
        result = TestResult("时序销量预测API (/sales-forecast)", "ML_API")
        try:
            start = time.time()
            resp = self.session.get(f"{self.ml_url}/api/predict/sales-forecast?days=7", timeout=60)
            elapsed = (time.time() - start) * 1000
            data = resp.json()
            
            if data.get('success') and data.get('data'):
                pred_data = data['data']
                has_history = len(pred_data.get('history', [])) > 0
                has_prediction = len(pred_data.get('prediction', [])) > 0
                
                result.finish(has_history and has_prediction, 
                    error="数据结构不完整" if not (has_history and has_prediction) else None,
                    details={
                        'executionTime': data.get('execution_time', 0),
                        'historyCount': len(pred_data.get('history', [])),
                        'predictionCount': len(pred_data.get('prediction', [])),
                        'mape': pred_data.get('model_accuracy', {}).get('mape'),
                        'responseTimeMs': round(elapsed, 2)
                    })
                
                if result.passed:
                    self.log(f"✓ 销量预测API正常 - 历史:{len(pred_data.get('history',[]))}条, 预测:{len(pred_data.get('prediction',[]))}天, 耗时:{elapsed:.0f}ms", 'SUCCESS')
                else:
                    self.log("⚠ 销量预测API返回数据不完整", 'WARN')
            else:
                result.finish(False, error=data.get('message', '未知错误'))
                self.log(f"✗ 销量预测API失败 - {data.get('message')}", 'ERROR')
        except Exception as e:
            result.finish(False, error=str(e))
            self.log(f"✗ 销量预测API异常 - {e}", 'ERROR')
        self.results.append(result)
        return result

    def test_price_elasticity_api(self):
        """测试价格弹性分析API"""
        result = TestResult("价格弹性分析API (/price-elasticity)", "ML_API")
        try:
            resp = self.session.get(f"{self.ml_url}/api/predict/price-elasticity", timeout=60)
            data = resp.json()
            
            if data.get('success') and data.get('data'):
                elastic_data = data['data']
                has_coefficients = len(elastic_data.get('elasticity_coefficients', [])) > 0
                
                result.finish(has_coefficients,
                    error="缺少弹性系数数据",
                    details={
                        'coefficientCount': len(elastic_data.get('elasticity_coefficients', [])),
                        'categoriesTested': elastic_data.get('categories_tested', 0),
                        'executionTime': data.get('execution_time', 0)
                    })
                
                status = "SUCCESS" if result.passed else "WARN"
                self.log(f"✓ 价格弹性API正常 - 类别数:{elastic_data.get('categories_tested',0)}", status.lower())
            else:
                result.finish(False, error=data.get('message'))
                self.log(f"✗ 价格弹性API失败 - {data.get('message')}", 'ERROR')
        except Exception as e:
            result.finish(False, error=str(e))
            self.log(f"✗ 价格弹性API异常 - {e}", 'ERROR')
        self.results.append(result)
        return result

    def test_shop_gmv_api(self):
        """测试店铺GMV预测API"""
        result = TestResult("店铺GMV预测API (/shop-gmv)", "ML_API")
        try:
            resp = self.session.get(f"{self.ml_url}/api/predict/shop-gmv", timeout=60)
            data = resp.json()
            
            if data.get('success') and data.get('data'):
                gmv_data = data['data']
                shops = gmv_data.get('shop_predictions', [])
                
                result.finish(len(shops) > 0,
                    error="无店铺数据",
                    details={
                        'shopCount': len(shops),
                        'topGmv': shops[0].get('predicted_gmv', 0) if shops else 0,
                        'modelType': gmv_data.get('model_type', 'Unknown')
                    })
                
                self.log(f"✓ GMV预测API正常 - 店铺数:{len(shops)}", "success" if result.passed else "warn")
            else:
                result.finish(False, error=data.get('message'))
                self.log(f"✗ GMV预测API失败", 'ERROR')
        except Exception as e:
            result.finish(False, error=str(e))
            self.log(f"✗ GMV预测API异常 - {e}", 'ERROR')
        self.results.append(result)
        return result

    def test_product_heat_api(self):
        """测试商品热度预测API"""
        result = TestResult("商品热度预测API (/product-heat)", "ML_API")
        try:
            resp = self.session.get(f"{self.ml_url}/api/predict/product-heat", timeout=60)
            data = resp.json()
            
            if data.get('success') and data.get('data'):
                heat_data = data['data']
                products = heat_data.get('product_heat_scores', [])
                
                result.finish(len(products) > 0,
                    error="无商品热度数据",
                    details={
                        'productCount': len(products),
                        'topProduct': products[0].get('title', 'N/A')[:30] if products else 'N/A',
                        'topScore': products[0].get('heat_score', 0) if products else 0
                    })
                
                self.log(f"✓ 商品热度API正常 - 商品数:{len(products)}", "success" if result.passed else "warn")
            else:
                result.finish(False, error=data.get('message'))
                self.log(f"✗ 商品热度API失败", 'ERROR')
        except Exception as e:
            result.finish(False, error=str(e))
            self.log(f"✗ 商品热度API异常 - {e}", 'ERROR')
        self.results.append(result)
        return result

    def test_province_sales_api(self):
        """测试省份销量预测API"""
        result = TestResult("省份销量预测API (/province-sales)", "ML_API")
        try:
            resp = self.session.get(f"{self.ml_url}/api/predict/province-sales", timeout=60)
            data = resp.json()
            
            if data.get('success') and data.get('data'):
                province_data = data['data']
                provinces = province_data.get('province_predictions', [])
                clusters = province_data.get('cluster_info', {})
                
                result.finish(len(provinces) > 0,
                    error="无省份数据",
                    details={
                        'provinceCount': len(provinces),
                        'clusterCount': len(clusters.get('clusters', [])),
                        'algorithm': clusters.get('algorithm', 'KMeans')
                    })
                
                self.log(f"✓ 省份销量API正常 - 省份数:{len(provinces)}, 聚类数:{len(clusters.get('clusters',[]))}", 
                        "success" if result.passed else "warn")
            else:
                result.finish(False, error=data.get('message'))
                self.log(f"✗ 省份销量API失败", 'ERROR')
        except Exception as e:
            result.finish(False, error=str(e))
            self.log(f"✗ 省份销量API异常 - {e}", 'ERROR')
        self.results.append(result)
        return result

    def test_category_trend_api(self):
        """测试品类趋势预测API"""
        result = TestResult("品类趋势预测API (/category-trend)", "ML_API")
        try:
            resp = self.session.get(f"{self.ml_url}/api/predict/category-trend?future_periods=6", timeout=60)
            data = resp.json()
            
            if data.get('success') and data.get('data'):
                trend_data = data['data']
                categories = trend_data.get('category_trends', [])
                
                result.finish(len(categories) > 0,
                    error="无品类趋势数据",
                    details={
                        'categoryCount': len(categories),
                        'futurePeriods': trend_data.get('future_periods', 6)
                    })
                
                self.log(f"✓ 品类趋势API正常 - 品类数:{len(categories)}", "success" if result.passed else "warn")
            else:
                result.finish(False, error=data.get('message'))
                self.log(f"✗ 品类趋势API失败", 'ERROR')
        except Exception as e:
            result.finish(False, error=str(e))
            self.log(f"✗ 品类趋势API异常 - {e}", 'ERROR')
        self.results.append(result)
        return result

    def test_data_query_apis(self):
        """测试数据分析查询API（通过Spring Boot）"""
        apis = [
            ("/project/taobaoGoodsAnalyse/categoryGoodsPrice", "品类价格查询"),
            ("/project/taobaoGoodsAnalyse/categoryGoodsSales", "品类销量查询"),
            ("/project/taobaoGoodsAnalyse/provinceGoodsSales", "省份销量查询"),
            ("/project/taobaoGoodsAnalyse/shopGoodsSales", "店铺销量查询"),
            ("/project/taobaoGoodsAnalyse/cityGoodsPrice", "城市价格查询")
        ]
        
        query_results = []
        for endpoint, name in apis:
            result = TestResult(f"数据查询API ({name})", "DATA_QUERY")
            try:
                start = time.time()
                resp = self.session.get(f"{self.base_url}{endpoint}", timeout=15)
                elapsed = (time.time() - start) * 1000
                data = resp.json()
                
                if data.get('code') == 0 and data.get('data'):
                    records = data['data']
                    result.finish(len(records) > 0,
                        error="空结果集" if len(records) == 0 else None,
                        details={'recordCount': len(records), 'responseTimeMs': round(elapsed, 2)})
                    
                    status = "SUCCESS" if result.passed else "WARN"
                    self.log(f"  ✓ {name} - {len(records)}条记录 ({elapsed:.0f}ms)", status.lower())
                else:
                    result.finish(False, error=data.get('msg', '请求失败'))
                    self.log(f"  ✗ {name} - {data.get('msg', 'Error')}", 'ERROR')
            except Exception as e:
                result.finish(False, error=str(e))
                self.log(f"  ✗ {name} - {e}", 'ERROR')
            
            query_results.append(result)
            self.results.append(result)
        
        return query_results

    def run_performance_benchmark(self, iterations=5):
        """运行性能基准测试"""
        self.log("\n" + "="*60, 'INFO')
        self.log(f"🚀 开始性能基准测试 (迭代次数: {iterations})", 'INFO')
        self.log("="*60, 'INFO')
        
        perf_results = []
        
        endpoints = [
            ("ML API - 销量预测", f"{self.ml_url}/api/predict/sales-forecast?days=7"),
            ("ML API - 价格弹性", f"{self.ml_url}/api/predict/price-elasticity"),
            ("Data API - 品类价格", f"{self.base_url}/project/taobaoGoodsAnalyse/categoryGoodsPrice"),
            ("Data API - 省份销量", f"{self.base_url}/project/taobaoGoodsAnalyse/provinceGoodsSales"),
        ]
        
        for name, url in endpoints:
            result = TestResult(f"性能基准 - {name}", "PERFORMANCE")
            times = []
            successes = 0
            
            for i in range(iterations):
                try:
                    start = time.time()
                    resp = self.session.get(url, timeout=60)
                    elapsed = (time.time() - start) * 1000
                    times.append(elapsed)
                    
                    if resp.status_code == 200:
                        successes += 1
                except Exception as e:
                    times.append(0)
            
            if times:
                avg_time = statistics.mean(times)
                p95_idx = int(len(times) * 0.95)
                p99_idx = int(len(times) * 0.99)
                
                sorted_times = sorted(times)
                result.finish(successes >= iterations * 0.8,
                    details={
                        'iterations': iterations,
                        'successes': successes,
                        'avgResponseTimeMs': round(avg_time, 2),
                        'minResponseTimeMs': round(min(times), 2),
                        'maxResponseTimeMs': round(max(times), 2),
                        'p50ResponseTimeMs': round(sorted_times[len(sorted_times)//2], 2),
                        'p95ResponseTimeMs': round(sorted_times[min(p95_idx, len(sorted_times)-1)], 2),
                        'p99ResponseTimeMs': round(sorted_times[min(p99_idx, len(sorted_times)-1)], 2),
                        'throughput': round(iterations / (sum(times)/1000), 2) if sum(times) > 0 else 0
                    })
                
                self.log(f"  📊 {name}: 平均{avg_time:.0f}ms, P95:{sorted_times[min(p95_idx,len(sorted_times)-1)]:.0f}ms, "
                        f"成功率:{successes}/{iterations} ({successes/iterations*100:.0f}%)", 
                        'SUCCESS' if result.passed else 'WARN')
            
            perf_results.append(result)
            self.results.append(result)
        
        return perf_results

    def run_all_tests(self, include_perf=True, perf_iterations=3):
        """运行完整测试套件"""
        suite_start = time.time()
        
        print(f"\n{Colors.BOLD}{Colors.CYAN}")
        print("="*70)
        print("  淘宝商品销售数据分析系统 - 自动化测试套件")
        print(f"  测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        print(f"{Colors.RESET}\n")
        
        self.log("📍 测试环境配置:", 'INFO')
        self.log(f"   • 应用服务器: {self.base_url}", 'INFO')
        self.log(f"   • ML服务地址: {self.ml_url}", 'INFO')
        self.log(f"   • 性能测试迭代: {perf_iterations}次", 'INFO')
        
        print(f"\n{Colors.YELLOW}{'─'*70}{Colors.RESET}")
        self.log("Phase 1: 基础连通性测试", 'INFO')
        print(f"{Colors.YELLOW}{'─'*70}{Colors.RESET}\n")
        
        self.test_application_server()
        self.test_ml_service_root()
        
        print(f"\n{Colors.YELLOW}{'─'*70}{Colors.RESET}")
        self.log("Phase 2: ML预测API测试", 'INFO')
        print(f"{Colors.YELLOW}{'─'*70}{Colors.RESET}\n")
        
        self.test_sales_forecast_api()
        self.test_price_elasticity_api()
        self.test_shop_gmv_api()
        self.test_product_heat_api()
        self.test_province_sales_api()
        self.test_category_trend_api()
        
        print(f"\n{Colors.YELLOW}{'─'*70}{Colors.RESET}")
        self.log("Phase 3: 数据查询API测试", 'INFO')
        print(f"{Colors.YELLOW}{'─'*70}{Colors.RESET}\n")
        
        self.test_data_query_apis()
        
        if include_perf:
            self.run_performance_benchmark(perf_iterations)
        
        suite_end = time.time()
        total_time = suite_end - suite_start
        
        self.generate_summary_report(total_time)
        return self.results

    def generate_summary_report(self, total_time):
        """生成测试总结报告"""
        passed = sum(1 for r in self.results if r.passed)
        failed = len(self.results) - passed
        pass_rate = (passed / len(self.results) * 100) if self.results else 0
        
        avg_response = statistics.mean([r.response_time for r in self.results]) if self.results else 0
        
        report = {
            'reportTitle': '淘宝商品销售数据分析系统 - 自动化测试报告',
            'generatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'environment': {
                'applicationUrl': self.base_url,
                'mlServiceUrl': self.ml_url,
                'pythonVersion': sys.version.split()[0],
                'platform': sys.platform
            },
            'summary': {
                'totalTests': len(self.results),
                'passedTests': passed,
                'failedTests': failed,
                'passRate': f'{pass_rate:.1f}%',
                'totalExecutionTime': f'{total_time:.2f}s',
                'averageResponseTime': f'{avg_response:.2f}ms',
                'overallStatus': 'ALL_TESTS_PASSED' if failed == 0 else 'SOME_TESTS_FAILED'
            },
            'testResults': [r.to_dict() for r in self.results]
        }
        
        print(f"\n\n{Colors.BOLD}{Colors.CYAN}")
        print("="*70)
        print("  📊 测试执行总结")
        print("="*70)
        print(f"{Colors.RESET}")
        
        print(f"  {Colors.BOLD}总测试数:{Colors.RESET}     {len(self.results)}")
        print(f"  {Colors.GREEN}通过测试:{Colors.RESET}     {passed}")
        print(f"  {Colors.RED}失败测试:{Colors.RESET}     {failed}")
        print(f"  {Colors.CYAN}通过率:{Colors.RESET}       {pass_rate:.1f}%")
        print(f"  {Colors.YELLOW}总耗时:{Colors.RESET}       {total_time:.2f}s")
        print(f"  {Colors.BLUE}平均响应时间:{Colors.RESET}  {avg_response:.2f}ms")
        
        status_color = Colors.GREEN if failed == 0 else Colors.RED
        status_text = "✅ 所有测试通过" if failed == 0 else "⚠️ 部分测试失败"
        print(f"\n  {Colors.BOLD}{status_color}最终状态: {status_text}{Colors.RESET}")
        
        print(f"\n{Colors.CYAN}{'='*70}{Colors.RESET}\n")
        
        output_file = f'test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.log(f"\n📄 详细报告已保存: {output_file}", 'SUCCESS')
        
        return report

def main():
    parser = argparse.ArgumentParser(description='淘宝商品销售数据分析系统 - 自动化测试工具')
    parser.add_argument('--no-perf', action='store_true', help='跳过性能基准测试')
    parser.add_argument('--iterations', type=int, default=3, help='性能测试迭代次数 (默认: 3)')
    parser.add_argument('--output', type=str, default=None, help='输出报告文件名')
    
    try:
        import argparse
        args = parser.parse_args()
    except:
        args = type('Args', (), {'no_perf': False, 'iterations': 3, 'output': None})()
    
    suite = AutomatedTestSuite()
    
    try:
        suite.run_all_tests(
            include_perf=not args.no_perf,
            perf_iterations=args.iterations
        )
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠ 测试被用户中断{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ 测试套件执行异常: {e}{Colors.RESET}")

if __name__ == "__main__":
    main()
