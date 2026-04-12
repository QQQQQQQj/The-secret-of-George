# 🤖 机器学习预测系统 - 启动指南

## 系统架构

```
前端 (ECharts大屏) :6002
       ↓
Java Spring Boot :6002 (MLPredictionController)
       ↓ HTTP
Python FastAPI ML服务 :6003 (6个ML模型)
       ↓
MySQL :3306 (shangpinfenxistr)
```

## 快速启动步骤

### 第1步：安装Python依赖

```bash
cd ml_service
pip install -r requirements.txt
```

### 第2步：初始化预测结果表（可选）

```bash
mysql -u root -proot shangpinfenxistr < sql/ml_prediction_tables.sql
```

### 第3步：启动Python ML服务（端口6003）

```bash
cd ml_service
python main.py
```

启动成功后会看到：
```
============================================================
🚀 淘宝商品销售数据 ML 预测服务启动中...
   服务地址: http://localhost:6003
   API文档: http://localhost:6003/docs
============================================================
```

### 第4步：启动Java后端服务（端口6002）

在IDEA中启动 `DataAnalyseApplication.java`，或：
```bash
# 在DataAnalyse项目根目录
mvn spring-boot:run -pl colin-admin
```

### 第5步：访问预测页面

浏览器打开：`http://localhost:6002/project/mlPrediction`

## API接口一览

| 接口 | 功能 | 方法 |
|------|------|------|
| `/api/predict/sales-forecast` | 时序销量预测 | GET |
| `/api/predict/amount-forecast` | 时序销售额预测 | GET |
| `/api/predict/price-elasticity` | 价格弹性分析 | GET |
| `/api/predict/category-price` | 品类价格分析 | GET |
| `/api/predict/shop-gmv` | 店铺GMV预测 | GET |
| `/api/predict/city-gmv` | 城市GMV排名 | GET |
| `/api/predict/product-heat` | 商品热度预测 | GET |
| `/api/predict/province-sales` | 省份销量预测 | GET |
| `/api/predict/city-sales` | 城市销量分布 | GET |
| `/api/predict/category-trend` | 品类趋势预测 | GET |
| `/api/predict/all` | 一键全部预测 | GET |

## 6大ML模型说明

### 1. 📈 时序销量预测 (Prophet)
- **算法**: Facebook Prophet 时间序列模型
- **输入**: 每日销售额&销量数据 (ads_taobao_beauty_makeup_daily_amt_cnt)
- **输出**: 未来N天的销量/销售额预测 + 95%置信区间 + 趋势方向
- **评估指标**: MAPE, RMSE, R²

### 2. 💰 价格-销量弹性模型 (多项式回归+Ridge)
- **算法**: 多项式特征 + Ridge回归
- **输入**: 各价格区间的销量/销售额数据
- **输出**: 弹性系数、最优定价建议、价格策略
- **应用场景**: 定价决策、促销力度制定

### 3. 🏪 店铺GMV预测 (GradientBoosting)
- **算法**: Gradient Boosting Regressor
- **输入**: 店铺的销售额、销量、评论数、客单价等特征
- **输出**: GMV预测值、潜力评分(0-100)、运营建议
- **特征重要性**: 自动识别核心驱动因素

### 4. 🔥 商品热度预测 (Random Forest)
- **算法**: Random Forest Regressor + 文本特征提取
- **输入**: 商品标题、销量、评论数
- **输出**: 热度评分、热度等级(爆款/热门/上升/一般/冷门)、优化建议
- **特征工程**: 品牌识别、关键词匹配、促销标签检测

### 5. 🗺️ 地区销量预测 (KMeans聚类+GBDT)
- **算法**: K-Means聚类 + Gradient Boosting
- **输入**: 省份/城市销量、包邮率、地理区域
- **输出**: 聚类分组(潜力/成熟/成长/待开发)、潜力指数、区域策略
- **帕累托分析**: 城市销量集中度分析

### 6. 📊 品类趋势预测 (趋势外推+属性建模)
- **算法**: 基于品类属性的复合增长模型
- **输入**: 7大品类的当前市场份额、平均价格
- **输出**: 未来12个月份额变化、增长潜力评分、组合优化建议
- **维度分析**: 必需性、购买频率、季节性、价格敏感度

## 文件结构

```
ml_service/
├── main.py                      # FastAPI主应用入口
├── db_config.py                 # 数据库连接配置
├── requirements.txt             # Python依赖
├── sql/
│   └── ml_prediction_tables.sql # MySQL预测表DDL
└── models/
    ├── __init__.py              # 模块导出
    ├── time_series_predictor.py # 模型1: 时序预测
    ├── price_elasticity_model.py# 模型2: 价格弹性
    ├── shop_gmv_predictor.py    # 模型3: GMV预测
    ├── product_heat_predictor.py# 模型4: 热度预测
    ├── region_sales_predictor.py# 模型5: 地区预测
    └── category_trend_predictor.py # 模型6: 品类趋势

DataAnalyse/colin-admin/src/main/java/com/colin/project/controller/
└── MLPredictionController.java  # Java后端API控制器

DataAnalyse/colin-admin/src/main/resources/templates/project/mlPrediction/
└── mlPrediction.html            # 前端可视化大屏
```
