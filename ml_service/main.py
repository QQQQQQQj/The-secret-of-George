# -*- coding: utf-8 -*-
"""
ML预测服务 - FastAPI 主应用
提供6大机器学习预测能力的RESTful API
端口: 6003
"""
import sys
import io
import os

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
import time
import logging

from models.time_series_predictor import predictor as ts_predictor
from models.price_elasticity_model import elasticity_model as pe_model
from models.shop_gmv_predictor import gmv_predictor as gmv_model
from models.product_heat_predictor import heat_predictor as heat_model
from models.region_sales_predictor import region_predictor as region_model
from models.category_trend_predictor import trend_predictor as trend_model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="淘宝商品销售数据 ML 预测服务",
    description="基于机器学习的销量/价格/GMV/热度/地区/品类预测系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictionResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: str = ""
    execution_time: float = 0.0

@app.get("/")
async def root():
    return {
        "service": "淘宝商品销售数据 ML 预测服务",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/api/predict/sales-forecast - 时序销量预测",
            "/api/predict/amount-forecast - 时序销售额预测",
            "/api/predict/price-elasticity - 价格弹性分析",
            "/api/predict/category-price - 品类价格分析",
            "/api/predict/shop-gmv - 店铺GMV预测",
            "/api/predict/city-gmv - 城市GMV排名",
            "/api/predict/product-heat - 商品热度预测",
            "/api/predict/province-sales - 省份销量预测",
            "/api/predict/city-sales - 城市销量分布",
            "/api/predict/category-trend - 品类趋势预测",
            "/api/predict/all - 全部模型预测(一键运行)"
        ]
    }

@app.get("/api/predict/sales-forecast", response_model=PredictionResponse)
async def sales_forecast(days: int = Query(default=30, ge=7, le=180, description="预测天数")):
    start_time = time.time()
    try:
        result = ts_predictor.train_sales_forecast(days=days)
        exec_time = time.time() - start_time
        
        if 'error' in result:
            return PredictionResponse(success=False, message=result['error'], execution_time=exec_time)
        
        return PredictionResponse(
            success=True,
            data=result,
            message=f"成功预测未来{days}天销量",
            execution_time=exec_time
        )
    except Exception as e:
        logger.error(f"销量预测失败: {str(e)}")
        return PredictionResponse(success=False, message=str(e), execution_time=time.time()-start_time)

@app.get("/api/predict/amount-forecast", response_model=PredictionResponse)
async def amount_forecast(days: int = Query(default=30, ge=7, le=180, description="预测天数")):
    start_time = time.time()
    try:
        result = ts_predictor.train_amount_forecast(days=days)
        exec_time = time.time() - start_time
        
        if 'error' in result:
            return PredictionResponse(success=False, message=result['error'], execution_time=exec_time)
        
        return PredictionResponse(
            success=True,
            data=result,
            message=f"成功预测未来{days}天销售额",
            execution_time=exec_time
        )
    except Exception as e:
        logger.error(f"销售额预测失败: {str(e)}")
        return PredictionResponse(success=False, message=str(e), execution_time=time.time()-start_time)

@app.get("/api/predict/price-elasticity", response_model=PredictionResponse)
async def price_elasticity():
    start_time = time.time()
    try:
        result = pe_model.train_elasticity_model()
        exec_time = time.time() - start_time
        
        if 'error' in result:
            return PredictionResponse(success=False, message=result['error'], execution_time=exec_time)
        
        return PredictionResponse(
            success=True,
            data=result,
            message="价格弹性分析完成",
            execution_time=exec_time
        )
    except Exception as e:
        logger.error(f"价格弹性分析失败: {str(e)}")
        return PredictionResponse(success=False, message=str(e), execution_time=time.time()-start_time)

@app.get("/api/predict/category-price", response_model=PredictionResponse)
async def category_price_analysis():
    start_time = time.time()
    try:
        result = pe_model.category_price_analysis()
        exec_time = time.time() - start_time
        
        return PredictionResponse(
            success=True,
            data=result,
            message="品类价格分析完成",
            execution_time=exec_time
        )
    except Exception as e:
        logger.error(f"品类价格分析失败: {str(e)}")
        return PredictionResponse(success=False, message=str(e), execution_time=time.time()-start_time)

@app.get("/api/predict/shop-gmv", response_model=PredictionResponse)
async def shop_gmv_prediction():
    start_time = time.time()
    try:
        result = gmv_model.train_gmv_model()
        exec_time = time.time() - start_time
        
        if 'error' in result:
            return PredictionResponse(success=False, message=result['error'], execution_time=exec_time)
        
        return PredictionResponse(
            success=True,
            data=result,
            message="店铺GMV预测完成",
            execution_time=exec_time
        )
    except Exception as e:
        logger.error(f"店铺GMV预测失败: {str(e)}")
        return PredictionResponse(success=False, message=str(e), execution_time=time.time()-start_time)

@app.get("/api/predict/city-gmv", response_model=PredictionResponse)
async def city_gmv_prediction():
    start_time = time.time()
    try:
        result = gmv_model.predict_city_gmv()
        exec_time = time.time() - start_time
        
        if 'error' in result:
            return PredictionResponse(success=False, message=result['error'], execution_time=exec_time)
        
        return PredictionResponse(
            success=True,
            data=result,
            message="城市GMV排名计算完成",
            execution_time=exec_time
        )
    except Exception as e:
        logger.error(f"城市GMV排名失败: {str(e)}")
        return PredictionResponse(success=False, message=str(e), execution_time=time.time()-start_time)

@app.get("/api/predict/product-heat", response_model=PredictionResponse)
async def product_heat_prediction():
    start_time = time.time()
    try:
        result = heat_model.train_heat_model()
        exec_time = time.time() - start_time
        
        if 'error' in result:
            return PredictionResponse(success=False, message=result['error'], execution_time=exec_time)
        
        return PredictionResponse(
            success=True,
            data=result,
            message="商品热度预测完成",
            execution_time=exec_time
        )
    except Exception as e:
        logger.error(f"商品热度预测失败: {str(e)}")
        return PredictionResponse(success=False, message=str(e), execution_time=time.time()-start_time)

@app.get("/api/predict/province-sales", response_model=PredictionResponse)
async def province_sales_prediction():
    start_time = time.time()
    try:
        result = region_model.train_province_model()
        exec_time = time.time() - start_time
        
        if 'error' in result:
            return PredictionResponse(success=False, message=result['error'], execution_time=exec_time)
        
        return PredictionResponse(
            success=True,
            data=result,
            message="省份销量预测完成",
            execution_time=exec_time
        )
    except Exception as e:
        logger.error(f"省份销量预测失败: {str(e)}")
        return PredictionResponse(success=False, message=str(e), execution_time=time.time()-start_time)

@app.get("/api/predict/city-sales", response_model=PredictionResponse)
async def city_sales_distribution():
    start_time = time.time()
    try:
        result = region_model.predict_city_distribution()
        exec_time = time.time() - start_time
        
        if 'error' in result:
            return PredictionResponse(success=False, message=result['error'], execution_time=exec_time)
        
        return PredictionResponse(
            success=True,
            data=result,
            message="城市销量分布分析完成",
            execution_time=exec_time
        )
    except Exception as e:
        logger.error(f"城市销量分布分析失败: {str(e)}")
        return PredictionResponse(success=False, message=str(e), execution_time=time.time()-start_time)

@app.get("/api/predict/category-trend", response_model=PredictionResponse)
async def category_trend_prediction(future_periods: int = Query(default=12, ge=3, le=24, description="预测月数")):
    start_time = time.time()
    try:
        result = trend_model.train_trend_model(future_periods=future_periods)
        exec_time = time.time() - start_time
        
        if 'error' in result:
            return PredictionResponse(success=False, message=result['error'], execution_time=exec_time)
        
        return PredictionResponse(
            success=True,
            data=result,
            message=f"品类趋势预测完成（未来{future_periods}个月）",
            execution_time=exec_time
        )
    except Exception as e:
        logger.error(f"品类趋势预测失败: {str(e)}")
        return PredictionResponse(success=False, message=str(e), execution_time=time.time()-start_time)

@app.get("/api/predict/all", response_model=PredictionResponse)
async def run_all_predictions(sales_days: int = Query(default=30, ge=7, le=180)):
    start_time = time.time()
    results = {}
    
    predictions = [
        ("sales_forecast", lambda: ts_predictor.train_sales_forecast(days=sales_days)),
        ("amount_forecast", lambda: ts_predictor.train_amount_forecast(days=sales_days)),
        ("price_elasticity", lambda: pe_model.train_elasticity_model()),
        ("category_price", lambda: pe_model.category_price_analysis()),
        ("shop_gmv", lambda: gmv_model.train_gmv_model()),
        ("city_gmv", lambda: gmv_model.predict_city_gmv()),
        ("product_heat", lambda: heat_model.train_heat_model()),
        ("province_sales", lambda: region_model.train_province_model()),
        ("city_sales", lambda: region_model.predict_city_distribution()),
        ("category_trend", lambda: trend_model.train_trend_model())
    ]
    
    for name, func in predictions:
        try:
            results[name] = {"status": "success", "data": func()}
        except Exception as e:
            results[name] = {"status": "failed", "error": str(e)}
            logger.error(f"{name} 预测失败: {str(e)}")
    
    total_time = time.time() - start_time
    successful = sum(1 for r in results.values() if r["status"] == "success")
    
    return PredictionResponse(
        success=True,
        data={
            "predictions": results,
            "summary": {
                "total_models": len(predictions),
                "successful": successful,
                "failed": len(predictions) - successful,
                "total_execution_time": round(total_time, 2)
            }
        },
        message=f"全部{len(predictions)}个模型预测完成，成功{successful}个",
        execution_time=total_time
    )

if __name__ == "__main__":
    print("=" * 60)
    print(" [ML] Taobao Goods Sales ML Prediction Service Starting...")
    print("   URL: http://localhost:6003")
    print("   API Docs: http://localhost:6003/docs")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=6003)
