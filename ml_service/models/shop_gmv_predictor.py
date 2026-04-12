# -*- coding: utf-8 -*-
"""
模型3: 店铺GMV预测与潜力评估
使用 XGBoost / Random Forest 预测各店铺未来GMV
结合销量、销售额、评论数等多维特征
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import cross_val_score
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

from db_config import fetch_data

class ShopGMVPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        
    def load_shop_data(self):
        sql = """
        SELECT 
            s.store_name,
            s.total_sales_amount,
            s.total_sales_count,
            COALESCE(c.total_comments, 0) as total_comments,
            s.total_sales_amount / NULLIF(s.total_sales_count, 0) as avg_order_value,
            COALESCE(c.total_comments, 0) / NULLIF(s.total_sales_count, 0) as comment_rate
        FROM ads_taobao_beauty_makeup_store_amt_cnt s
        LEFT JOIN ads_taobao_beauty_makeup_store_comments c ON s.store_name = c.store_name
        ORDER BY s.total_sales_amount DESC
        """
        df = fetch_data(sql)
        return df
    
    def load_shop_gmv_detail(self):
        sql = """
        SELECT NAME as shop_name, SUM(deal * price) as gmv, 
               COUNT(*) as product_cnt, AVG(price) as avg_price,
               SUM(deal) as total_deal, STDDEV(price) as price_std
        FROM t_taobao_goods_sales
        WHERE NAME != 'INTO YOU旗舰店'
        GROUP BY NAME
        ORDER BY gmv DESC
        LIMIT 50
        """
        df = fetch_data(sql)
        return df
    
    def train_gmv_model(self):
        df = self.load_shop_data()
        if len(df) < 5:
            return {'error': '店铺数据不足'}
        
        feature_cols = ['total_sales_amount', 'total_sales_count', 'total_comments', 
                       'avg_order_value', 'comment_rate']
        
        X = df[feature_cols].fillna(0).values
        y = df['total_sales_amount'].values
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            subsample=0.8,
            random_state=42
        )
        
        cv_scores = cross_val_score(model, X_scaled, y, cv=3, scoring='r2')
        model.fit(X_scaled, y)
        
        self.model = model
        self.scaler = scaler
        
        predictions = model.predict(X_scaled)
        
        shop_predictions = []
        for i, row in df.iterrows():
            actual_gmv = row['total_sales_amount']
            pred_gmv = predictions[i]
            growth_potential = ((pred_gmv - actual_gmv) / actual_gmv * 100) if actual_gmv > 0 else 0
            
            score = self._calculate_potential_score(row, predictions[i])
            
            shop_predictions.append({
                'shop_name': row['store_name'],
                'actual_gmv': float(actual_gmv),
                'predicted_gmv': round(float(pred_gmv), 2),
                'total_sales': int(row['total_sales_count']),
                'total_comments': int(row['total_comments']),
                'avg_order_value': round(float(row['avg_order_value']), 2),
                'growth_potential_pct': round(growth_potential, 2),
                'potential_score': round(score, 2),
                'potential_level': self._get_potential_level(score),
                'recommendation': self._get_shop_recommendation(score, row)
            })
        
        shop_predictions.sort(key=lambda x: x['potential_score'], reverse=True)
        
        feature_importance = dict(zip(feature_cols, model.feature_importances_.tolist()))
        feature_importance = dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))
        
        top_growth = [s for s in shop_predictions if s['growth_potential_pct'] > 10][:5]
        top_stable = [s for s in shop_predictions if abs(s['growth_potential_pct']) < 10][:5]
        
        return {
            'shop_predictions': shop_predictions,
            'model_metrics': {
                'cv_r2_mean': round(cv_scores.mean(), 4),
                'cv_r2_std': round(cv_scores.std(), 4),
                'overall_r2': round(r2_score(y, predictions), 4),
                'rmse': round(np.sqrt(mean_squared_error(y, predictions)), 2),
                'mae': round(mean_absolute_error(y, predictions), 2)
            },
            'feature_importance': {k: round(v, 4) for k, v in feature_importance.items()},
            'insights': {
                'top_growth_potential': top_growth,
                'most_stable': top_stable,
                'key_driver': max(feature_importance.items(), key=lambda x: x[1])[0],
                'total_shops_analyzed': len(df)
            }
        }
    
    def predict_city_gmv(self):
        df = self.load_shop_gmv_detail()
        if len(df) == 0:
            return {'error': '无城市GMV数据'}
        
        results = []
        for _, row in df.iterrows():
            results.append({
                'name': row['shop_name'],
                'gmv': round(float(row['gmv']), 2),
                'product_cnt': int(row['product_cnt']),
                'avg_price': round(float(row['avg_price']), 2),
                'total_deal': int(row['total_deal']),
                'price_std': round(float(row['price_std']), 2) if pd.notna(row['price_std']) else 0
            })
        
        results.sort(key=lambda x: x['gmv'], reverse=True)
        
        total_gmv = sum(r['gmv'] for r in results)
        for r in results:
            r['gmv_share_pct'] = round(r['gmv'] / total_gmv * 100, 2)
        
        return {
            'city_gvm_ranking': results[:30],
            'total_gmv': round(total_gmv, 2),
            'shop_count': len(results)
        }
    
    def _calculate_potential_score(self, row, predicted):
        score = 50
        comments_ratio = row.get('total_comments', 0) / max(row.get('total_sales_count', 1), 1)
        score += min(comments_ratio * 10, 20)
        
        aov = row.get('avg_order_value', 0)
        if 10 < aov < 50:
            score += 15
        elif aov >= 50:
            score += 10
            
        growth = (predicted - row.get('total_sales_amount', 0)) / max(row.get('total_sales_amount', 1), 1) * 100
        score += min(max(growth, -20), 30)
        
        return min(max(score, 0), 100)
    
    def _get_potential_level(self, score):
        if score >= 80:
            return "极高潜力 ⭐⭐⭐⭐⭐"
        elif score >= 65:
            return "高潜力 ⭐⭐⭐⭐"
        elif score >= 50:
            return "中等潜力 ⭐⭐⭐"
        elif score >= 35:
            return "一般 ⭐⭐"
        else:
            return "待提升 ⭐"
    
    def _get_shop_recommendation(self, score, row):
        if score >= 80:
            return "重点投入资源，扩大营销，增加SKU"
        elif score >= 65:
            return "保持增长态势，优化产品结构"
        elif score >= 50:
            return "稳定运营，适度营销推广"
        elif score >= 35:
            return "需要分析瓶颈，考虑促销策略"
        else:
            return "建议重新评估定位或调整策略"

gmv_predictor = ShopGMVPredictor()
