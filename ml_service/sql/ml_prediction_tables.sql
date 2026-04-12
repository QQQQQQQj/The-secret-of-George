-- ============================================
-- ML预测结果表 - 淘宝商品销售数据分析系统
-- 创建时间: 2026-04-12
-- 说明: 存储所有机器学习模型的预测结果
-- ============================================

USE `shangpinfenxistr`;

-- 1. 时序销量预测结果表
DROP TABLE IF EXISTS `ml_prediction_sales_forecast`;
CREATE TABLE `ml_prediction_sales_forecast` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `predict_date` date NOT NULL COMMENT '预测日期',
  `date_type` varchar(20) NOT NULL DEFAULT 'future' COMMENT '类型: history历史/future预测',
  `predicted_sales` decimal(18,2) DEFAULT NULL COMMENT '预测销量',
  `predicted_amount` decimal(18,2) DEFAULT NULL COMMENT '预测销售额',
  `lower_bound` decimal(18,2) DEFAULT NULL COMMENT '预测下界',
  `upper_bound` decimal(18,2) DEFAULT NULL COMMENT '预测上界',
  `actual_sales` bigint(20) DEFAULT NULL COMMENT '实际销量(历史数据)',
  `actual_amount` decimal(18,2) DEFAULT NULL COMMENT '实际销售额(历史数据)',
  `model_version` varchar(50) DEFAULT 'prophet_v1' COMMENT '模型版本',
  `mape` decimal(5,2) DEFAULT NULL COMMENT '平均绝对百分比误差',
  `r2_score` decimal(5,4) DEFAULT NULL COMMENT 'R平方值',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_predict_date` (`predict_date`),
  KEY `idx_date_type` (`date_type`)
) ENGINE=InnoDB COMMENT='时序销量/销售额预测结果';

-- 2. 价格弹性分析结果表
DROP TABLE IF EXISTS `ml_prediction_price_elasticity`;
CREATE TABLE `ml_prediction_price_elasticity` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `price_range` varchar(50) NOT NULL COMMENT '价格区间',
  `mid_price` decimal(10,2) NOT NULL COMMENT '中间价格',
  `actual_sales` bigint(20) DEFAULT NULL COMMENT '实际销量',
  `predicted_sales` decimal(18,2) DEFAULT NULL COMMENT '预测销量',
  `actual_amount` decimal(18,2) DEFAULT NULL COMMENT '实际销售额',
  `elasticity_coef` decimal(10,4) DEFAULT NULL COMMENT '价格弹性系数',
  `elasticity_type` varchar(50) DEFAULT NULL COMMENT '弹性类型: 富有弹性/缺乏弹性/单位弹性',
  `optimal_price` decimal(10,2) DEFAULT NULL COMMENT '建议最优价格',
  `pricing_suggestion` varchar(500) DEFAULT NULL COMMENT '定价建议',
  `model_r2` decimal(5,4) DEFAULT NULL,
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB COMMENT='价格弹性分析结果';

-- 3. 店铺GMV预测结果表
DROP TABLE IF EXISTS `ml_prediction_shop_gmv`;
CREATE TABLE `ml_prediction_shop_gmv` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `shop_name` varchar(200) NOT NULL COMMENT '店铺名称',
  `actual_gmv` decimal(18,2) NOT NULL COMMENT '实际GMV',
  `predicted_gmv` decimal(18,2) DEFAULT NULL COMMENT '预测GMV',
  `total_sales` bigint(20) DEFAULT NULL COMMENT '总销量',
  `total_comments` int(11) DEFAULT NULL COMMENT '总评论数',
  `avg_order_value` decimal(10,2) DEFAULT NULL COMMENT '平均订单价值',
  `growth_potential_pct` decimal(8,2) DEFAULT NULL COMMENT '增长潜力百分比',
  `potential_score` decimal(5,2) DEFAULT NULL COMMENT '潜力评分(0-100)',
  `potential_level` varchar(50) DEFAULT NULL COMMENT '潜力等级',
  `recommendation` varchar(500) DEFAULT NULL COMMENT '运营建议',
  `model_version` varchar(50) DEFAULT 'xgboost_v1',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_shop_name` (`shop_name`),
  KEY `idx_potential_score` (`potential_score`)
) ENGINE=InnoDB COMMENT='店铺GMV预测与潜力评估结果';

-- 4. 商品热度预测结果表
DROP TABLE IF EXISTS `ml_prediction_product_heat`;
CREATE TABLE `ml_prediction_product_heat` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `product_title` varchar(500) NOT NULL COMMENT '商品标题',
  `actual_sales` bigint(20) DEFAULT NULL COMMENT '实际销量',
  `actual_comments` int(11) DEFAULT NULL COMMENT '实际评论数',
  `predicted_comments` decimal(12,0) DEFAULT NULL COMMENT '预测评论数',
  `heat_score` decimal(5,2) DEFAULT NULL COMMENT '热度评分(0-100)',
  `heat_level` varchar(50) DEFAULT NULL COMMENT '热度等级: 爆款/热门/上升中/一般/冷门',
  `brand_score` int(11) DEFAULT 0 COMMENT '品牌得分',
  `keyword_count` int(11) DEFAULT 0 COMMENT '关键词数量',
  `has_promo` tinyint(1) DEFAULT 0 COMMENT '是否有促销标签',
  `optimization_suggestion` varchar(500) DEFAULT NULL COMMENT '优化建议',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_heat_score` (`heat_score`)
) ENGINE=InnoDB COMMENT='商品热度预测结果';

-- 5. 地区销量预测结果表
DROP TABLE IF EXISTS `ml_prediction_region_sales`;
CREATE TABLE `ml_prediction_region_sales` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `region_type` varchar(20) NOT NULL COMMENT '地区类型: province/city',
  `region_name` varchar(100) NOT NULL COMMENT '地区名称',
  `actual_sales` bigint(20) DEFAULT NULL COMMENT '实际销量',
  `predicted_sales` decimal(18,2) DEFAULT NULL COMMENT '预测销量',
  `market_share_pct` decimal(8,3) DEFAULT NULL COMMENT '市场份额%',
  `postfree_rate` decimal(5,2) DEFAULT NULL COMMENT '包邮率(省份)',
  `region_group` varchar(50) DEFAULT NULL COMMENT '所属区域: 华东/华南等',
  `cluster_id` int(11) DEFAULT NULL COMMENT '聚类分组ID',
  `cluster_label` varchar(50) DEFAULT NULL COMMENT '聚类标签',
  `potential_index` decimal(5,2) DEFAULT NULL COMMENT '潜力指数',
  `strategy` varchar(500) DEFAULT NULL COMMENT '策略建议',
  `city_rank` int(11) DEFAULT NULL COMMENT '城市排名',
  `cumulative_pct` decimal(8,2) DEFAULT NULL COMMENT '累计占比%(城市)',
  `tier` varchar(50) DEFAULT NULL COMMENT '城市级别',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_region_type_name` (`region_type`, `region_name`),
  KEY `idx_potential_index` (`potential_index`)
) ENGINE=InnoDB COMMENT='地区销量分布预测结果';

-- 6. 品类趋势预测结果表
DROP TABLE IF EXISTS `ml_prediction_category_trend`;
CREATE TABLE `ml_prediction_category_trend` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `category_name` varchar(100) NOT NULL COMMENT '品类名称',
  `current_market_share` decimal(8,2) DEFAULT NULL COMMENT '当前市场份额%',
  `future_market_share_12m` decimal(8,2) DEFAULT NULL COMMENT '未来12月预期份额%',
  `share_change_pct` decimal(8,2) DEFAULT NULL COMMENT '份额变化%',
  `current_total_sales` bigint(20) DEFAULT NULL COMMENT '当前总销量',
  `avg_price` decimal(10,2) DEFAULT NULL COMMENT '平均价格',
  `trend_direction` varchar(50) DEFAULT NULL COMMENT '趋势方向',
  `growth_potential_score` decimal(5,2) DEFAULT NULL COMMENT '增长潜力评分',
  `growth_potential_level` varchar(50) DEFAULT NULL COMMENT '潜力等级',
  `recommendation` varchar(500) DEFAULT NULL COMMENT '建议',
  `monthly_prediction_json` text DEFAULT NULL COMMENT '月度预测JSON数据',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_category` (`category_name`)
) ENGINE=InnoDB COMMENT='品类销量趋势预测结果';

-- 7. ML模型运行日志表
DROP TABLE IF EXISTS `ml_model_run_log`;
CREATE TABLE `ml_model_run_log` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `model_name` varchar(100) NOT NULL COMMENT '模型名称',
  `model_type` varchar(50) NOT NULL COMMENT '模型类型',
  `status` varchar(20) NOT NULL COMMENT '运行状态: success/failed/pending',
  `execution_time_sec` decimal(10,3) DEFAULT NULL COMMENT '执行耗时(秒)',
  `record_count` int(11) DEFAULT NULL COMMENT '处理记录数',
  `metrics_json` text DEFAULT NULL COMMENT '评估指标JSON',
  `error_message` text DEFAULT NULL COMMENT '错误信息',
  `run_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '运行时间',
  PRIMARY KEY (`id`),
  KEY `idx_model_name` (`model_name`),
  KEY `idx_run_time` (`run_time`)
) ENGINE=InnoDB COMMENT='ML模型运行日志';
