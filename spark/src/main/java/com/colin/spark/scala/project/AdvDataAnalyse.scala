package com.colin.spark.scala.project

import org.apache.spark.sql.{SaveMode, SparkSession}
import org.apache.spark.{SparkConf, SparkContext}

import java.util.Properties

/**
 * desc: 日志分析
 */
object AdvDataAnalyse {
    def main(args: Array[String]): Unit = {
        val conf = getSparkContext("AdvDataAnalyse").getConf
        val session = SparkSession.builder()
          .appName("CSVDataFrameSql")
          .config(conf)
          .getOrCreate()
        val properties: Properties = new Properties()
        properties.setProperty("user", "root")
        properties.setProperty("password", "123456")
        properties.setProperty("driver", "com.mysql.cj.jdbc.Driver")
        properties.setProperty("numPartitions", "10")
        val chenggonganliDf = session.read.jdbc("jdbc:mysql://localhost:3306/springboot3937h?useUnicode=true&characterEncoding=UTF-8&allowMultiQueries=true&autoReconnect=true&useSSL=false&rewriteBatchedStatements=true&serverTimezone=Asia/Shanghai",
            "chenggonganli", properties)
        chenggonganliDf.createTempView("chenggonganli_view")
        val guanggaotoufangDf = session.read.jdbc("jdbc:mysql://localhost:3306/springboot3937h?useUnicode=true&characterEncoding=UTF-8&allowMultiQueries=true&autoReconnect=true&useSSL=false&rewriteBatchedStatements=true&serverTimezone=Asia/Shanghai",
            "guanggaotoufang", properties)
        guanggaotoufangDf.createTempView("guanggaotoufang_view")
        val shujubaobiaoDf = session.read.jdbc("jdbc:mysql://localhost:3306/springboot3937h?useUnicode=true&characterEncoding=UTF-8&allowMultiQueries=true&autoReconnect=true&useSSL=false&rewriteBatchedStatements=true&serverTimezone=Asia/Shanghai",
            "shujubaobiao", properties)
        shujubaobiaoDf.createTempView("shujubaobiao_view")


        //1.数量
        session.sql("select pinpaimingcheng,chanpinxinxi," +
          "count(IF(ispay ='已支付',1,null)) as payNum," +
          "count(IF(ispay ='未支付',1,null)) as unPayNum " +
          "from guanggaotoufang_view group by pinpaimingcheng,chanpinxinxi").write.mode(SaveMode.Overwrite)
          .option("truncate", value = true)
          .jdbc("jdbc:mysql://localhost:3306/springboot3937h?useUnicode=true&characterEncoding=UTF-8&allowMultiQueries=true&autoReconnect=true&useSSL=false&rewriteBatchedStatements=true&serverTimezone=Asia/Shanghai",
              "adv_analyse_one", properties)

        //2.
        session.sql("select pinpaimingcheng,toufangfangan," +
          "sum(clicknum) as click_total," +
          "sum(thumbsupnum) as thumbsupnum_total," +
          "sum(crazilynum) as crazilynum_total " +
          "from chenggonganli_view group by pinpaimingcheng,toufangfangan").write.mode(SaveMode.Overwrite)
          .option("truncate", value = true)
          .jdbc("jdbc:mysql://localhost:3306/springboot3937h?useUnicode=true&characterEncoding=UTF-8&allowMultiQueries=true&autoReconnect=true&useSSL=false&rewriteBatchedStatements=true&serverTimezone=Asia/Shanghai",
              "adv_analyse_two", properties)

        //3.用户数
        session.sql("select pinpaimingcheng,zhanghao," +
          "sum(fangwenyonghu) as fangwenyonghu_total " +
          "from shujubaobiao_view group by pinpaimingcheng,zhanghao").write.mode(SaveMode.Overwrite)
          .option("truncate", value = true)
          .jdbc("jdbc:mysql://localhost:3306/springboot3937h?useUnicode=true&characterEncoding=UTF-8&allowMultiQueries=true&autoReconnect=true&useSSL=false&rewriteBatchedStatements=true&serverTimezone=Asia/Shanghai",
              "adv_analyse_three", properties)

    }

    def getSparkContext(name: String): SparkContext = {
        val conf = new SparkConf()
        conf.setAppName(name)
          .setMaster("local")
        conf.set("spark.driver.host", "localhost")
        conf.set("spark.files.overwrite", "true")
        new SparkContext(conf)
    }
}
