#!/usr/bin/env python3
"""16688 shop-watch fallback check via public goods-detail API (no login).
14:00 round: browser main check in progress; API cross-check of key items + suppliers."""
import json, time, urllib.request, os, sys

URL = "https://www.16688.com.cn/shopApi/goods/detail"
ITEMS = [
    # 9 price-rise items
    "G58765224","G64054971","G71458844","G90637135","G12318610","G17273603",
    "G92032851","G21381900","G45545033",
    # key stock items
    "G67214403","G80457088","G22200558","G65757790","G94280804","G39950048",
    "G26230358","G39193217","G13584753","G83827625","G28305841","G44914240","G82673430",
    "G11182810","G23289171","G60579329",
    # 29 out-of-stock card items (16:10 list; G21381900/G45545033 already listed)
    "G12640624","G23332833","G13886309","G22406493","G18127331","G71298007",
    "G53068374","G70235614","G49403972","G94140838","G16751470","G74037190",
    "G57932882","G32057196","G38697421","G94224454","G65330164",
    "G82948110","G81226147","G95850652","G33029203","G54198080","G33989962",
    "G57555737","G37396230","G16159068","G95114834",
    # supplier items
    "G58623390","G28249616","G43352737","G43047814","G44535765","G17135024",
    "G16457492","G88583447","G10715427","G55860591","G67540683","G62882706",
    "G17363849","G43172769","G93046088","G64421416","G63655921","G35609721",
    "G95596017","G86294008","G91878107","G86111857","G95821598","G96905314",
    "G70325220","G66960080","G21995299","G74489049",
    "G33553847","G34439275","G40777543","G79955434","G33269562","G89746857",
    "G23344813","G97462192","G55076329","G72948188","G47203469","G28676896",
    "G14749149","G19785887","G77101321","G56885639","G69846615","G10789744","G98655567",
    "G68180283","G90483699","G66935304",
    "G49713567","G27313376","G55303397","G46648196","G84612822","G54326466",
    "G39865326","G72763691","G71919958","G35649984","G41978113","G78937097",
]

def fetch(no, tries=3):
    body = json.dumps({"goods_no": no}).encode()
    req = urllib.request.Request(URL, data=body,
        headers={"Content-Type": "application/json",
                 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
    last = None
    for _ in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception as e:
            last = e
            time.sleep(2)
    return {"_error": str(last)}

out_path = os.path.expanduser("~/workspace/shop-watch/check_api_1400.jsonl")
results = []
for no in ITEMS:
    res = fetch(no)
    d = res.get("data") if isinstance(res, dict) else None
    if isinstance(d, dict):
        rec = {"goods_no": no, "name": d.get("name"), "price": d.get("price"),
               "stock": d.get("stock_available_quantity"),
               "status": d.get("stock_available_status"),
               "delivery": d.get("delivery_method"),
               "shop": d.get("shop_no"), "sales": d.get("sales_count_text")}
    elif isinstance(res, dict) and res.get("code") == 0:
        rec = {"goods_no": no, "absent": True, "msg": res.get("msg")}
    else:
        rec = {"goods_no": no, "error": str(res.get("_error"))}
    results.append(rec)
    print(json.dumps(rec, ensure_ascii=False), flush=True)
    time.sleep(1.5)
with open(out_path, "w") as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print("DONE", len(results), file=sys.stderr)
