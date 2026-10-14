# -*- coding: utf-8 -*-
"""临时诊断：拉最近 7 天 ASC 报表，按 aid 分组统计，定位谁是凶手数据"""
import sys
from datetime import date

sys.path.insert(0, r'd:\qa-payTest\daily_report')
import fetch_asc_daily as asc
import pandas as pd

AID_SSS = '1483169890'
AID_BXY = '1599063568'

reports = asc.get_recent_reports(10)
days_sorted = sorted(reports)[-7:]
print(f'有数据的日期：{[d.strftime("%m-%d") for d in days_sorted]}')
print()

for d in days_sorted:
    df = reports[d]
    print(f'=== {d:%Y-%m-%d} ===')
    print(f'TSV 总行数：{len(df)}')
    print(f'Apple Identifier 列 dtype: {df["Apple Identifier"].dtype}')
    print(f'唯一 Apple Identifier 值：{sorted(df["Apple Identifier"].unique())[:10]}')
    
    # 按 aid 分组统计
    for aid, name in [(AID_BXY, '不夜星球'), (AID_SSS, '谁是凶手')]:
        app_df = df[df['Apple Identifier'].astype(str) == aid]
        if len(app_df) == 0:
            print(f'{name}({aid}): 0 行')
            continue
        price = pd.to_numeric(app_df['Customer Price'], errors='coerce').fillna(0.0)
        units = pd.to_numeric(app_df['Units'], errors='coerce').fillna(0)
        gross = (price * units).sum()
        neg_units = units[units < 0].sum()
        print(f'{name}({aid}): {len(app_df)}行, 销售额={gross:+.2f}, 退款={int(-neg_units)}件')
    
    # 其他 aid（非两个主力 App）
    other_df = df[~df['Apple Identifier'].astype(str).isin([AID_BXY, AID_SSS])]
    if len(other_df) > 0:
        price = pd.to_numeric(other_df['Customer Price'], errors='coerce').fillna(0.0)
        units = pd.to_numeric(other_df['Units'], errors='coerce').fillna(0)
        gross = (price * units).sum()
        neg_units = units[units < 0].sum()
        other_aids = other_df['Apple Identifier'].unique()
        print(f'其他 aid({len(other_aids)}个): 销售额={gross:+.2f}, 退款={int(-neg_units)}件')
        print(f'  aid 列表：{sorted([str(a) for a in other_aids])[:15]}')
    print()
