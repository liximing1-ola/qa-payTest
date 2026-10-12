# -*- coding: utf-8 -*-
"""临时诊断：iOS 退款核实——哪个 App 在退（aid + /v1/apps 反查名称与 bundleId）、
退的哪些货币（币种×件数×原币金额×折CNY）、国家分布、SKU、退款日期与原购买月份。
用完即删"""
import os
import sys
from collections import defaultdict
from datetime import date, timedelta

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_asc_daily as asc

APP_LIST = {int(a['app_id']): a['name'] for a in asc.APP_LIST}

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
print(f"=== iOS 退款核实（{start_d} ~ {end_d}）===")
print("TSV 列名:", list(df.columns))

units = pd.to_numeric(df['Units'], errors='coerce').fillna(0)
price = pd.to_numeric(df['Customer Price'], errors='coerce').fillna(0.0)
df = df.assign(_u=units, _p=price)
neg = df[df['_u'] < 0].copy()
print(f"退款行数：{len(neg)}  件数合计：{int(-neg['_u'].sum())}")

country_col = next((c for c in ('Country', 'Customer Country', 'Country Code')
                    if c in neg.columns), None)

by_aid = defaultdict(lambda: {
    'cnt': 0, 'cur': defaultdict(lambda: [0, 0.0]),
    'country': defaultdict(int), 'sku': set(), 'days': defaultdict(int),
    'pmonth': defaultdict(int)})
for _, r in neg.iterrows():
    aid = int(r['Apple Identifier'])
    g = by_aid[aid]
    n = int(-r['_u'])
    g['cnt'] += n
    cur = str(r['Customer Currency'])
    g['cur'][cur][0] += n
    g['cur'][cur][1] += r['_p'] * n
    if country_col:
        g['country'][str(r[country_col])] += n
    g['sku'].add(f"{r['SKU']}({r['Title']})")
    g['days'][str(r['_rd'])] += n
    pd_ = str(r.get('Purchase Date') or '')
    if len(pd_) >= 7:
        g['pmonth'][pd_[:7]] += n

for aid in sorted(by_aid, key=lambda a: -by_aid[a]['cnt']):
    g = by_aid[aid]
    print(f"\naid={aid} [{APP_LIST.get(aid, '未在APP_LIST')}] 退款 {g['cnt']} 件")
    for cur, (n, amt) in sorted(g['cur'].items(), key=lambda x: -x[1][0]):
        cny = asc.CNY_RATES.get(cur, 1.0) * amt
        print(f"  币种 {cur}: {n} 件 / {amt:,.2f} {cur} ≈ {cny:,.2f} CNY")
    if g['country']:
        print("  国家:", dict(sorted(g['country'].items(), key=lambda x: -x[1])))
    print("  日期:", dict(sorted(g['days'].items())))
    print("  原购买月:", dict(sorted(g['pmonth'].items())))
    skus = sorted(g['sku'])
    print(f"  SKU({len(skus)}):", skus[:10], '...' if len(skus) > 10 else '')

total_cny = sum(asc.CNY_RATES.get(c, 1.0) * v[1]
                for g in by_aid.values() for c, v in g['cur'].items())
print(f"\n退款折CNY合计: {total_cny:,.2f}")

# /v1/apps 反查报表中出现过的全部 aid 的 App 名与 bundleId
all_aids = sorted({int(a) for a in df['Apple Identifier']})
ids_param = ','.join(str(a) for a in all_aids)
resp = requests.get("https://api.appstoreconnect.apple.com/v1/apps",
                    headers={"Authorization": f"Bearer {token}"},
                    params={"filter[id]": ids_param,
                            "fields[apps]": "name,bundleId", "limit": 200},
                    timeout=30)
print(f"\n=== /v1/apps 反查（报表共 {len(all_aids)} 个 aid，HTTP {resp.status_code}）===")
if resp.status_code == 200:
    found = {int(x['id']): (x['attributes'].get('name'),
                            x['attributes'].get('bundleId'))
             for x in resp.json().get('data', [])}
    for aid in all_aids:
        if aid in found:
            mark = '★' if aid in APP_LIST else ('◀有退款' if aid in by_aid else '')
            print(f"aid={aid}: {found[aid][0]}  bundleId={found[aid][1]}  {mark}")
    missing = [a for a in all_aids if a not in found]
    if missing:
        print("接口未返回（不在当前账号可见 App 列表，疑似已下架/转移）:", missing)
else:
    print("查询失败:", resp.text[:300])
