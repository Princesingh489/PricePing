import json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    )
    page.goto('https://www.amazon.in/s?k=deals', timeout=20000)
    page.wait_for_timeout(3000)
    
    results = page.evaluate('''() => {
        const out = [];
        const items = document.querySelectorAll('div[data-asin]:not([data-asin=""])');
        for (const it of items) {
            const asin = it.getAttribute('data-asin');
            const titleEl = it.querySelector('h2 a span');
            const linkEl = it.querySelector('h2 a');
            const imgEl = it.querySelector('img.s-image');
            const priceWhole = it.querySelector('span.a-price-whole');
            const mrpEl = it.querySelector('span.a-price.a-text-price span.a-offscreen');
            
            if (titleEl && linkEl && imgEl && priceWhole) {
                const title = titleEl.innerText.trim();
                const price = parseFloat(priceWhole.innerText.replace(/[^0-9]/g, ''));
                const mrp = mrpEl ? parseFloat(mrpEl.innerText.replace(/[^0-9]/g, '')) : price * 1.5;
                out.push({
                    asin,
                    title,
                    product_url: 'https://www.amazon.in/dp/' + asin,
                    image_url: imgEl.src,
                    price,
                    mrp,
                    discount_percent: Math.round(((mrp - price) / mrp) * 100)
                });
            }
        }
        return out;
    }''')
    browser.close()
    
    with open('scripts/amazon_found.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("Amazon products found:", len(results))
