"""pages/page2.py — product detail page for SAINT SINNER."""

import storage
import models
from pages import page1

TITLE = "Detail"


def build(query):
    items = storage.load()
    if not items:
        items = page1.default_products()
        storage.save(items)

    index = 0
    if "i" in query and query["i"].isdigit():
        index = int(query["i"])
    if index < 0:
        index = 0
    if index >= len(items):
        index = len(items) - 1

    item_number = 0
    for item in items:
        page1.prepare_product(item, item_number)
        item_number = item_number + 1
    storage.save(items)
    product = items[index]

    thumb_main = product.get("image", "/static/images/shirt1.jpg")
    thumbs = [thumb_main, "/static/images/shirt2.jpg", "/static/images/shirt3.jpg", "/static/images/shirt4.jpg"]
    if product.get("name") == "Chrome Reaper Tee":
        thumbs = [thumb_main, "/static/images/shirt2.jpg", "/static/images/shirt5.jpg", "/static/images/shirt6.jpg"]

    product_obj = models.Product(product["name"], product["price"], product.get("tag", "SAINT SINNER"), thumb_main)
    return {
        "product": product,
        "product_obj": product_obj,
        "description": product_obj.describe(),
        "gallery": thumbs,
        "index": index,
        "prev": index - 1 if index > 0 else None,
        "next": index + 1 if index < len(items) - 1 else None,
        "count": len(items),
    }


def handle(form):
    items = storage.load()
    action = form.get("action", "")
    no = form.get("no", "")

    if action not in ("add", "buy") or not no.isdigit():
        return "กรุณาเลือกสินค้า"

    index = int(no)
    if index < 0 or index >= len(items):
        return "ไม่พบสินค้า"

    item = items[index]
    item["picked"] = True
    item["qty"] = max(1, int(item.get("qty", 1)))
    storage.save(items)

    if action == "buy":
        return "✅ สินค้าถูกเพิ่มไปยังตะกร้าแล้ว"
    return "✅ เพิ่มในตะกร้าแล้ว"
