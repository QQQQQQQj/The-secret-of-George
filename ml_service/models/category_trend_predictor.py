# -*- coding: utf-8 -*-
"""
模型6: 品类销量趋势预测
预测7大品类的未来销量占比变化趋势
使用: 时间序列外推 + 市场份额分析
"""
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

from db_config import fetch_data

class CategoryTrendPredictor:
    def __init__(self):
        self.trend_models = {}
        
    def load_category_data(self):
        price_sql = "SELECT goods_category, avg_price FROM ads_taobao_category_goods_price ORDER BY avg_price"
        sales_sql = "SELECT goods_category, total_sales FROM ads_taobao_category_goods_sales ORDER BY total_sales"
        
        price_df = fetch_data(price_sql)
        sales_df = fetch_data(sales_sql)
        
        merged = pd.merge(price_df, sales_df, on='goods_category')
        return merged
    
    def get_category_attributes(self, category):
        attrs = {
            '食品': {'necessity': 0.9, 'frequency': 0.95, 'seasonality': 0.3, 'price_sensitivity': 0.8},
            '化妆品': {'necessity': 0.6, 'frequency': 0.6, 'seasonality': 0.5, 'price_sensitivity': 0.4},
            '护肤品': {'necessity': 0.65, 'frequency': 0.55, 'seasonality': 0.45, 'price_sensitivity': 0.35},
            '家电': {'necessity': 0.5, 'frequency': 0.2, 'seasonality': 0.3, 'price_sensitivity': 0.25},
            '家具': {'necessity': 0.35, 'frequency': 0.15, 'seasonality': 0.2, 'price_sensitivity': 0.3},
            '服装': {'necessity': 0.55, 'frequency': 0.75, 'seasonality': 0.8, 'price_sensitivity': 0.6},
            '笔记本电脑': {'necessity': 0.4, 'frequency': 0.15, 'seasonality': 0.25, 'price_sensitivity': 0.2}
        }
        return attrs.get(category, {'necessity': 0.5, 'frequency': 0.5, 'seasonality': 0.4, 'price_sensitivity': 0.5})
    
    def train_trend_model(self, future_periods=12):
        df = self.load_category_data()
        if len(df) < 3:
            return {'error': '品类数据不足'}
        
        total_sales = df['total_sales'].sum()
        df['market_share'] = df['total_sales'] / total_sales * 100
        
        for _, row in df.iterrows():
            cat = row['goods_category']
            attrs = self.get_category_attributes(cat)
            
            current_share = row['market_share']
            price = row['avg_price']
            
            base_growth = self._estimate_base_growth(attrs)
            
            price_factor = max(0.1, min(2.0, (500 / price) ** 0.3))
            
            saturation_factor = max(0.5, 1 - current_share / 100)
            
            trend_direction = self._get_trend_direction(cat, current_share, attrs)
            
            predicted_shares = []
            share = current_share
            
            for period in range(future_periods):
                seasonal_adj = 1 + 0.1 * np.sin(2 * np.pi * period / 12) * attrs['seasonality']
                
                noise = np.random.normal(0, 0.005)
                
                change_rate = base_growth * price_factor * saturation_factor * seasonal_adj + noise
                
                share = share * (1 + change_rate / 100)
                predicted_shares.append(max(share, 0.5))
            
            self.trend_models[cat] = {
                'current_share': current_share,
                'predicted_shares': predicted_shares,
                'trend_direction': trend_direction,
                'attributes': attrs
            }
        
        category_trends = []
        for _, row in df.iterrows():
            cat = row['goods_category']
            model_info = self.trend_models.get(cat, {})
            
            final_share = model_info.get('predicted_shares', [])[-1] if model_info.get('predicted_shares') else row['market_share']
            share_change = final_share - row['market_share']
            
            growth_potential = self._assess_growth_potential(
                cat, 
                row['market_share'], 
                final_share,
                model_info.get('trend_direction', '稳定'),
                model_info.get('attributes', {})
            )
            
            category_trends.append({
                'category': cat,
                'current_market_share': round(row['market_share'], 2),
                'future_market_share_12m': round(final_share, 2),
                'share_change_pct': round(share_change, 2),
                'current_total_sales': int(row['total_sales']),
                'avg_price': float(row['avg_price']),
                'trend_direction': model_info.get('trend_direction', '稳定'),
                'growth_potential_score': round(growth_potential['score'], 2),
                'growth_potential_level': growth_potential['level'],
                'recommendation': growth_potential['recommendation'],
                'monthly_prediction': [round(s, 2) for s in model_info.get('predicted_shares', [row['market_share']] * 12)]
            })
        
        category_trends.sort(key=lambda x: x['growth_potential_score'], reverse=True)
        
        rising_cats = [c for c in category_trends if c['share_change_pct'] > 0]
        declining_cats = [c for c in category_trends if c['share_change_pct'] < 0]
        
        stable_cats = [c for c in category_trends if abs(c['share_change_pct']) <= 1]
        
        return {
            'category_trends': category_trends,
            'summary': {
                'total_categories': len(df),
                'rising_categories': [{'name': c['category'], 'change': c['share_change_pct']} for c in rising_cats],
                'declining_categories': [{'name': c['category'], 'change': c['share_change_pct']} for c in declining_cats],
                'stable_categories': [c['category'] for c in stable_cats],
                'dominant_category': max(category_trends, key=lambda x: x['current_market_share'])['category'],
                'highest_potential': max(category_trends, key=lambda x: x['growth_potential_score'])['category']
            },
            'portfolio_optimization': self._generate_portfolio_advice(category_trends)
        }
    
    def _estimate_base_growth(self, attrs):
        necessity = attrs['necessity']
        frequency = attrs['frequency']
        seasonality = attrs['seasonality']
        
        base = 0.5
        
        if frequency > 0.7:
            base += 1.5
        elif frequency > 0.4:
            base += 0.8
            
        if necessity > 0.7:
            base += 0.5
            
        if seasonality > 0.6:
            base *= 1.2
            
        return base
    
    def _get_trend_direction(self, category, current_share, attrs):
        high_share_thresholds = {'食品': 40, '化妆品': 30, '护肤品': 25}
        threshold = high_share_thresholds.get(category, 20)
        
        if current_share > threshold:
            return "📉 成熟期/趋稳"
        elif current_share > threshold * 0.6:
            return "📈 成长期"
        else:
            return "🚀 快速增长期"
    
    def _assess_growth_potential(self, category, current_share, future_share, direction, attrs):
        score = 50
        
        share_change = future_share - current_share
        score += min(share_change * 2, 20)
        
        if direction == "🚀 快速增长期":
            score += 20
        elif direction == "📈 成长期":
            score += 10
            
        if attrs['frequency'] > 0.7:
            score += 10
        if attrs['necessity'] > 0.7:
            score += 5
        if attrs['price_sensitivity'] > 0.5:
            score += 5
            
        if current_share < 10:
            score += 5
            
        score = min(max(score, 0), 100)
        
        if score >= 80:
            level = "⭐⭐⭐⭐⭐ 极高潜力"
        elif score >= 65:
            level = "⭐⭐⭐⭐ 高潜力"
        elif score >= 50:
            level = "⭐⭐⭐ 中等潜力"
        elif score >= 35:
            level = "⭐⭐ 一般"
        else:
            level = "⭐ 待观察"
        
        recommendations = {
            "🚀 快速增长期": f"{category}处于快速增长期，建议加大投入，抢占市场份额",
            "📈 成长期": f"{category}稳步成长，建议优化产品结构，提升竞争力",
            "📉 成熟期/趋稳": f"{category}已成熟，建议聚焦利润率，开发差异化产品"
        }
        
        recommendation = recommendations.get(direction, f"持续关注{category}的市场表现")
        
        return {'score': score, 'level': level, 'recommendation': recommendation}
    
    def _generate_portfolio_advice(self, trends):
        top3 = trends[:3]
        bottom3 = trends[-3:]
        
        advice = []
        advice.append("【核心品类】重点投入资源：" + "、".join([c['category'] for c in top3]))
        advice.append("【优化品类】考虑调整策略：" + "、".join([c['category'] for c in bottom3]))
        
        avg_growth = np.mean([c['share_change_pct'] for c in trends])
        if avg_growth > 1:
            advice.append("整体市场呈扩张态势，可积极布局")
        elif avg_growth < -1:
            advice.append("市场竞争加剧，需精细化运营")
        else:
            advice.append("市场整体平稳，关注结构性机会")
        
        return advice

trend_predictor = CategoryTrendPredictor()
