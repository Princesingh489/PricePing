import json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    )
    try:
        page.goto('https://www.ajio.com/s/clothing-4461-74581?query=%3Arelevance%3Adiscountflag%3Atrue', timeout=18000)
        page.wait_for_timeout(3000)
        print("AJIO Title:", page.title())
        
        items = page.evaluate('''() => {
            const results = [];
            const cards = document.querySelectorAll('div.item, div.rilrtl-products-list__item');
            for (const c of cards) {
                const a = c.querySelector('a');
                const img = c.querySelector('img');
                const brand = c.querySelector('.brand');
                const name = c.querySelector('.nameCls');
                const price = c.querySelector('.price');
                const org = c.querySelector('.orginal-price');
                const disc = c.querySelector('.discount');
                if (a && img && price) {
                    results.push({
                        title: (brand ? brand.innerText + ' ' : '') + (name ? name.innerText : ''),
                        link: a.href,
                        img: img.src,
                        price: price.innerText,
                        mrp: org ? org.innerText : '',
                        disc: disc ? disc.innerText : ''
                    });
                }
            }
            return results;
        }''')
        print("AJIO items found:", len(items))
        with open('scripts/ajio_found.json', 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("AJIO err:", e)
    browser.close()
