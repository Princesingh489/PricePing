import json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    )
    page.goto('https://www.flipkart.com/search?q=smartwatch', timeout=20000)
    page.wait_for_timeout(3000)
    
    # Get all elements with data-id or all links with /p/
    data = page.evaluate('''() => {
        const results = [];
        const items = document.querySelectorAll('div[data-id]');
        for (const item of items) {
            const a = item.querySelector('a[href*="/p/"]');
            const img = item.querySelector('img');
            const text = item.innerText;
            if (a && img) {
                results.push({
                    dataId: item.getAttribute('data-id'),
                    link: a.href,
                    img: img.src,
                    alt: img.alt,
                    text: text.slice(0, 200)
                });
            }
        }
        return results;
    }''')
    browser.close()
    
    with open('scripts/flipkart_found.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Items found: {len(data)}")
