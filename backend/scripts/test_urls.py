import urllib.request
import ssl
import sys
from services.trending_engine import VERIFIED_STORE_CATALOG
from db.database import SessionLocal
from db import models

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

print('=== TESTING SEED CATALOG URLS ===')
for item in VERIFIED_STORE_CATALOG:
    url = item['product_url']
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=6) as resp:
            print(f"[OK {resp.status}] {item['store']} | {item['deal_key']} | {url[:70]}")
    except urllib.error.HTTPError as e:
        print(f"[HTTP {e.code}] {item['store']} | {item['deal_key']} | {url[:70]}")
    except Exception as e:
        print(f"[ERR {type(e).__name__}] {item['store']} | {item['deal_key']} | {url[:70]}")

print('\n=== TESTING DB PRODUCTS URLS ===')
db = SessionLocal()
prods = db.query(models.Product).all()
for p in prods:
    url = p.product_url
    store = p.store or (p.platform.value if hasattr(p.platform, 'value') else str(p.platform))
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=6) as resp:
            print(f"[OK {resp.status}] DB {p.id} {store} | {p.product_name[:30]} | {url[:70]}")
    except urllib.error.HTTPError as e:
        print(f"[HTTP {e.code}] DB {p.id} {store} | {p.product_name[:30]} | {url[:70]}")
    except Exception as e:
        print(f"[ERR {type(e).__name__}] DB {p.id} {store} | {p.product_name[:30]} | {url[:70]}")
