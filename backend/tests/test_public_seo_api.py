from fastapi.testclient import TestClient
from main import app
from db.database import SessionLocal
from db.models import Product, PlatformEnum, AvailabilityEnum

client = TestClient(app)

def test_public_product_endpoint_not_found():
    response = client.get("/api/products/public/non-existent-product-slug-xyz-random-123")
    assert response.status_code == 404
    assert "detail" in response.json()

def test_public_product_endpoint_success():
    db = SessionLocal()
    try:
        p = Product(
            id=9999,
            product_name="Apple iPhone 15 128GB Black",
            product_url="https://www.amazon.in/dp/B0CHX1W1XY",
            product_image="https://m.media-amazon.com/images/I/71657TiFeHL._SX679_.jpg",
            current_price=69999.0,
            original_price=79900.0,
            discount_percentage=12.0,
            platform=PlatformEnum.amazon,
            availability=AvailabilityEnum.in_stock,
            rating=4.6,
            review_count=1240,
        )
        db.merge(p)
        db.commit()

        # Call public endpoint with slug
        res = client.get("/api/products/public/apple-iphone-15-128gb-black")
        assert res.status_code == 200
        data = res.json()
        assert data["product"]["product_name"] == "Apple iPhone 15 128GB Black"
        assert data["product"]["current_price"] == 69999.0
        assert "priceping.store" in data["canonical_url"]
        assert "Price Ping" in data["meta_title"]
        assert "Price Ping" in data["meta_description"]
        assert isinstance(data["cross_store_offers"], list)
    finally:
        db.query(Product).filter(Product.id == 9999).delete()
        db.commit()
        db.close()
