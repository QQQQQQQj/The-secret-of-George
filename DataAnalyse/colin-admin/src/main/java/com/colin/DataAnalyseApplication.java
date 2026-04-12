package com.colin;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration;

/**
 * 启动程序
 * 
 * @author ruoyi
 */
@SpringBootApplication(exclude = { DataSourceAutoConfiguration.class })
public class DataAnalyseApplication
{
    public static void main(String[] args)
    {
        // System.setProperty("spring.devtools.restart.enabled", "false");
        SpringApplication.run(DataAnalyseApplication.class, args);
        System.out.println("(♥◠‿◠)ﾉﾞ  淘宝商品销售数据分析系统启动成功   ლ(´ڡ`ლ)ﾞ");
    }
}