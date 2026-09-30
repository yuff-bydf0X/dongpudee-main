"""pages/page1.py — SAINT SINNER storefront catalog."""

import storage

TITLE = "Shop"


def default_products():
    return [
        {
            "name": "GU",
            "category": "Hoodie",
            "price": 390,
            "tag": "HAND-PAINTED",
            "sizes": ["S", "M", "L", "XL", "XXL"],
            "image": "/static/images/shirt1.jpg",
            "picked": False,
            "qty": 1,
        },
        {
            "name": "Uniqlo",
            "category": "Hoodie",
            "price": 590,
            "tag": "SAINT SINNER",
            "sizes": ["S", "M", "L", "XL", "XXL"],
            "image": "/static/images/shirt2.jpg",
            "picked": False,
            "qty": 1,
        },
        {
            "name": "Uniqlo",
            "category": "Hoodie",
            "price": 490,
            "tag": "FULL PATTERN",
            "sizes": ["S", "M", "L", "XL", "XXL"],
            "image": "/static/images/shirt3.jpg",
            "picked": False,
            "qty": 1,
        },
        {
            "name": "Skull",
            "category": "T-shirt",
            "price": 390,
            "tag": "LIMITED DROP",
            "sizes": ["S", "M", "L", "XL", "XXL"],
            "image": "/static/images/shirt4.jpg",
            "picked": False,
            "qty": 1,
        },
        {
            "name": "Uniqlo",
            "category": "Hoodie",
            "price": 490,
            "tag": "CYBERPUNK",
            "sizes": ["S", "M", "L", "XL", "XXL"],
            "image": "/static/images/shirt5.jpg",
            "picked": False,
            "qty": 1,
        },
        {
            "name": "Uniqlo",
            "category": "Hoodie",
            "price": 390,
            "tag": "NEW SEASON",
            "sizes": ["S", "M", "L", "XL", "XXL"],
            "image": "/static/images/shirt6.jpg",
            "picked": False,
            "qty": 1,
        },
    ]


def prepare_product(item, index):
    if not item.get("sizes"):
        item["sizes"] = ["S", "M", "L", "XL", "XXL"]
    if not item.get("image"):
        item["image"] = "/static/images/shirt1.jpg"
    if not item.get("tag"):
        item["tag"] = "SAINT SINNER"
    if "picked" not in item:
        item["picked"] = False
    item["qty"] = max(1, int(item.get("qty", 1)))
    item["no"] = index
    item["price_label"] = "฿" + str(item.get("price", 0))
    item["short_tag"] = item.get("tag", "SAINT SINNER")
    return item


def filter_products(products, query):
    keyword = query.get("q", "").strip().lower()
    category = query.get("category", "").strip().lower()
    size = query.get("size", "").strip().upper()
    minimum = query.get("min_price", "").strip()
    maximum = query.get("max_price", "").strip()
    try:
        minimum = int(minimum) if minimum else None
    except ValueError:
        minimum = None
    try:
        maximum = int(maximum) if maximum else None
    except ValueError:
        maximum = None

    results = []
    for item in products:
        name = item.get("name", "").lower()
        item_category = item.get("category", "").lower()
        price = int(item.get("price", 0))
        if keyword and keyword not in name:
            continue
        if category and category != item_category:
            continue
        if size and size not in item.get("sizes", []):
            continue
        if minimum is not None and price < minimum:
            continue
        if maximum is not None and price > maximum:
            continue
        results.append(item)
    return results


def sort_products(products, sort_by):
    remaining = list(products)
    ordered = []
    while len(remaining) > 0:
        best = remaining[0]
        for item in remaining:
            price = int(item.get("price", 0))
            best_price = int(best.get("price", 0))
            sales = int(item.get("sold_count", 0))
            best_sales = int(best.get("sold_count", 0))
            if sort_by == "price_asc" and price < best_price:
                best = item
            elif sort_by == "price_desc" and price > best_price:
                best = item
            elif sort_by == "latest":
                item_date = item.get("created_at", "")
                best_date = best.get("created_at", "")
                if item_date > best_date or (item_date == best_date and item["no"] > best["no"]):
                    best = item
            elif sort_by == "best_selling" and sales > best_sales:
                best = item
        ordered.append(best)
        remaining.remove(best)
    return ordered


def build(query):
    items = storage.load()
    if not items:
        items = default_products()
        storage.save(items)

    products = []
    index = 0
    for item in items:
        products.append(prepare_product(item, index))
        index = index + 1

    storage.save(items)

    categories = ["เสื้อ", "หมวก"]
    sizes = []
    for item in products:
        for size in item["sizes"]:
            if size not in sizes:
                sizes.append(size)

    sort_by = query.get("sort", "latest")
    if sort_by not in ("price_asc", "price_desc", "latest", "best_selling"):
        sort_by = "latest"
    results = sort_products(filter_products(products, query), sort_by)

    return {
        "products": results,
        "count": len(items),
        "result_count": len(results),
        "keyword": query.get("q", ""),
        "selected_category": query.get("category", ""),
        "selected_size": query.get("size", ""),
        "min_price": query.get("min_price", ""),
        "max_price": query.get("max_price", ""),
        "sort_by": sort_by,
        "categories": categories,
        "sizes": sizes,
        "hero_title": "SAINT SINNER",
        "hero_text": "Streetwear for the after-hours crowd.",
    }


def handle(form):
    items = storage.load()
    action = form.get("action", "")
    no = form.get("no", "")

    if action not in ("add", "buy") or not no.isdigit():
        return "กรุณาเลือกสินค้า"

    index = int(no)
    if index < 0 or index >= len(items):
        return "ไม่พบสินค้าในคอลเลกชัน"

    item = items[index]
    item["picked"] = True
    item["qty"] = max(1, int(item.get("qty", 1)))
    storage.save(items)

    if action == "buy":
        return "✅ ใส่ตะกร้าแล้ว พร้อมชำระเงิน"
    return "✅ เพิ่มสินค้าในตะกร้าแล้ว"
