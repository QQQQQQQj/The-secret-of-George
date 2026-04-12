drop table if exists project.ods_taobao_goods_sales;
CREATE TABLE project.ods_taobao_goods_sales
(
    type       STRING COMMENT '产品类型 (如：笔记本电脑)',
    title      STRING COMMENT '商品标题 (产品详细描述)',
    price      STRING COMMENT '价格 (单位：元)',
    deal       STRING COMMENT '成交量 (销量)',
    img_src    STRING COMMENT '商品图片地址',
    name       STRING COMMENT '店铺名称',
    address    STRING COMMENT '店铺所在地址 (省市)',
    isPostFree STRING COMMENT '是否包邮 (包邮/不包邮)',
    href       STRING COMMENT '商品详情页链接',
    name_href  STRING COMMENT '店铺详情页链接'
)
    ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
        WITH SERDEPROPERTIES (
        "separatorChar" = ",",
        "quoteChar" = "\"",
        "escapeChar" = "\\"
        )
    STORED AS INPUTFORMAT
        'org.apache.hadoop.mapred.TextInputFormat'
        OUTPUTFORMAT
            'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
    tblproperties ("skip.header.line.count" = "1","comment" = "淘宝商品销售数据")
;
load data inpath '/project/taobaoGoods/taobaoGoods.csv' into table project.ods_taobao_goods_sales;

DROP TABLE IF EXISTS project.dwd_taobao_goods_sales;
CREATE TABLE project.dwd_taobao_goods_sales
    stored as ORC AS
select type,
       title,
       cast(price as decimal(10, 2))                                                                        as price,
       cast(deal as bigint)                                                                                 as deal,
       img_src,
       name,
       regexp_replace(IF(instr(address, ' ') > 0, split(address, ' ')[0], address), '省|市|壮族自治区', '') as province,
       regexp_replace(IF(instr(address, ' ') > 0, split(address, ' ')[1], address), '省|市|壮族自治区', '') as city,
       isPostFree,
       IF(href like 'http:%', href, concat('http:', href))                                                  as href,
       IF(name_href like 'http:%', name_href, concat('http:', name_href))                                   as name_href
from project.ods_taobao_goods_sales
where type <> 'type'
  and title is not null;


-- 每个省的商品销量
DROP TABLE IF EXISTS project.ads_taobao_province_goods_sales;
CREATE TABLE project.ads_taobao_province_goods_sales
    stored as ORC AS
select province,
       sum(deal) as total_sales
from project.dwd_taobao_goods_sales
group by province
order by total_sales desc;

-- 城市的商品销量排名
DROP TABLE IF EXISTS project.ads_taobao_city_goods_sales;
CREATE TABLE project.ads_taobao_city_goods_sales
    stored as ORC AS
select city,
       sum(deal) as total_sales
from project.dwd_taobao_goods_sales
group by city
order by total_sales desc
limit 50;

-- 店铺的销量排名
DROP TABLE IF EXISTS project.ads_taobao_shop_goods_sales;
CREATE TABLE project.ads_taobao_shop_goods_sales
    stored as ORC AS
select name      as shop_name,
       sum(deal) as total_sales
from project.dwd_taobao_goods_sales
group by name
order by total_sales desc
limit 50;

-- 每种商品的销量
DROP TABLE IF EXISTS project.ads_taobao_category_goods_sales;
CREATE TABLE project.ads_taobao_category_goods_sales
    stored as ORC AS
select type      as goods_category,
       sum(deal) as total_sales
from project.dwd_taobao_goods_sales
group by type;

-- 每种商品的均价分析
DROP TABLE IF EXISTS project.ads_taobao_category_goods_price;
CREATE TABLE project.ads_taobao_category_goods_price
    stored as ORC AS
select type                 as goods_category,
       round(avg(price), 2) as avg_price
from project.dwd_taobao_goods_sales
group by type;

-- 每个城市的商品均价分析
DROP TABLE IF EXISTS project.ads_taobao_city_goods_price;
CREATE TABLE project.ads_taobao_city_goods_price
    stored as ORC AS
select city,
       avg_price
from (select city,
             round(avg(price), 2) as avg_price,
             count(*) as cnt
      from project.dwd_taobao_goods_sales
      group by city) as tt
where cnt >= 10
order by avg_price desc
limit 50;
