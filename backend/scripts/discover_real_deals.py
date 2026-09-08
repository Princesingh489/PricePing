import requests
import json
import re

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'en-IN,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
})

print("Testing AJIO...")
try:
    r = session.get('https://www.ajio.com/api/category/83?currentPage=0&pageSize=10&format=json&query=%3Arelevance%3Adiscountflag%3Atrue', timeout=5)
    print("AJIO status:", r.status_code)
    if r.status_code == 200:
        data = r.json()
        prods = data.get('data', {}).get('products', [])
        print("AJIO prods:", len(prods))
        for p in prods[:5]:
            print(p.get('fnlColorVariantData', {}).get('colorGroup'), p.get('name'), p.get('price'), p.get('wasPriceData'), p.get('images'))
except Exception as e:
    print("AJIO err:", e)
