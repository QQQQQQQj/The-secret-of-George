# -*- coding: utf-8 -*-
"""
模型1: 时序销量/销售额预测
使用 statsmodels (Holt-Winters/SARIMA) 进行时间序列预测
支持: 日销量预测、日销售额预测、未来N天预测
Windows兼容版本
"""
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

from db_config import fetch_data, fetch_dict_data

try:
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    from statsmodels.tsa.arima.model import ARIMA
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False

class TimeSeriesPredictor:
    def __init__(self):
        self.sales_model = None
        self.amount_model = None
        
    def load_daily_data(self):
        sql = "SELECT date_key, total_sales_amount, total_sales_count FROM ads_taobao_beauty_makeup_daily_amt_cnt ORDER BY date_key"
        df = fetch_data(sql)
        return df
    
    def train_sales_forecast(self, days=30):
        df = self.load_daily_data()
        if len(df) < 5:
            return {'error': '数据不足，至少需要5天数据'}
        
        dates = pd.to_datetime(df['date_key'])
        sales_values = df['total_sales_count'].values.astype(float)
        amount_values = df['total_sales_amount'].values.astype(float)
        
        history_data = []
        for _, row in df.iterrows():
            history_data.append({
                'date': str(row['date_key'].date()) if hasattr(row['date_key'], 'date') else str(row['date_key']),
                'sales_amount': float(row['total_sales_amount']),
                'sales_count': int(row['total_sales_count'])
            })
        
        if HAS_STATSMODELS:
            predict_data, trend_info, accuracy = self._predict_with_statsmodels(sales_values, days)
        else:
            predict_data, trend_info, accuracy = _predict_with_numpy(sales_values, days)
        
        return {
            'history': history_data,
            'prediction': predict_data,
            'components': trend_info,
            'model_accuracy': accuracy,
            'forecast_days': days
        }
    
    def train_amount_forecast(self, days=30):
        df = self.load_daily_data()
        if len(df) < 5:
            return {'error': '数据不足，至少需要5天数据'}
        
        amount_values = df['total_sales_amount'].values.astype(float)
        
        if HAS_STATSMODELS:
            predict_data, accuracy = self._predict_amount_with_statsmodels(amount_values, days)
        else:
            predict_data, accuracy = _predict_amount_with_numpy(amount_values, days)
        
        return {
            'prediction': predict_data,
            'model_accuracy': accuracy,
            'forecast_days': days
        }
    
    def _predict_with_statsmodels(self, values, days):
        try:
            model = ExponentialSmoothing(
                values,
                trend='add',
                seasonal=None,
                damped_trend=True
            ).fit(optimized=True)
            
            forecast = model.forecast(days)
            
            fitted = model.fittedvalues
            actual = values[len(values) - len(fitted):]
            pred_fitted = fitted.values if hasattr(fitted, 'values') else np.array(fitted)
            
            last_date = pd.Timestamp('2022-11-14')
            predict_data = []
            for i, val in enumerate(forecast):
                future_date = last_date + pd.Timedelta(days=i+1)
                conf_width = abs(val) * 0.15
                predict_data.append({
                    'date': future_date.strftime('%Y-%m-%d'),
                    'predicted_sales': round(float(val), 2),
                    'lower_bound': round(float(val - conf_width), 2),
                    'upper_bound': round(float(val + conf_width), 2)
                })
            
            trend_val = '上升' if forecast.mean() > values[-3:].mean() else '下降'
            growth_rate = round((forecast.mean() - values[-3:].mean()) / abs(values[-3:].mean()) * 100, 2) if values[-3:].mean() != 0 else 0
            
            accuracy = self._calc_accuracy(actual, pred_fitted[:len(actual)])
            
            return predict_data, {
                'trend': trend_val,
                'growth_rate': max(growth_rate, -99.99)
            }, accuracy
            
        except Exception as e:
            return _predict_with_numpy(values, days)[0], {'trend': '稳定', 'growth_rate': 0}, {'mape': 0, 'rmse': 0, 'mae': 0, 'r2': 0}
    
    def _predict_amount_with_statsmodels(self, values, days):
        try:
            model = ExponentialSmoothing(
                values,
                trend='add',
                seasonal=None,
                damped_trend=True
            ).fit(optimized=True)
            
            forecast = model.forecast(days)
            
            fitted = model.fittedvalues
            actual = values[len(values) - len(fitted):]
            pred_fitted = fitted.values if hasattr(fitted, 'values') else np.array(fitted)
            
            last_date = pd.Timestamp('2022-11-14')
            predict_data = []
            for i, val in enumerate(forecast):
                future_date = last_date + pd.Timedelta(days=i+1)
                conf_width = abs(val) * 0.15
                predict_data.append({
                    'date': future_date.strftime('%Y-%m-%d'),
                    'predicted_amount': round(float(val), 2),
                    'lower_bound': round(float(val - conf_width), 2),
                    'upper_bound': round(float(val + conf_width), 2)
                })
            
            accuracy = self._calc_accuracy(actual, pred_fitted[:len(actual)])
            return predict_data, accuracy
            
        except Exception:
            return _predict_amount_with_numpy(values, days)
    
    def _calc_accuracy(self, actual, predicted):
        try:
            if len(actual) == 0 or len(predicted) == 0:
                return {'mape': 0, 'rmse': 0, 'mae': 0, 'r2': 0}
            min_len = min(len(actual), len(predicted))
            actual = actual[:min_len]
            predicted = predicted[:min_len]
            
            mape = np.mean(np.abs((actual - predicted) / np.where(actual == 0, 1, actual))) * 100
            rmse = float(np.sqrt(np.mean((actual - predicted) ** 2)))
            mae = float(np.mean(np.abs(actual - predicted)))
            
            ss_res = np.sum((actual - predicted) ** 2)
            ss_tot = np.sum((actual - np.mean(actual)) ** 2)
            r2 = round(1 - ss_res / ss_tot, 4) if ss_tot > 0 else 0
            
            return {
                'mape': round(mape, 2),
                'rmse': round(rmse, 2),
                'mae': round(mae, 2),
                'r2': r2
            }
        except Exception:
            return {'mape': 0, 'rmse': 0, 'mae': 0, 'r2': 0}


def _predict_with_numpy(values, days):
    n = len(values)
    if n < 3:
        last_val = values[-1] if len(values) > 0 else 0
        result = []
        for i in range(days):
            result.append({
                'date': f'2022-11-{15+i}',
                'predicted_sales': round(float(last_val), 2),
                'lower_bound': round(float(last_val * 0.9), 2),
                'upper_bound': round(float(last_val * 1.1), 2)
            })
        return result, {'trend': '稳定', 'growth_rate': 0}, {'mape': 0, 'rmse': 0, 'mae': 0, 'r2': 0}
    
    recent = values[-min(n, 7):]
    slope = (recent[-1] - recent[0]) / max(len(recent) - 1, 1)
    
    base = values[-1]
    decay = 0.95
    
    predictions = []
    current = base
    for i in range(days):
        current = current + slope * (decay ** i)
        noise_factor = 0.02 * abs(current)
        pred_val = current + np.random.normal(0, noise_factor)
        predictions.append(pred_val)
    
    last_date = pd.Timestamp('2022-11-14')
    predict_data = []
    for i, val in enumerate(predictions):
        future_date = last_date + pd.Timedelta(days=i+1)
        conf_width = abs(val) * 0.18
        predict_data.append({
            'date': future_date.strftime('%Y-%m-%d'),
            'predicted_sales': round(float(max(val, 0)), 2),
            'lower_bound': round(float(max(val - conf_width, 0)), 2),
            'upper_bound': round(float(val + conf_width), 2)
        })
    
    trend = '上升' if slope > 0 else ('下降' if slope < 0 else '稳定')
    avg_recent = np.mean(recent[-3:])
    growth = round((predictions[-1] - avg_recent) / abs(avg_recent) * 100, 2) if avg_recent != 0 else 0
    
    fitted = []
    for i in range(n):
        idx = max(0, i - min(n, 7))
        seg = values[idx:i+1] if i == 0 else values[idx:i+1]
        seg_slope = (seg[-1] - seg[0]) / max(len(seg) - 1, 1)
        fitted_val = seg[0] + seg_slope * (i - idx)
        fitted.append(fitted_val)
    
    accuracy_vals = values[max(0, n-len(fitted)):]
    fit_vals = np.array(fitted[max(0, n-len(fitted)):])
    mape = np.mean(np.abs((accuracy_vals - fit_vals) / np.where(accuracy_vals==0, 1, accuracy_vals))) * 100
    rmse = np.sqrt(np.mean((accuracy_vals - fit_vals)**2))
    
    return predict_data, {'trend': trend, 'growth_rate': max(growth, -99.99)}, {
        'mape': round(mape, 2), 'rmse': round(rmse, 2), 'mae': round(np.mean(np.abs(accuracy_vals-fit_vals)), 2),
        'r2': round(1 - np.sum((accuracy_vals-fit_vals)**2)/np.sum((accuracy_vals-np.mean(accuracy_vals))**2), 4) if np.std(accuracy_vals) > 0 else 0
    }

def _predict_amount_with_numpy(values, days):
    data, _, acc = _predict_with_numpy(values, days)
    for item in data:
        item['predicted_amount'] = item.pop('predicted_sales')
        lb = item.pop('lower_bound')
        ub = item.pop('upper_bound')
        item['lower_bound'] = lb
        item['upper_bound'] = ub
    return data, acc

predictor = TimeSeriesPredictor()
