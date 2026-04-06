"""Seed database with lab data. Run: python seed.py (from /app in Docker)."""

from app import create_app
from app.extensions import db
from app.models import (
    CartItem,
    Category,
    Coupon,
    Order,
    OrderItem,
    Payment,
    Product,
    Refund,
    Review,
    User,
)

MIN_PRODUCTS = 40


def _picsum(seed: str) -> str:
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in seed)[:80]
    return f"https://picsum.photos/seed/{safe}/400/300"


def _catalog_rows():
    """(category_slug, name, description, price, stock, seed_suffix)"""
    rows = []
    # Electronics
    elec = [
        ("Lab Laptop 15", "15-inch laptop for testing.", 999.99, 50),
        ("USB-C Hub 7-in-1", "Ports for every peripheral.", 49.99, 120),
        ("Wireless Mouse", "Ergonomic optical mouse.", 24.99, 300),
        ("Mechanical Keyboard", "RGB backlit switches.", 129.99, 80),
        ("4K Monitor 27in", "HDR-ready display.", 349.99, 40),
        ("Webcam HD Pro", "1080p video calls.", 89.99, 150),
        ("Noise-Canceling Headphones", "Over-ear Bluetooth.", 199.99, 90),
        ("Portable SSD 1TB", "USB 3.2 fast storage.", 119.99, 200),
        ("Smartphone Stand", "Adjustable aluminum.", 19.99, 500),
        ("Tablet 10in", "Android tablet for media.", 279.99, 60),
        ("Bluetooth Speaker", "Waterproof outdoor.", 79.99, 110),
        ("Power Bank 20000mAh", "Fast charge USB-C.", 45.99, 250),
        ("USB Flash Drive 128GB", "Metal casing keychain.", 14.99, 400),
        ("HDMI Cable 6ft", "4K-ready braided cable.", 9.99, 600),
    ]
    for i, (n, d, p, s) in enumerate(elec):
        rows.append(("electronics", n, d, p, s, f"elec-{i}"))
    # Books
    books = [
        ("Web Security 101", "Introduction to app security.", 29.99, 100),
        ("Python Cookbook", "Recipes for developers.", 44.99, 75),
        ("SQL Antipatterns", "Database design pitfalls.", 39.99, 60),
        ("The Tangled Web", "Browser security deep dive.", 34.99, 55),
        ("Cryptography Engineering", "Practical crypto.", 49.99, 40),
        ("Threat Modeling", "Design secure systems.", 42.99, 45),
        ("Bug Bounty Bootcamp", "Finding vulns responsibly.", 36.99, 90),
        ("Network Forensics", "Packets and analysis.", 51.99, 30),
    ]
    for i, (n, d, p, s) in enumerate(books):
        rows.append(("books", n, d, p, s, f"book-{i}"))
    # Home
    home = [
        ("Desk Lamp LED", "Dimmable warm light.", 35.99, 180),
        ("Coffee Maker", "12-cup programmable.", 89.99, 70),
        ("Air Purifier", "HEPA filter small room.", 159.99, 35),
        ("Throw Blanket", "Soft fleece 50x60.", 24.99, 220),
        ("Storage Bins Set", "Stackable 3-pack.", 32.99, 140),
        ("Wall Clock Silent", "12-inch modern.", 28.99, 95),
    ]
    for i, (n, d, p, s) in enumerate(home):
        rows.append(("home", n, d, p, s, f"home-{i}"))
    # Apparel
    apparel = [
        ("Cotton T-Shirt", "Unisex crew neck.", 18.99, 400),
        ("Hoodie Zip", "Fleece-lined winter.", 54.99, 150),
        ("Running Shoes", "Lightweight trainers.", 89.99, 85),
        ("Denim Jeans", "Slim fit classic.", 59.99, 120),
        ("Winter Jacket", "Water-resistant shell.", 129.99, 55),
        ("Baseball Cap", "Adjustable strap.", 16.99, 300),
    ]
    for i, (n, d, p, s) in enumerate(apparel):
        rows.append(("apparel", n, d, p, s, f"app-{i}"))
    # Sports
    sports = [
        ("Yoga Mat", "Non-slip 6mm.", 32.99, 160),
        ("Dumbbells Pair 10lb", "Neoprene coated.", 24.99, 90),
        ("Jump Rope", "Speed cable.", 12.99, 200),
        ("Water Bottle Insulated", "32oz stainless.", 22.99, 250),
        ("Resistance Bands Set", "5 levels.", 19.99, 175),
        ("Foam Roller", "Muscle recovery.", 27.99, 130),
    ]
    for i, (n, d, p, s) in enumerate(sports):
        rows.append(("sports", n, d, p, s, f"sport-{i}"))
    return rows


def _truncate_catalog():
    """Clear catalog-related tables so we can reinsert products (lab convenience)."""
    # Ordered deletes — TRUNCATE multi-table can fail on FK ordering; ORM is reliable here.
    Refund.query.delete(synchronize_session=False)
    Payment.query.delete(synchronize_session=False)
    OrderItem.query.delete(synchronize_session=False)
    Order.query.delete(synchronize_session=False)
    CartItem.query.delete(synchronize_session=False)
    Review.query.delete(synchronize_session=False)
    Product.query.delete(synchronize_session=False)
    Category.query.delete(synchronize_session=False)
    db.session.commit()


def seed_categories_and_products():
    cats = {}
    for slug, name in [
        ("electronics", "Electronics"),
        ("books", "Books"),
        ("home", "Home & Kitchen"),
        ("apparel", "Apparel"),
        ("sports", "Sports & Outdoors"),
    ]:
        c = Category(name=name, slug=slug)
        db.session.add(c)
        db.session.flush()
        cats[slug] = c.id

    for slug, name, desc, price, stock, suf in _catalog_rows():
        pid = cats[slug]
        seed = f"vulnshop-{slug}-{suf}"
        db.session.add(
            Product(
                category_id=pid,
                name=name,
                description=desc,
                price=price,
                stock=stock,
                image_url=_picsum(seed),
            )
        )
    db.session.commit()
    print(f"Catalog seeded: {Product.query.count()} products.")


def ensure_catalog():
    """Reseed catalog when below MIN_PRODUCTS (e.g. after adding Picsum URLs)."""
    n = Product.query.count()
    if n >= MIN_PRODUCTS:
        return
    print(f"Catalog has {n} products (minimum {MIN_PRODUCTS}); refreshing catalog tables…")
    _truncate_catalog()
    seed_categories_and_products()


def seed_users_and_coupons():
    if User.query.filter_by(email="admin@lab.local").first():
        return False
    coupons = [
        Coupon(code="WELCOME10", discount_percent=10, max_uses=1000, stackable=True),
        Coupon(code="LAB50", discount_percent=50, max_uses=5, stackable=True),
    ]
    db.session.add_all(coupons)
    admin = User(
        email="admin@lab.local",
        full_name="Lab Admin",
        role="admin",
    )
    admin.set_password("admin123")
    user = User(
        email="user@lab.local",
        full_name="Lab User",
        role="user",
    )
    user.set_password("UserPass123!")
    staging = User(
        email="staging@lab.local",
        full_name="Staging",
        role="user",
    )
    staging.set_password("staging")
    db.session.add_all([admin, user, staging])
    db.session.commit()
    print("Users and coupons seeded.")
    return True


def run():
    app = create_app()
    with app.app_context():
        fresh = seed_users_and_coupons()
        if fresh:
            seed_categories_and_products()
        else:
            ensure_catalog()


if __name__ == "__main__":
    run()
