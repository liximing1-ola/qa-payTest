# -*- coding: utf-8 -*-
"""临时诊断：近 7 天鸿蒙 IAP 订单逐单核对——tradeState/tradeType/currency 分布、
各币种金额、按日聚合、summarize 口径合计、商品 TOP，定位"金额不对"根因。用完即删"""
import sys
import os
from collections import Counter
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_harmony_daily as hm

end_d = date.today() - timedelta(days=1)
start_d = end_d - timedelta(days=6)
start_ms = int(datetime(start_d.year, start_d.month, start_d.day,
                        tzinfo=hm.CST).timestamp() * 1000)
end_ms = int(datetime(end_d.year, end_d.month, end_d.day,
                      tzinfo=hm.CST).timestamp() * 1000) + 24 * 3600 * 1000
orders = hm.query_iap_orders_range(start_ms, end_ms)
print(f"=== 鸿蒙 IAP 订单核对（{start_d} ~ {end_d} 北京时间，不含今日）===")
print(f"原始订单总数：{len(orders)}")
print("tradeState分布:", dict(Counter(o.get('tradeState') for o in orders)))
print("tradeType分布:", dict(Counter(o.get('tradeType') for o in orders)))
print("currency分布:", dict(Counter(o.get('currency') for o in orders)))

by_cur = {}
for o in orders:
    if o.get('tradeState') != 0:
        continue
    cur = o.get('currency') or '?'
    slot = by_cur.setdefault(cur, [0, 0.0, 0, 0.0])
    if o.get('tradeType') == 'REFUND':
        slot[2] += 1
        slot[3] += float(o.get('refundMoney') or 0)
    else:
        slot[0] += 1
        slot[1] += float(o.get('payMoney') or 0)
for cur, (cnt, pay, rcnt, refund) in by_cur.items():
    print(f"币种 {cur}: 支付 {cnt} 笔 / {pay:,.2f}  退款 {rcnt} 笔 / {refund:,.2f}")

by_day = hm.summarize_orders_by_day(orders)
for d in sorted(by_day):
    a = by_day[d]
    print(f"{d}  单 {a['count']}  额 {a['amount']:,.2f}  "
          f"退 {a['refund_count']} / {a['refund_amount']:,.2f}")
s = hm.summarize_orders(orders)
print(f"summarize_orders 口径合计: 单 {s['purchase_count']} / {s['purchase_amount']:,.2f}  "
      f"退 {s['refund_count']} / {s['refund_amount']:,.2f}  净 {s['net_amount']:,.2f}")

by_prod = Counter()
for o in orders:
    if o.get('tradeState') == 0 and o.get('tradeType') != 'REFUND':
        by_prod[str(o.get('productName') or o.get('productId'))] += 1
print("商品TOP8:", by_prod.most_common(8))
