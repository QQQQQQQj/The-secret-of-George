$(function () {
    var prefix = "/usedCar";
    echarts_1();
    echarts_2();
    echarts_3();
    echarts_4();

    function echarts_1() {
        // 基于准备好的dom，初始化echarts实例
        $.get('/taobaoAnalyse/shopGoodsSales', function (result) {
            var myChart = echarts.init(document.getElementById('echart1'));
            option = {
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'shadow'
                    }
                },
                legend: {
                    data:['销量'],
                    textStyle: {
                        color: "#fff",
                        fontSize: '12',

                    },
                },
                "grid": {
                    "top": "20",
                    "right": "10%",
                    "bottom": "30",
                    "left": "10%",
                },
                // grid: {
                //     left: '3%',
                //     right: '4%',
                //     bottom: '3%',
                //     containLabel: true
                // },
                xAxis: {
                    type: 'value',
                    boundaryGap: [0, 0.01],
                    splitLine: {
                        show: false // 隐藏网格线
                    },
                    axisLabel: {
                        interval: 0,
                        show: true,
                        textStyle: {
                            color: "rgba(255,255,255,.6)",
                            fontSize: '12',
                        },

                    },

                },
                yAxis: {
                    type: 'category',
                    data: result.xdata,
                    splitLine: {
                        show: false // 隐藏网格线
                    },
                    axisLabel: {
                        textStyle: {
                            color: 'rgba(255,255,255,.6)',
                            fontSize:'10',
                        }
                    },
                },

                series: [
                    {
                        name: '销量',
                        type: 'bar',
                        data: result.ydata,
                        itemStyle: {
                            normal: {
                                color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [{
                                    offset: 0,
                                    color: '#FFD700'
                                },
                                    {
                                        offset: 1,
                                        color: '#FFC1C1'
                                    }
                                ]),
                                barBorderRadius: 15,
                            }
                        },
                    },
                ]
            };


            myChart.setOption(option);
            window.addEventListener("resize", function () {
                myChart.resize();
            });
        });



    }

    function echarts_2() {
        $.get("/taobaoAnalyse/categoryGoodsSales", function (result) {
            var myChart = echarts.init(document.getElementById('echart2'));
            option = {
                tooltip: {
                    trigger: 'item',
                    formatter: "{a} <br/>{b} : {c}"
                },
                legend: {
                    orient: 'vertical',
                    top: '25%',
                    left: 0,
                    data: [],
                    textStyle: {
                        color: 'rgba(255,255,255,.5)',
                        fontSize: '12',
                    }
                },

                series: [{
                    name: '销量',
                    type: 'pie',
                    radius: '50%',
                    center: ['60%', '40%'],
                    clockwise: false,
                    data: [],
                    label: {
                        normal: {
                            textStyle: {
                                color: 'rgba(255,255,255,.6)',
                                fontSize: 14,
                            }
                        }
                    },
                    labelLine: {
                        normal: {
                            show: false
                        }
                    },
                    itemStyle: {
                        normal: {
                            //borderWidth: 1,
                            //borderColor: '#ffffff',
                        },
                        emphasis: {
                            borderWidth: 0,
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }
                    }
                }],
                color: ['#836FFF','#CD00CD','#AB82FF','#FFA500', '#B22222'],
                //backgroundColor: '#fff'
            };
            for (let i = 0; i < result.xdata.length; i++) {
                var mapData = {
                    name: '',
                    value: 0
                }
                option.legend.data.push(result.xdata[i])
                mapData.name = result.xdata[i]
                mapData.value = result.ydata[i]
                option.series[0].data.push(mapData)
            }
            myChart.setOption(option);
            $(window).resize(myChart.resize);
        });

    }

    function echarts_3() {
        // 基于准备好的dom，初始化echarts实例

        $.get("/taobaoAnalyse/cityGoodsPrice", function (result) {
            var myChart = echarts.init(document.getElementById('echart3'));
            data = result
            option = {
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'shadow'
                    }
                },
                legend: {
                    data: ['均价'],
                    top: '0',
                    textStyle: {
                        color: "#fff",
                        fontSize: '12',

                    },
                    icon: 'circle',
                    itemGap: 35
                },
                "grid": {
                    "top": "5%",
                    "right": "10%",
                    "bottom": "60",
                    "left": "10%",
                },
                xAxis: [{
                    type: 'category',
                    data: data.xdata,
                    axisLine: {
                        show: true,
                        lineStyle: {
                            color: "rgba(255,255,255,.1)",
                            width: 1,
                            type: "solid"
                        },
                    },
                    axisTick: {
                        show: false,
                    },
                    axisLabel: {
                        interval: 0,
                        rotate: 45,
                        show: true,
                        splitNumber: 5,
                        textStyle: {
                            color: "rgba(255,255,255,.6)",
                            fontSize: '12',
                        },
                        formatter: function (value) {
                            if (value.length > 6) {
                                return value.substring(0, 6) + '...';  // 长文本超出部分隐藏
                            } else {
                                return value;
                            }
                        }
                    },
                }],
                yAxis: [{
                    type: 'value',
                    axisLabel: {
                        //formatter: '{value} %'
                        show: true,
                        textStyle: {
                            color: "rgba(255,255,255,.6)",
                            fontSize: '12',
                        },
                    },
                    axisTick: {
                        show: false,
                    },
                    axisLine: {
                        show: true,
                        lineStyle: {
                            color: "rgba(255,255,255,.1	)",
                            width: 1,
                            type: "solid"
                        },
                    },
                    splitLine: {
                        lineStyle: {
                            color: "rgba(255,255,255,.1)",
                        }
                    }
                }],
                series: [{
                    name: '均价',
                    type: 'scatter',
                    smooth: true,
                    data: data.ydata,
                    itemStyle: {
                        normal: {
                            color: '#EEEE00',
                            opacity: 1,
                            barBorderRadius: 5,
                        }
                    }
                },
                ]
            };

            myChart.setOption(option);
            window.addEventListener("resize", function () {
                myChart.resize();
            });
        });

        // 使用刚指定的配置项和数据显示图表。

    }


    function echarts_4() {

        // 基于准备好的dom，初始化echarts实例
        $.get('/taobaoAnalyse/cityGoodsSales', function (result) {
            // 基于准备好的dom，初始化echarts实例
            var myChart = echarts.init(document.getElementById('echart4'));
            option = {
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {type: 'shadow'},
                },
                "grid": {
                    "top": "15",
                    "right": "10%",
                    "bottom": "40",
                    "left": "50",
                },
                legend: {
                    data: ['销量'],
                    right: 'center',
                    top: 0,
                    textStyle: {
                        color: "#fff"
                    },
                    itemWidth: 12,
                    itemHeight: 10,
                },
                xAxis: [
                    {
                        "type": "category",
                        data: result.xdata,
                        axisLine: {lineStyle: {color: "rgba(255,255,255,.1)"}},
                        axisLabel: {
                            interval: 0,
                            rotate: 45,
                            show: true,
                            splitNumber: 5,
                            textStyle: {
                                color: "rgba(255,255,255,.6)",
                                fontSize: '12',
                            },
                            formatter: function (value) {
                                if (value.length > 6) {
                                    return value.substring(0, 6) + '...';  // 长文本超出部分隐藏
                                } else {
                                    return value;
                                }
                            }
                        },

                    },
                ],
                yAxis: [
                    {
                        "type": "value",
                        splitLine: {show: false},
                        axisTick: {show: false},
                        "axisLabel": {
                            "show": true,
                            color: "rgba(255,255,255,.6)"

                        },
                        axisLine: {lineStyle: {color: 'rgba(255,255,255,.1)'}},//左线色

                    },

                ],
                series: [

                    {
                        "name": "销量",
                        "type": "bar",
                        "data": result.ydata,
                        "barWidth": "20%",
                        "itemStyle": {
                            "normal": {
                                barBorderRadius: 15,
                                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                                    offset: 0,
                                    color: '#FFB5C5'
                                }, {
                                    offset: 1,
                                    color: '#FF34B3'
                                }]),
                            }
                        },
                        "barGap": "0"
                    },
                ]
            };
            // 使用刚指定的配置项和数据显示图表。
            myChart.setOption(option);
            window.addEventListener("resize", function () {
                myChart.resize();
            });
        });

    }






})



		
		
		


		









