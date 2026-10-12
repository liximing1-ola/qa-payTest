# -*- coding: utf-8 -*-
"""临时诊断：iOS 退款行原交易时间核实——Begin Date / End Date（原充值/订阅周期），
外加分退款 aid 的近 14 天正向销售按日分布。用完即删"""
import os
import sys
from datetime import date, timedelta

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_asc_daily as asc

end_d = date.today() - timedelta(days=1)
start_d = end_d - timedelta(days=13)
token = asc.get_asc_token()

dfs = []
d = start_d
while d <= end_d:
    try:
        dfs.append(asc.get_asc_daily_report(d, token).assign(_rd=f"{d:%m-%d}"))
    except Exception as e:
        if 'code:404' not in str(e):
            raise
    d += timedelta(days=1)
df = pd.concat(dfs, ignore_index=True)

units = pd.to_numeric(df['Units'], errors='coerce').fillna(0)
df = df.assign(_u=units)
neg = df[df['_u'] < 0].copy()
print(f"=== iOS 退款行原交易时间（{start_d} ~ {end_d}，共 {len(neg)} 行）===")

print("\n--- 退款行关键字段（含原交易周期）---")
show_cols = ['Apple Identifier', 'SKU', 'Title', 'Product Type Identifier', '_u',
             'Customer Price', 'Customer Currency', 'Country Code',
             'Begin Date', 'End Date', 'Parent Identifier', 'Subscription', 'Period',
             'Proceeds Reason', '_rd']
show_cols = [c for c in show_cols if c in neg.columns]
for _, r in neg.sort_values(['Apple Identifier', '_rd']).iterrows():
    print(' | '.join(f"{c}={r[c]}" for c in show_cols))

print("\n--- 按 (aid, SKU, Begin Date) 聚合 ---")
agg = neg.groupby(['Apple Identifier', 'SKU', 'Begin Date', 'End Date'],
                  dropna=False)['_u'].sum()
for (aid, sku, bd, ed), u in agg.items():
    print(f"aid={aid}  {sku}  原交易周期 {bd} ~ {ed}  退款 {int(-u)} 件")

print("\n--- 退款 aid 的正向销售按日分布（近 14 天，看是否仍有新充值/续费）---")
pos = df[df['_u'] > 0]
for aid in sorted(neg['Apple Identifier'].astype(int).unique()):
    sub = pos[pos['Apple Identifier'] == aid]
    if len(sub) == 0:
        print(f"aid={aid}: 近 14 天无正向销售行")
        continue
    by_day = {k: int(v) for k, v in sub.groupby('_rd')['_u'].sum().items()}
    skus = sorted(sub['SKU'].astype(str).unique())[:8]
    print(f"aid={aid}: 正向销售合计 {int(sub['_u'].sum())} 件  按日 {by_day}")
    print(f"    正向SKU样例: {skus}")
