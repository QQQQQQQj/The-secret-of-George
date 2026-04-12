# -*- coding: utf-8 -*-
"""
模型5: 地区销量分布预测
结合省份/城市特征，预测各地区销量潜力
使用: 聚类 + 回归分析
"""
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import silhouette_score
import warnings
warnings.filterwarnings('ignore')

from db_config import fetch_data

class RegionSalesPredictor:
    def __init__(self):
        self.province_model = None
        self.city_model = None
        
    def load_province_data(self):
        sales_sql = "SELECT province, total_sales FROM ads_taobao_province_goods_sales ORDER BY total_sales DESC"
        rate_sql = "SELECT province, postfree_rate FROM ads_taobao_province_postfree_rate ORDER BY postfree_rate DESC"
        
        sales_df = fetch_data(sales_sql)
        rate_df = fetch_data(rate_sql)
        
        merged = pd.merge(sales_df, rate_df, on='province', how='left')
        merged['postfree_rate'] = merged['postfree_rate'].fillna(0.5)
        
        return merged
    
    def load_city_data(self):
        sql = "SELECT city, total_sales FROM ads_taobao_city_goods_sales ORDER BY total_sales DESC LIMIT 50"
        df = fetch_data(sql)
        return df
    
    def get_region_type(self, name):
        east = ['上海', '江苏', '浙江', '安徽', '福建', '江西', '山东']
        south = ['广东', '广西', '海南']
        central = ['河南', '湖北', '湖南']
        north = ['北京', '天津', '河北', '山西', '内蒙古']
        west = ['四川', '重庆', '贵州', '云南', '西藏']
        northwest = ['陕西', '甘肃', '青海', '宁夏', '新疆']
        northeast = ['辽宁', '吉林', '黑龙江']
        
        if name in east:
            return 1, '华东'
        elif name in south:
            return 2, '华南'
        elif name in central:
            return 3, '华中'
        elif name in north:
            return 4, '华北'
        elif name in west:
            return 5, '西南'
        elif name in northwest:
            return 6, '西北'
        elif name in northeast:
            return 7, '东北'
        else:
            return 0, '海外/其他'
    
    def train_province_model(self):
        df = self.load_province_data()
        if len(df) < 5:
            return {'error': '省份数据不足'}
        
        df['region_code'], df['region_name'] = zip(*df['province'].apply(lambda x: self.get_region_type(x)))
        df['is_coastal'] = df['region_code'].isin([1, 2, 4]).astype(int)
        df['sales_tier'] = pd.cut(df['total_sales'], bins=5, labels=[1, 2, 3, 4, 5], duplicates='drop').fillna(3).astype(int)
        
        feature_cols = ['postfree_rate', 'region_code', 'is_coastal']
        X = df[feature_cols].values
        y = df['total_sales'].values
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        model = GradientBoostingRegressor(n_estimators=80, max_depth=4, learning_rate=0.1, random_state=42)
        model.fit(X_scaled, y)
        self.province_model = (model, scaler, feature_cols)
        
        predictions = model.predict(X_scaled)
        
        kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
        df['cluster'] = kmeans.fit_predict(X_scaled)
        
        cluster_labels = {0: '🔵 潜力市场', 1: '🟢 成熟市场', 2: '🟡 成长市场', 3: '🔴 待开发'}
        
        region_predictions = []
        for i, row in df.iterrows():
            actual = row['total_sales']
            pred = predictions[i]
            
            region_predictions.append({
                'province': row['province'],
                'actual_sales': int(actual),
                'predicted_sales': round(float(pred), 0),
                'market_share_pct': round(actual / df['total_sales'].sum() * 100, 3),
                'postfree_rate': float(row['postfree_rate']),
                'region': row['region_name'],
                'cluster': int(row['cluster']),
                'cluster_label': cluster_labels.get(int(row['cluster']), '未知'),
                'deviation_pct': round((pred - actual) / actual * 100, 2) if actual > 0 else 0,
                'potential_index': self._calc_potential_index(pred, actual),
                'strategy': self._get_region_strategy(int(row['cluster']), pred, actual)
            })
        
        region_predictions.sort(key=lambda x: x['potential_index'], reverse=True)
        
        cluster_summary = df.groupby('cluster').agg({
            'province': 'count',
            'total_sales': ['mean', 'sum']
        }).round(0)
        
        top_potential = [r for r in region_predictions if r['potential_index'] >= 70][:10]
        mature_markets = [r for r in region_predictions if r['cluster'] == 1][:5]
        
        return {
            'region_predictions': region_predictions,
            'cluster_analysis': {
                'cluster_count': len(cluster_labels),
                'clusters': {cluster_labels[k]: {
                    'province_count': int(df[df['cluster'] == k].shape[0]),
                    'avg_sales': int(df[df['cluster'] == k]['total_sales'].mean()),
                    'total_sales': int(df[df['cluster'] == k]['total_sales'].sum())
                } for k in range(4)}
            },
            'model_metrics': {
                'r2_score': round(model.score(X_scaled, y), 4),
                'provinces_analyzed': len(df)
            },
            'insights': {
                'top_potential_regions': top_potential,
                'mature_markets': mature_markets,
                'best_region_group': max([(v['total_sales'], k) for k, v in {cluster_labels[k]: {'total_sales': int(df[df['cluster']==k]['total_sales'].sum())} for k in range(4)}.items()])[1]
            }
        }
    
    def predict_city_distribution(self):
        df = self.load_city_data()
        if len(df) == 0:
            return {'error': '无城市数据'}
        
        results = []
        total = df['total_sales'].sum()
        cumsum = 0
        
        for i, row in df.iterrows():
            cumsum += row['total_sales']
            results.append({
                'city': row['city'],
                'sales': int(row['total_sales']),
                'market_share_pct': round(row['total_sales'] / total * 100, 3),
                'cumulative_pct': round(cumsum / total * 100, 2),
                'rank': i + 1,
                'tier': self._get_city_tier(i + 1, row['total_sales'], total)
            })
        
        pareto_80 = sum(1 for r in results if r['cumulative_pct'] <= 80)
        
        return {
            'city_ranking': results[:50],
            'statistics': {
                'total_cities': len(results),
                'pareto_80_cities': pareto_80,
                'top10_concentration': round(sum(r['sales'] for r in results[:10]) / total * 100, 2),
                'avg_city_sales': int(total / len(results))
            }
        }
    
    def _calc_potential_index(self, predicted, actual):
        if actual == 0:
            return 50
        ratio = predicted / actual
        score = 50
        
        if ratio > 1.2:
            score += min((ratio - 1) * 30, 40)
        elif ratio < 0.8:
            score -= min((1 - ratio) * 20, 30)
            
        if actual > 50000000:
            score += 10
            
        return min(max(score, 0), 100)
    
    def _get_region_strategy(self, cluster, predicted, actual):
        strategies = {
            0: "重点开发新客户，加大市场推广投入",
            1: "维护客户关系，提升客单价和复购率",
            2: "优化供应链，扩大市场份额",
            3: "评估市场可行性，考虑合作或代理模式"
        }
        return strategies.get(cluster, "根据实际情况制定策略")
    
    def _get_city_tier(self, rank, sales, total):
        share = sales / total * 100
        if rank <= 5 or share > 5:
            return "S级 - 核心城市"
        elif rank <= 15 or share > 2:
            return "A级 - 重点城市"
        elif rank <= 30 or share > 1:
            return "B级 - 成长城市"
        else:
            return "C级 - 潜力城市"

region_predictor = RegionSalesPredictor()
