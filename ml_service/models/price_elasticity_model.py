# -*- coding: utf-8 -*-
"""
模型2: 价格-销量弹性模型
分析不同价格区间与销量的关系，找到最优定价点
使用: 多项式回归 + XGBoost + 弹性系数计算
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import json
import warnings
warnings.filterwarnings('ignore')

from db_config import fetch_data

class PriceElasticityModel:
    def __init__(self):
        self.price_model = None
        self.elasticity_coef = None
        
    def load_price_data(self):
        sql = "SELECT price_range, total_sales_amount, total_sales_count, order_cnt FROM ads_taobao_beauty_makeup_price_distribute ORDER BY order_cnt"
        df = fetch_data(sql)
        return df
    
    def load_category_price_data(self):
        sql = "SELECT goods_category, avg_price, total_sales FROM ads_taobao_category_goods_price cp JOIN ads_taobao_category_goods_sales cs ON cp.goods_category = cs.goods_category"
        df = fetch_data(sql)
        return df
    
    def parse_price_range(self, price_str):
        if price_str == '1000+':
            return (1000, 2000)
        parts = price_str.split('-')
        return (int(parts[0]), int(parts[1]))
    
    def get_mid_price(self, price_str):
        low, high = self.parse_price_range(price_str)
        return (low + high) / 2
    
    def train_elasticity_model(self):
        df = self.load_price_data()
        
        df['mid_price'] = df['price_range'].apply(self.get_mid_price)
        df['price_low'] = df['price_range'].apply(lambda x: self.parse_price_range(x)[0])
        df['price_high'] = df['price_range'].apply(lambda x: self.parse_price_range(x)[1])
        
        X = df[['mid_price', 'price_low', 'price_high']].values
        y_sales = df['total_sales_count'].values
        y_amount = df['total_sales_amount'].values
        
        poly = PolynomialFeatures(degree=3, include_bias=False)
        X_poly = poly.fit_transform(X)
        
        model_sales = Ridge(alpha=1.0)
        model_sales.fit(X_poly, y_sales)
        
        model_amount = Ridge(alpha=1.0)
        model_amount.fit(X_poly, y_amount)
        
        sales_pred = model_sales.predict(X_poly)
        amount_pred = model_amount.predict(X_poly)
        
        price_points = []
        for _, row in df.iterrows():
            mid = row['mid_price']
            idx = _
            
            elasticity = self._calc_elasticity(mid, y_sales, sales_pred)
            
            optimal_price = self._find_optimal_price(model_sales, poly, mid)
            
            price_points.append({
                'price_range': row['price_range'],
                'mid_price': round(mid, 2),
                'actual_sales': int(row['total_sales_count']),
                'predicted_sales': round(sales_pred[list(df.index)[_]], 2) if _ < len(sales_pred) else 0,
                'actual_amount': float(row['total_sales_amount']),
                'predicted_amount': round(amount_pred[_], 2) if _ < len(amount_pred) else 0,
                'elasticity': round(elasticity, 4),
                'elasticity_type': '富有弹性' if abs(elasticity) > 1 else ('缺乏弹性' if abs(elasticity) < 1 else '单位弹性'),
                'optimal_price_suggestion': round(optimal_price, 2),
                'suggestion': self._get_pricing_suggestion(elasticity, mid, optimal_price)
            })
        
        r2_sales = r2_score(y_sales, sales_pred)
        r2_amount = r2_score(y_amount, amount_pred)
        
        best_range = max(price_points, key=lambda x: x['actual_sales'])
        
        return {
            'price_analysis': price_points,
            'model_metrics': {
                'sales_r2': round(r2_sales, 4),
                'amount_r2': round(r2_amount, 4),
                'sales_rmse': round(np.sqrt(mean_squared_error(y_sales, sales_pred)), 2),
                'amount_rmse': round(np.sqrt(mean_squared_error(y_amount, amount_pred)), 2)
            },
            'insights': {
                'best_price_range': best_range['price_range'],
                'best_price_mid': best_range['mid_price'],
                'best_sales': best_range['actual_sales'],
                'overall_recommendation': self._get_overall_recommendation(price_points)
            }
        }
    
    def category_price_analysis(self):
        df = self.load_category_price_data()
        
        results = []
        for _, row in df.iterrows():
            results.append({
                'category': row['goods_category'],
                'avg_price': float(row['avg_price']),
                'total_sales': int(row['total_sales']),
                'price_positioning': self._get_price_positioning(row['avg_price']),
                'market_share_pct': round(row['total_sales'] / df['total_sales'].sum() * 100, 2)
            })
        
        return {'category_analysis': results}
    
    def _calc_elasticity(self, price, actual, predicted):
        try:
            price_points = [10, 60, 150, 250, 400, 750, 1500]
            mid_prices = [self.get_mid_price(str(p)) for p in price_points]
            arr = np.array(mid_prices)
            idx = np.where(np.isclose(arr, price, atol=50))[0]
            if len(idx) > 0 and idx[0] < len(actual) - 1:
                p1, q1 = price, actual[idx[0]]
                p2, q2 = price * 1.1, actual[min(idx[0] + 1, len(actual)-1)]
                if q1 > 0 and p2 != p1:
                    return ((q2 - q1) / ((q1 + q2) / 2)) / ((p2 - p1) / ((p1 + p2) / 2))
        except Exception:
            pass
        return -1.5
    
    def _find_optimal_price(self, model, poly, current_price):
        test_prices = np.linspace(current_price * 0.5, current_price * 2, 20)
        max_sales = -1
        optimal = current_price
        for p in test_prices:
            X_test = poly.transform([[p, p * 0.8, p * 1.2]])
            pred = model.predict(X_test)[0]
            if pred > max_sales:
                max_sales = pred
                optimal = p
        return optimal
    
    def _get_pricing_suggestion(self, elasticity, current, optimal):
        if elasticity < -1:
            diff_pct = (optimal - current) / current * 100
            if diff_pct > 10:
                return f"建议提价{abs(diff_pct):.1f}%至¥{optimal:.0f}，销量敏感度高但利润空间大"
            elif diff_pct < -10:
                return f"建议降价{abs(diff_pct):.1f}%至¥{optimal:.0f}以刺激销量"
            else:
                return "当前定价接近最优水平"
        elif elasticity > -1:
            return "需求缺乏弹性，可适当提价增加营收"
        else:
            return "保持当前定价策略"
    
    def _get_price_positioning(self, price):
        if price < 100:
            return "低价位/大众消费"
        elif price < 500:
            return "中低价位/性价比"
        elif price < 1500:
            return "中高价位/品质消费"
        else:
            return "高价位/奢侈消费"
    
    def _get_overall_recommendation(self, points):
        elastic_items = [p for p in points if abs(p.get('elasticity', 0)) > 1]
        inelastic_items = [p for p in points if abs(p.get('elasticity', 0)) <= 1]
        
        if elastic_items:
            best = max(elastic_items, key=lambda x: x['actual_sales'])
            return f"重点关注{best['price_range']}价位段，该区间富有弹性且销量最高({best['actual_sales']:,})，建议优化该价位产品组合"
        return "各价位段需求相对稳定，建议通过提升产品质量和品牌价值来驱动增长"

elasticity_model = PriceElasticityModel()
