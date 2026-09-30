import os
import uuid

from account_store import load_accounts, make_password_hash, save_accounts

TITLE = "Sign Up"

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ACCOUNTS_FILE = os.path.join(ROOT, "accounts.json")


def build():
    return {
        "headline": "Create your account",
        "subtext": "Register to save your shipping address and order details.",
    }


def handle(form):
    full_name = (form.get("full_name", "") or "").strip()
    email = (form.get("email", "") or "").strip().lower()
    password = (form.get("password", "") or "").strip()
    phone = (form.get("phone", "") or "").strip()
    address = (form.get("address", "") or "").strip()
    district = (form.get("district", "") or "").strip()
    province = (form.get("province", "") or "").strip()
    postal_code = (form.get("postal_code", "") or "").strip()

    if not full_name or not email or not password:
        return "กรุณากรอกชื่อ อีเมล และรหัสผ่านให้ครบ"

    if "@" not in email or "." not in email:
        return "รูปแบบอีเมลไม่ถูกต้อง"

    if len(password) < 6:
        return "รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร"

    accounts = load_accounts(ACCOUNTS_FILE)
    for account in accounts:
        saved_email = (account.get("email", "") or "").strip().casefold()
        if saved_email == email:
            return "อีเมลนี้มีคนสมัครแล้ว"

    accounts.append(
        {
            "user_id": uuid.uuid4().hex,
            "full_name": full_name,
            "email": email,
            "password_hash": make_password_hash(password),
            "phone": phone,
            "address": {
                "street": address,
                "district": district,
                "province": province,
                "postal_code": postal_code,
            },
            "created_at": "now",
        }
    )
    save_accounts(accounts, ACCOUNTS_FILE)
    return "สมัครสมาชิกสำเร็จ"
