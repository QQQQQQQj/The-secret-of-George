#淘宝商品销售明细数据导出
sqoop export --connect jdbc:mysql://192.168.3.225:3306/visual?serverTimezone=GMT%2B8 \
--username work \
--password 123456 \
--driver com.mysql.cj.jdbc.Driver \
--table t_taobao_goods_sales  -hcatalog-database project \
--hcatalog-table dwd_taobao_goods_sales;

#每个省的商品销量
sqoop export --connect jdbc:mysql://192.168.3.225:3306/visual?serverTimezone=GMT%2B8 \
--username work \
--password 123456 \
--driver com.mysql.cj.jdbc.Driver \
--table ads_taobao_province_goods_sales  -hcatalog-database project \
--hcatalog-table ads_taobao_province_goods_sales;

#城市的商品销量排名
sqoop export --connect jdbc:mysql://192.168.3.225:3306/visual?serverTimezone=GMT%2B8 \
--username work \
--password 123456 \
--driver com.mysql.cj.jdbc.Driver \
--table ads_taobao_city_goods_sales  -hcatalog-database project \
--hcatalog-table ads_taobao_city_goods_sales;

#店铺的销量排名
sqoop export --connect jdbc:mysql://192.168.3.225:3306/visual?serverTimezone=GMT%2B8 \
--username work \
--password 123456 \
--driver com.mysql.cj.jdbc.Driver \
--table ads_taobao_shop_goods_sales  -hcatalog-database project \
--hcatalog-table ads_taobao_shop_goods_sales;

#每种商品的销量
sqoop export --connect jdbc:mysql://192.168.3.225:3306/visual?serverTimezone=GMT%2B8 \
--username work \
--password 123456 \
--driver com.mysql.cj.jdbc.Driver \
--table ads_taobao_category_goods_sales  -hcatalog-database project \
--hcatalog-table ads_taobao_category_goods_sales;

#每种商品的均价分析
sqoop export --connect jdbc:mysql://192.168.3.225:3306/visual?serverTimezone=GMT%2B8 \
--username work \
--password 123456 \
--driver com.mysql.cj.jdbc.Driver \
--table ads_taobao_category_goods_price  -hcatalog-database project \
--hcatalog-table ads_taobao_category_goods_price;

#每个城市的商品均价分析
sqoop export --connect jdbc:mysql://192.168.3.225:3306/visual?serverTimezone=GMT%2B8 \
--username work \
--password 123456 \
--driver com.mysql.cj.jdbc.Driver \
--table ads_taobao_city_goods_price  -hcatalog-database project \
--hcatalog-table ads_taobao_city_goods_price;
