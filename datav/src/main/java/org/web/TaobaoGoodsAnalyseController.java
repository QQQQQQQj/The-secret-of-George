package org.web;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.autoconfigure.EnableAutoConfiguration;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/**
 * 降水量数据分析
 */
@RestController
@EnableAutoConfiguration
@RequestMapping(path = "/taobaoAnalyse", produces = "application/json;charset=UTF-8")
public class TaobaoGoodsAnalyseController {
    @Autowired
    private JdbcTemplate template;


    /**
     * 每个省的商品销量
     * @return
     * @throws IOException
     */
    @RequestMapping(path = "/provinceGoodsSales", method = RequestMethod.GET)
    public EchartData provinceGoodsSales() throws IOException {
        return template.query("select province,total_sales from shangpinfenxistr.ads_taobao_province_goods_sales", rs -> {
            EchartData data = new EchartData();
            while (rs.next()) {
                data.xdata.add(rs.getString(1));
                data.ydata.add(rs.getInt(2));
            }
            return data;
        });
    }

    /**
     * 店铺的销量排名
     * @return
     * @throws IOException
     */
    @RequestMapping(path = "/shopGoodsSales", method = RequestMethod.GET)
    public EchartData shopGoodsSales() throws IOException {
        return template.query("SELECT * from shangpinfenxistr.ads_taobao_shop_goods_sales order by total_sales desc limit 30", rs -> {
            EchartData data = new EchartData();
            while (rs.next()) {
                data.xdata.add(rs.getString(1));
                data.ydata.add(rs.getInt(2));
            }
            return data;
        });
    }

    /**
     * 每种商品的销量
     * @return
     * @throws IOException
     */
    @RequestMapping(path = "/categoryGoodsSales", method = RequestMethod.GET)
    public EchartData categoryGoodsSales() throws IOException {
        return template.query("select * from shangpinfenxistr.ads_taobao_category_goods_sales order by total_sales desc limit 30", rs -> {
            EchartData data = new EchartData();
            while (rs.next()) {
                data.xdata.add(rs.getString(1));
                data.ydata.add(rs.getInt(2));
            }
            return data;
        });
    }

    /**
     * 每个城市的商品均价分析
     * @return
     * @throws IOException
     */
    @RequestMapping(path = "/cityGoodsPrice", method = RequestMethod.GET)
    public EchartData cityGoodsPrice() throws IOException {
        return template.query("select * from shangpinfenxistr.ads_taobao_city_goods_price order by avg_price desc limit 30", rs -> {
            EchartData data = new EchartData();
            while (rs.next()) {
                data.xdata.add(rs.getString(1));
                data.ydata.add(rs.getBigDecimal(2));
            }
            return data;
        });
    }

    /**
     * 城市的商品销量排名
     * @return
     * @throws IOException
     */
    @RequestMapping(path = "/cityGoodsSales", method = RequestMethod.GET)
    public EchartData cityGoodsSales() throws IOException {
        return template.query("select * from shangpinfenxistr.ads_taobao_city_goods_sales order by total_sales desc limit 30", rs -> {
            EchartData data = new EchartData();
            while (rs.next()) {
                data.xdata.add(rs.getString(1));
                data.ydata.add(rs.getInt(2));
            }
            return data;
        });
    }


    public static class EchartData {

        public List<Object> xdata;
        public List<Object> ydata;
        public List<Object> zdata;
        public List<Object> wdata;

        public EchartData() {
            this.xdata = new ArrayList<Object>();
            this.ydata = new ArrayList<Object>();
            this.zdata = new ArrayList<Object>();
            this.wdata = new ArrayList<Object>();
        }


    }
}
