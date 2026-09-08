from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=['--disable-http2']
    )
    page = browser.new_page(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    )
    try:
        page.goto('https://www.nykaa.com', timeout=15000)
        print("Nykaa Title with --disable-http2:", page.title())
    except Exception as e:
        print("Nykaa failed:", e)
    browser.close()
