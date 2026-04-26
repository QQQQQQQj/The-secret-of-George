package com.colin.system.mapper.project;

import com.alibaba.fastjson.JSONObject;
import org.apache.ibatis.annotations.Param;

import java.util.List;

public interface TaobaoGoodsAnalyseMapper {
    List<JSONObject> categoryGoodsPrice();

    List<JSONObject> categoryGoodsSales();

    List<JSONObject> categoryShopGoodsPrice(@Param("goodsCategory") String goodsCategory);

    List<JSONObject> cityGoodsPrice();

    List<JSONObject> cityGoodsSales();

    List<JSONObject> provinceGoodsSales();

    List<JSONObject> provincePostfreeRate();

    List<JSONObject> shopGoodsSales();

    List<JSONObject> taobaoGoodsSales(@Param("type") String type, @Param("shopName") String shopName, @Param("province") String province);

    List<JSONObject> shopGmv();

    List<JSONObject> cityGmv();

    List<JSONObject> executeRawSql(@Param("sql") String sql);

}
