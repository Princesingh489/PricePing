import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests
from db.database import SessionLocal
from services.trending_engine import TrendingEngine

s = SessionLocal()
res1 = TrendingEngine.get_trending_deals(s, force_refresh=True)
deals1 = res1['deals']
print(f"Total deals: {len(deals1)} across {res1['stores_represented']}")

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

all_images_ok = True
for i, d in enumerate(deals1, 1):
    try:
        r = session.get(d['image_url'], stream=True, timeout=3)
        st = r.status_code
    except Exception as e:
        st = 'ERR'
    if st != 200:
        all_images_ok = False
    print(f"{i:2}. [{d['store']:8}] [{st}] {d['title'][:32]} | Rs {d['price']}/{d['mrp']} ({d['discount_percent']}%)")

print("\n--- REFRESH TEST (Product Change) ---")
res2 = TrendingEngine.get_trending_deals(s, force_refresh=True)
deals2 = res2['deals']
ids1 = [d['id'] for d in deals1]
ids2 = [d['id'] for d in deals2]
print(f"IDs changed on refresh: {ids1 != ids2}")
print(f"First 3 deals on cycle 1: {[d['title'][:25] for d in deals1[:3]]}")
print(f"First 3 deals on cycle 2: {[d['title'][:25] for d in deals2[:3]]}")
print(f"All images return HTTP 200: {all_images_ok}")
s.close()
