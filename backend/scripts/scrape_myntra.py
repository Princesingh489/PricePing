import json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    )
    # Myntra tshirts with 50-100% discount
    page.goto('https://www.myntra.com/men-tshirts?f=Discount%3A50.0_100.0', timeout=20000)
    page.wait_for_timeout(3000)
    
    myntra_data = page.evaluate('''() => {
        const results = [];
        const items = document.querySelectorAll('li.product-base');
        for (const item of items) {
            const a = item.querySelector('a');
            const img = item.querySelector('picture img, img');
            const brand = item.querySelector('h3.product-brand');
            const title = item.querySelector('h4.product-product');
            const price = item.querySelector('span.product-discountedPrice, span.product-price');
            const mrp = item.querySelector('span.product-strike');
            const disc = item.querySelector('span.product-discountPercentage');

            if (a && img && price) {
                results.push({
                    brand: brand ? brand.innerText.trim() : '',
                    title: (brand ? brand.innerText.trim() + ' ' : '') + (title ? title.innerText.trim() : ''),
                    link: a.href,
                    img: img.src,
                    price: price ? price.innerText.trim() : '',
                    mrp: mrp ? mrp.innerText.trim() : '',
                    disc: disc ? disc.innerText.trim() : ''
                });
            }
        }
        return results;
    }''')
    browser.close()
    
    with open('scripts/myntra_found.json', 'w', encoding='utf-8') as f:
        json.dump(myntra_data, f, indent=2, ensure_ascii=False)
    print(f"Myntra items found: {len(myntra_data)}")
