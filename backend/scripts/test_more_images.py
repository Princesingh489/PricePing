import requests

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
})

test_items = [
    # MYNTRA
    ('myntra', 'Libas Women Beige Kurta Set', 'https://assets.myntassets.com/h_720,q_90,w_540/v1/assets/images/10356511/2025/3/8/de31ac55-3742-4947-b32f-70f22ca038671741419318444-Libas-Women-Beige-Ethnic-Print-Straight-Kurta-Set-With-Side--1.jpg'),
    ('myntra', 'BROADSTAR Men Korean Pants', 'https://assets.myntassets.com/h_720,q_90,w_540/v1/assets/images/2025/SEPTEMBER/15/kwAmpR9a_e5ce9f1ae80a42a18a0b800355ee6680.jpg'),
    ('myntra', 'BROADSTAR Men Smart Trousers', 'https://assets.myntassets.com/h_720,q_90,w_540/v1/assets/images/2025/DECEMBER/15/TMHSBRde_668dfa1d30474de8844d05ac5b7315dd.jpg'),
    ('myntra', 'Koskii Women Embroidered Dress', 'https://assets.myntassets.com/h_720,q_90,w_540/v1/assets/images/2024/SEPTEMBER/4/6Il7NVwN_55f57a0ba9e342fb9a2ed0facda1d907.jpg'),
    ('myntra', 'Anouk Women Printed Kurta', 'https://assets.myntassets.com/h_720,q_90,w_540/v1/assets/images/11715910/2020/4/8/1e62a1aa-2144-469b-bfa3-fcf3b2a2aa431586326162357-Anouk-Women-Pink--Gold-Toned-Printed-Straight-Kurta-8151586326-1.jpg'),
    ('myntra', 'Kalini Women Bandhani Kurta', 'https://assets.myntassets.com/h_720,q_90,w_540/v1/assets/images/17926838/2022/4/19/27177519-74d6-47e2-8ea5-6b5825d1e6781650361099641-KALINI-Women-Kurta-Sets-971650361099197-1.jpg'),
    ('myntra', 'Sangria Women Floral Print Dress', 'https://assets.myntassets.com/h_720,q_90,w_540/v1/assets/images/13642398/2021/3/17/8009b2e2-636c-4860-bd70-36a5fae58f001615967676773-Sangria-Women-Kurtas-7161615967675713-1.jpg'),
    ('myntra', 'Varanga Women Embroidered Kurta', 'https://assets.myntassets.com/h_720,q_90,w_540/v1/assets/images/10856112/2019/11/5/c54b2d35-3769-42ec-84f9-ea9a0a1a0b381572948633363-Varanga-Women-Kurtas-351572948631481-1.jpg'),

    # NYKAA
    ('nykaa', 'Vaseline Deep Moisture Lotion', 'https://images-static.nykaa.com/media/catalog/product/tr:h-800,w-800,cm-pad_resize/0/2/029e0788901030769443_1.jpg'),
    ('nykaa', 'Nykaa Cosmetics Liquid Lipstick', 'https://images-static.nykaa.com/media/catalog/product/8/9/8904245704179_1.jpg'),
    ('nykaa', 'Maybelline Superstay Matte Ink', 'https://images-static.nykaa.com/media/catalog/product/0/4/041554496468_1.jpg'),
    ('nykaa', 'Biotique Morning Nectar Lotion', 'https://images-static.nykaa.com/media/catalog/product/8/9/8906009450070_1.jpg'),
    ('nykaa', 'Nykaa Wanderlust Body Butter', 'https://images-static.nykaa.com/media/catalog/product/8/9/8904245710644_1.jpg'),
    ('nykaa', 'Mamaearth Ubtan Face Wash', 'https://images-static.nykaa.com/media/catalog/product/8/9/8906087772437_1.jpg'),
    ('nykaa', 'L\'Oreal Paris Total Repair Shampoo', 'https://images-static.nykaa.com/media/catalog/product/8/9/8901526002166_1.jpg'),
    ('nykaa', 'Kay Beauty Matte Lipstick', 'https://images-static.nykaa.com/media/catalog/product/8/9/8904320701024_1.jpg'),

    # AJIO
    ('ajio', 'POINT COVE Boys Patterned Cotton Shirt', 'https://assets.ajio.com/medias/sys_master/root1/20260312/fdWQ/69b2bc5a4970ce6a6e3efa1f/-473Wx593H-443666961-olive-MODEL.jpg'),
    ('ajio', 'Avaasa Fusion Women Floral Straight Kurta', 'https://assets.ajio.com/medias/sys_master/root/20230624/eWq9/64969248d55b7d0c6396b2ae/-473Wx593H-441129379-black-MODEL.jpg'),
    ('ajio', 'Gulmohar Jaipur Women Printed Kurta', 'https://assets.ajio.com/medias/sys_master/root/20230620/q5eZ/64917454d55b7d0c6375eb0b/-473Wx593H-441112890-maroon-MODEL.jpg'),
]

print("Testing image URLs...")
for store, name, url in test_items:
    try:
        r = session.get(url, stream=True, timeout=3)
        print(f"[{r.status_code}] {store:8} | {name:32} | {url[:65]}")
    except Exception as e:
        print(f"[ERR] {store:8} | {name:32} | {e}")
