package com.colin.project.controller;

import com.alibaba.fastjson.JSONObject;
import com.colin.common.core.controller.BaseController;
import com.colin.common.core.domain.AjaxResult;
import com.colin.common.core.page.TableDataInfo;
import com.colin.common.utils.StringUtils;
import com.colin.system.mapper.project.TaobaoGoodsAnalyseMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Controller
@RequestMapping("/project/taobaoGoodsAnalyse")
public class TaobaoGoodsAnalyseController extends BaseController {
    private String prefix = "project/taobaoGoods";

    @Autowired
    private TaobaoGoodsAnalyseMapper taobaoGoodsAnalyseMapper;

    @GetMapping("/categoryGoodsPriceRoute")
    public String categoryGoodsPriceRoute() {
        return prefix + "/categoryGoodsPriceRoute";
    }

    @GetMapping("/categoryGoodsSalesRoute")
    public String categoryGoodsSalesRoute() {
        return prefix + "/categoryGoodsSalesRoute";
    }

    @GetMapping("/categoryShopGoodsPriceRoute")
    public String categoryShopGoodsPriceRoute() {
        return prefix + "/categoryShopGoodsPriceRoute";
    }

    @GetMapping("/cityGoodsPriceRoute")
    public String cityGoodsPriceRoute() {
        return prefix + "/cityGoodsPriceRoute";
    }

    @GetMapping("/cityGoodsSalesRoute")
    public String cityGoodsSalesRoute() {
        return prefix + "/cityGoodsSalesRoute";
    }
    @GetMapping("/cityGoodsSalesRoute2")
    public String cityGoodsSalesRoute2() {
        return prefix + "/cityGoodsSalesRoute2";
    }

    @GetMapping("/provinceGoodsSalesRoute")
    public String provinceGoodsSalesRoute() {
        return prefix + "/provinceGoodsSalesRoute";
    }

    @GetMapping("/provincePostfreeRateRoute")
    public String provincePostfreeRateRoute() {
        return prefix + "/provincePostfreeRateRoute";
    }

    @GetMapping("/shopGoodsSalesRoute")
    public String shopGoodsSalesRoute() {
        return prefix + "/shopGoodsSalesRoute";
    }

    @GetMapping("/taobaoGoodsSalesRoute")
    public String taobaoGoodsSalesRoute() {
        return prefix + "/taobaoGoodsSalesRoute";
    }


    @GetMapping("/categoryGoodsPrice")
    @ResponseBody
    public AjaxResult categoryGoodsPrice() {
        List<JSONObject> categoryGoodsPrice = taobaoGoodsAnalyseMapper.categoryGoodsPrice();
        return AjaxResult.success(categoryGoodsPrice);
    }

    @GetMapping("/categoryGoodsSales")
    @ResponseBody
    public AjaxResult categoryGoodsSales() {
        List<JSONObject> categoryGoodsSales = taobaoGoodsAnalyseMapper.categoryGoodsSales();
        return AjaxResult.success(categoryGoodsSales);
    }

    @GetMapping("/categoryShopGoodsPrice")
    @ResponseBody
    public AjaxResult categoryShopGoodsPrice(@RequestParam(value = "goodsCategory", required = false) String goodsCategory) {
        if (StringUtils.isBlank(goodsCategory)) {
            goodsCategory = "笔记本电脑";
        }
        List<JSONObject> categoryShopGoodsPrice = taobaoGoodsAnalyseMapper.categoryShopGoodsPrice(goodsCategory);
        return AjaxResult.success(categoryShopGoodsPrice);
    }

    @GetMapping("/cityGoodsPrice")
    @ResponseBody
    public AjaxResult cityGoodsPrice() {
        List<JSONObject> cityGoodsPrice = taobaoGoodsAnalyseMapper.cityGoodsPrice();
        return AjaxResult.success(cityGoodsPrice);
    }

    @GetMapping("/cityGoodsSales")
    @ResponseBody
    public AjaxResult cityGoodsSales() {
        List<JSONObject> cityGoodsSales = taobaoGoodsAnalyseMapper.cityGoodsSales();
        return AjaxResult.success(cityGoodsSales);
    }

    @GetMapping("/provinceGoodsSales")
    @ResponseBody
    public AjaxResult provinceGoodsSales() {
        List<JSONObject> provinceGoodsSales = taobaoGoodsAnalyseMapper.provinceGoodsSales();
        return AjaxResult.success(provinceGoodsSales);
    }

    @GetMapping("/provincePostfreeRate")
    @ResponseBody
    public AjaxResult provincePostfreeRate() {
        List<JSONObject> provincePostfreeRate = taobaoGoodsAnalyseMapper.provincePostfreeRate();
        return AjaxResult.success(provincePostfreeRate);
    }

    @GetMapping("/shopGoodsSales")
    @ResponseBody
    public AjaxResult shopGoodsSales() {
        List<JSONObject> shopGoodsSales = taobaoGoodsAnalyseMapper.shopGoodsSales();
        return AjaxResult.success(shopGoodsSales);
    }
    @GetMapping("/shopGmv")
    @ResponseBody
    public AjaxResult shopGmv() {
        List<JSONObject> shopGmv = taobaoGoodsAnalyseMapper.shopGmv();
        return AjaxResult.success(shopGmv);
    }

    @GetMapping("/cityGmv")
    @ResponseBody
    public AjaxResult cityGmv() {
        List<JSONObject> cityGmv = taobaoGoodsAnalyseMapper.cityGmv();
        return AjaxResult.success(cityGmv);
    }

    @PostMapping("/list")
    @ResponseBody
    public TableDataInfo list(@RequestParam(value = "type", required = false) String type,
                              @RequestParam(value = "shopName", required = false) String shopName,
                              @RequestParam(value = "province", required = false) String province) {
        startPage();
        List<JSONObject> list = taobaoGoodsAnalyseMapper.taobaoGoodsSales(type, shopName, province);
        return getDataTable(list);
    }
}
