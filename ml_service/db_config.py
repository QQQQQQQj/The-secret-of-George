# -*- coding: utf-8 -*-
"""
数据库配置 - 连接MySQL shangpinfenxistr 数据库
"""
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
import pandas as pd

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'shangpinfenxistr',
    'charset': 'utf8mb4'
}

def get_engine():
    url = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?charset={DB_CONFIG['charset']}"
    engine = create_engine(
        url,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_recycle=3600,
        pool_pre_ping=True
    )
    return engine

def fetch_data(sql: str) -> pd.DataFrame:
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(text(sql), conn)
    return df

def execute_sql(sql: str):
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()

def fetch_dict_data(sql: str) -> list:
    df = fetch_data(sql)
    return df.to_dict(orient='records')
