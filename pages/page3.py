"""pages/page3.py — shopping cart summary."""

import json
import os
import random
from datetime import datetime

import storage

TITLE = "Cart"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORDERS_FILE = os.path.join(ROOT, "orders.json")


def load_orders():
    try:
        with open(ORDERS_FILE, encoding="utf-8") as f:
            orders = json.load(f)
    except (OSError, json.JSONDecodeError):
        return []
    if isinstance(orders, list):
        return orders
    return []


def save_orders(orders):
    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)


def build(query=None):
    if query is None:
        query = {}

    items = storage.load()
    picked = []
    count = 0
    subtotal = 0

    index = 0
    for item in items:
        item["no"] = index
        index = index + 1
        if item.get("picked", False):
            qty = max(1, int(item.get("qty", 1)))
            item["qty"] = qty
            picked.append(item)
            count = count + qty
            subtotal = subtotal + qty * int(item.get("price", 0))

    shipping = 0
    if subtotal > 0 and subtotal < 2500:
        shipping = 120
    elif subtotal >= 2500:
        shipping = 0

    total = subtotal + shipping
    checkout_open = str(query.get("checkout", "")).strip().lower() in ("1", "true", "yes")
    tracking_query = query.get("track", "").strip().upper()
    tracking_order = None
    if tracking_query:
        for order in load_orders():
            if str(order.get("tracking_code", "")).upper() == tracking_query:
                tracking_order = order
                break

    return {
        "items": picked,
        "count": count,
        "subtotal": subtotal,
        "shipping": shipping,
        "total": total,
        "checkout_open": checkout_open,
        "tracking_query": tracking_query,
        "tracking_order": tracking_order,
    }


def handle(form):
    items = storage.load()
    action = form.get("action", "")
    no = form.get("no", "")

    if action == "pay":
        order_items = []
        subtotal = 0
        for item in items:
            if item.get("picked", False):
                qty = max(1, int(item.get("qty", 1)))
                price = int(item.get("price", 0))
                order_items.append({
                    "name": item.get("name", ""),
                    "category": item.get("category", ""),
                    "qty": qty,
                    "price": price,
                })
                subtotal = subtotal + qty * price
        if not order_items:
            return "ไม่มีสินค้าในตะกร้า"

        shipping = 120 if subtotal < 2500 else 0
        orders = load_orders()
        duplicate_code = True
        tracking_code = ""
        while duplicate_code:
            tracking_code = "PK" + str(random.randint(10000000, 99999999))
            duplicate_code = False
            for order in orders:
                if order.get("tracking_code") == tracking_code:
                    duplicate_code = True
                    break

        orders.append({
            "tracking_code": tracking_code,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": "กำลังเตรียมจัดส่ง",
            "items": order_items,
            "subtotal": subtotal,
            "shipping": shipping,
            "total": subtotal + shipping,
        })
        save_orders(orders)
        for item in items:
            item["picked"] = False
            item["qty"] = 1
        storage.save(items)
        return "ชำระเงินทดลองสำเร็จ เลขพัสดุของคุณคือ " + tracking_code

    if action == "clear":
        for item in items:
            item["picked"] = False
            item["qty"] = 1
        storage.save(items)
        return "ล้างตะกร้าแล้ว"

    if action in ("remove", "plus", "minus") and no.isdigit():
        index = int(no)
        if 0 <= index < len(items):
            item = items[index]
            if action == "remove":
                item["picked"] = False
                item["qty"] = 1
                storage.save(items)
                return "เอาสินค้าออกจากตะกร้าแล้ว"
            qty = max(1, int(item.get("qty", 1)))
            if action == "plus":
                qty = qty + 1
            elif action == "minus" and qty > 1:
                qty = qty - 1
            item["qty"] = qty
            storage.save(items)
            return "อัปเดตจำนวนสินค้าแล้ว"

    return "ไม่เข้าใจคำสั่ง"
