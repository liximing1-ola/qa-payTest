# -*- coding: utf-8 -*-
"""临时诊断：拉近 14 天 ASC TSV 全行，按 Apple Identifier 聚合——下载/正销售/退款
Units 分布 + Title 样例，定性退款行的 6 个未知 aid 到底是什么 App。用完即删"""
import sys
import os
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_asc_daily as asc
import pandas as pd

AID_NAME = {str(a['app_id']): a['name'] for a in asc.APP_LIST}
DAYS = 14
end_d = date.today() - timedelta(days=1)
start_d = end_d - timedelta(days=DAYS - 1)

stats = {}
for i in range(DAYS):
    d = start_d + timedelta(days=i)
    try:
        df = asc.get_asc_daily_report(d)
    except Exception as e:
        if 'code:404' in str(e):
            continue
        raise
    df['_u'] = pd.to_numeric(df['Units'], errors='coerce').fillna(0)
    df['_t'] = df['Product Type Identifier'].astype(str)
    for aid, g in df.groupby('Apple Identifier'):
        aid = str(aid)
        s = stats.setdefault(aid, {'dl_units': 0, 'pos_units': 0, 'neg_units': 0,
                                   'neg_days': [], 'dl_titles': set(), 'sku_titles': set()})
        s['dl_units'] += int(g.loc[g['_t'].isin(['1', '3']), '_u'].sum())
        s['pos_units'] += int(g.loc[g['_u'] > 0, '_u'].sum())
        neg = int(-g.loc[g['_u'] < 0, '_u'].sum())
        if neg:
            s['neg_units'] += neg
            s['neg_days'].append(f"{d:%m-%d}")
        for t in g.loc[g['_t'].isin(['1', '3']), 'Title'].unique()[:2]:
            s['dl_titles'].add(str(t))
        for t in g.loc[g['_u'] < 0, 'Title'].unique()[:2]:
            s['sku_titles'].add(str(t))

print(f"=== iOS aid 分布（{start_d} ~ {end_d}，共 {len(stats)} 个 Apple Identifier）===")
for aid, s in sorted(stats.items()):
    name = AID_NAME.get(aid, '!! 不在APP_LIST')
    print(f"aid={aid} [{name}]")
    print(f"  下载Units(类型1+3)={s['dl_units']}  正销售Units={s['pos_units']}  "
          f"退款Units={s['neg_units']}  退款日={s['neg_days']}")
    print(f"  下载行Title样例={sorted(s['dl_titles'])[:2]}")
    print(f"  退款行Title样例={sorted(s['sku_titles'])[:3]}")
