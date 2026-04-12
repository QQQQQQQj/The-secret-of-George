# -*- coding: utf-8 -*-
"""
模型4: 商品热度（评论数）预测
基于商品特征预测市场热度/评论数
使用: 随机森林 + 特征工程
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import warnings
warnings.filterwarnings('ignore')

from db_config import fetch_data

class ProductHeatPredictor:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        
    def load_goods_data(self):
        sql = """
        SELECT 
            gc.title,
            gc.total_sales,
            COALESCE(gco.totel_comments, 0) as total_comments,
            LENGTH(gc.title) as title_length,
            (SELECT AVG(total_sales_amount / NULLIF(total_sales_count, 0)) FROM ads_taobao_beauty_makeup_price_distribute WHERE order_cnt = 4) as market_avg_price
        FROM ads_taobao_beauty_makeup_goods_cnt gc
        LEFT JOIN ads_taobao_beauty_makeup_goods_comments gco ON gc.title = gco.title
        ORDER BY gc.total_sales DESC
        LIMIT 30
        """
        df = fetch_data(sql)
        return df
    
    def extract_title_features(self, title):
        if pd.isna(title):
            return {'brand_score': 0, 'keyword_count': 0, 'has_promo': 0, 'function_count': 0}
        
        features = {
            'brand_score': 0,
            'keyword_count': 0,
            'has_promo': 0,
            'function_count': 0,
            'title_len': len(title)
        }
        
        brands = ['妮维雅', '美宝莲', '蜜丝佛陀', 'innisfree', '悦诗风吟', '相宜本草', 
                  '自然堂', 'CHANDO', '佰草集', '兰蔻', '雅漾', '雅诗兰黛', '资生堂',
                  '欧莱雅', '娇兰', '薇姿', '雪花秀', '倩碧', '兰芝', '美加净', '欧珀莱']
        
        for brand in brands:
            if brand in title:
                features['brand_score'] = len(brand)
                break
        
        keywords = ['保湿', '补水', '清洁', '控油', '祛痘', '防晒', '遮瑕', '美白', 
                   '抗皱', '淡斑', '卸妆', '唇膏', '口红', '洗面奶', '面膜', '套装']
        for kw in keywords:
            if kw in title:
                features['keyword_count'] += 1
        
        if any(x in title for x in ['双11', '来啦', '更划算', '套组', '套装', '正品']):
            features['has_promo'] = 1
            
        functions = ['温和', '深层', '持久', '清爽', '滋润', '防水', '不晕染', '轻薄', '便携']
        for func in functions:
            if func in title:
                features['function_count'] += 1
                
        return features
    
    def train_heat_model(self):
        df = self.load_goods_data()
        if len(df) < 5:
            return {'error': '商品数据不足'}
        
        title_features = df['title'].apply(self.extract_title_features).apply(pd.Series)
        
        df = pd.concat([df.reset_index(drop=True), title_features.reset_index(drop=True)], axis=1)
        
        feature_cols = ['total_sales', 'title_length', 'brand_score', 'keyword_count', 
                       'has_promo', 'function_count', 'title_len']
        
        available_cols = [c for c in feature_cols if c in df.columns]
        X = df[available_cols].fillna(0).values
        y = df['total_comments'].values
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=6,
            min_samples_split=3,
            random_state=42
        )
        
        cv_scores = cross_val_score(model, X_scaled, y, cv=3, scoring='r2')
        model.fit(X_scaled, y)
        
        self.model = model
        
        predictions = model.predict(X_scaled)
        
        product_predictions = []
        for i, row in df.iterrows():
            actual_comments = row.get('total_comments', 0)
            pred_comments = predictions[i]
            
            heat_score = self._calc_heat_score(pred_comments, row.get('total_sales', 0))
            
            product_predictions.append({
                'title': str(row['title'])[:50] + '...' if len(str(row['title'])) > 50 else str(row['title']),
                'actual_sales': int(row.get('total_sales', 0)),
                'actual_comments': int(actual_comments),
                'predicted_comments': round(float(pred_comments), 0),
                'heat_score': round(heat_score, 2),
                'heat_level': self._get_heat_level(heat_score),
                'brand_score': int(row.get('brand_score', 0)),
                'keyword_count': int(row.get('keyword_count', 0)),
                'has_promo': int(row.get('has_promo', 0)),
                'optimization_suggestion': self._get_optimization_suggestion(heat_score, row)
            })
        
        product_predictions.sort(key=lambda x: x['heat_score'], reverse=True)
        
        feature_importance = dict(zip(available_cols, model.feature_importances_.tolist()))
        feature_importance = dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))
        
        top_hot = [p for p in product_predictions if p['heat_level'] in ['🔥 爆款', '⭐ 热门']]
        potential_gems = [p for p in product_predictions if p['predicted_comments'] > p['actual_comments'] * 1.5][:5]
        
        return {
            'product_predictions': product_predictions,
            'model_metrics': {
                'cv_r2_mean': round(cv_scores.mean(), 4),
                'overall_r2': round(model.score(X_scaled, y), 4),
                'products_analyzed': len(df)
            },
            'feature_importance': {k: round(v, 4) for k, v in feature_importance.items()},
            'insights': {
                'hot_products': top_hot[:10],
                'potential_gems': potential_gems,
                'key_success_factors': list(feature_importance.keys())[:3],
                'avg_heat_score': round(np.mean([p['heat_score'] for p in product_predictions]), 2)
            }
        }
    
    def _calc_heat_score(self, predicted_comments, sales):
        if sales == 0:
            return 0
        comment_ratio = predicted_comments / sales
        score = 50
        
        score += min(predicted_comments / 100000 * 20, 30)
        score += min(comment_ratio * 100 * 15, 25)
        
        if predicted_comments > 500000:
            score += 15
        elif predicted_comments > 200000:
            score += 10
            
        return min(max(score, 0), 100)
    
    def _get_heat_level(self, score):
        if score >= 85:
            return "🔥 爆款"
        elif score >= 70:
            return "⭐ 热门"
        elif score >= 55:
            return "📈 上升中"
        elif score >= 40:
            return "📊 一般"
        else:
            return "❄️ 冷门"
    
    def _get_optimization_suggestion(self, heat_score, row):
        if heat_score < 40:
            suggestions = []
            if row.get('keyword_count', 0) < 2:
                suggestions.append("增加热门关键词")
            if row.get('has_promo', 0) == 0:
                suggestions.append("添加促销标签")
            if row.get('brand_score', 0) == 0:
                suggestions.append("强化品牌露出")
            return "；".join(suggestions) if suggestions else "需要综合优化"
        elif heat_score < 60:
            return "有潜力，可适当增加营销投入"
        elif heat_score < 80:
            return "表现良好，保持当前策略"
        else:
            return "爆款潜质，建议加大推广力度"

heat_predictor = ProductHeatPredictor()
