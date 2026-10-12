# -*- coding: utf-8 -*-
"""临时：拉近 14 天 iOS 销售报表，提取退款负行——按日/按商品聚合后打印，用完即删"""
import sys
import os
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_asc_daily as asc
import pandas as pd

DAYS = 14
end_d = date.today() - timedelta(days=1)
start_d = end_d - timedelta(days=DAYS - 1)

neg_rows = []
for i in range(DAYS):
    d = start_d + timedelta(days=i)
    try:
        df = asc.get_asc_daily_report(d)
    except Exception as e:
        if 'code:404' in str(e):
            continue
        print(f"[ABORT] {d} 拉取失败：{str(e)[:200]}")
        sys.exit(2)
    units = pd.to_numeric(df['Units'], errors='coerce').fillna(0)
    neg_rows.append(df[units < 0].assign(_day=f"{d:%m-%d}"))

print(f"窗口：{start_d} ~ {end_d}（{DAYS} 天）")
if not neg_rows:
    print("窗口内无退款行")
    sys.exit(0)

all_neg = pd.concat(neg_rows, ignore_index=True)
price = pd.to_numeric(all_neg['Customer Price'], errors='coerce').fillna(0.0)
units = pd.to_numeric(all_neg['Units'], errors='coerce').fillna(0)
all_neg['_amt'] = price * units          # 负值（原币种）
# 逐行复用生产折算口径：{币种: 金额} → CNY
all_neg['_cny'] = [asc._total_cny({c: a})
                   for c, a in zip(all_neg['Customer Currency'], all_neg['_amt'])]

print("\n=== 按日退款（处理日口径）===")
by_day = all_neg.groupby('_day').agg(cnt=('_day', 'size'), units=('Units', 'sum'),
                                     cny=('_cny', 'sum'))
for day, r in by_day.iterrows():
    print(f"{day}  退款 {abs(r['units']):.0f} 件  {abs(r['cny']):,.2f} 元")

print("\n=== 按商品退款（窗口合计）===")
by_sku = all_neg.groupby(['SKU', 'Title']).agg(units=('Units', 'sum'), cny=('_cny', 'sum'))
for (sku, title), r in by_sku.iterrows():
    print(f"{sku} | {title}  {abs(r['units']):.0f} 件  {abs(r['cny']):,.2f} 元")

print("\n=== 原始退款行 ===")
cols = ['_day', 'Apple Identifier', 'SKU', 'Title', 'Units', 'Customer Price',
        'Customer Currency', 'Country Code']
print(all_neg[cols].to_string(index=False))
print(f"\n合计：{abs(all_neg['Units'].sum()):.0f} 件 / {abs(all_neg['_cny'].sum()):,.2f} 元")
