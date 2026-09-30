import json
import os
import uuid

from account_store import load_accounts, make_password_hash, password_matches, save_accounts
from pages.page3 import load_orders

TITLE = "Sign In"

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ACCOUNTS_FILE = os.path.join(ROOT, "accounts.json")
SESSION_FILE = os.path.join(ROOT, "session.json")


def load_session():
    if not os.path.exists(SESSION_FILE):
        return {}
    with open(SESSION_FILE, encoding="utf-8") as f:
        try:
            data = json.load(f)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass
    return {}


def save_session(data):
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def find_session_account(session, accounts):
    if not session.get("logged_in"):
        return None

    user_id = session.get("user_id", "")
    session_email = (session.get("email", "") or "").strip().casefold()
    for account in accounts:
        saved_email = (account.get("email", "") or "").strip().casefold()
        if user_id and account.get("user_id") == user_id:
            return account
        if not user_id and session_email and saved_email == session_email:
            return account
    return None


def build(query=None):
    if query is None:
        query = {}
    session = load_session()
    account = find_session_account(session, load_accounts(ACCOUNTS_FILE))
    if account is None:
        return {"logged_in": False, "user_name": "", "user_email": "", "user_initial": ""}

    user_name = account.get("full_name", "")
    address = account.get("address", {})
    tracking_code = (query.get("tracking_code", "") or "").strip().upper()
    tracking_order = None
    if tracking_code:
        for order in load_orders():
            if str(order.get("tracking_code", "")).upper() == tracking_code:
                tracking_order = order
                break
    return {
        "logged_in": True,
        "editing_profile": query.get("edit", "") == "1",
        "user_name": user_name,
        "user_email": account.get("email", ""),
        "user_initial": user_name.strip()[:1] or "?",
        "phone": account.get("phone", ""),
        "street": address.get("street", ""),
        "district": address.get("district", ""),
        "province": address.get("province", ""),
        "postal_code": address.get("postal_code", ""),
        "tracking_code": tracking_code,
        "tracking_order": tracking_order,
    }


def handle(form):
    action = form.get("action", "")
    if action == "logout":
        save_session({})
        return "ออกจากระบบแล้ว"
    if action == "switch_account":
        save_session({})
        return "ออกจากบัญชีเดิมแล้ว กรุณาเข้าสู่ระบบด้วยบัญชีอื่น"

    if action == "update_profile":
        session = load_session()
        accounts = load_accounts(ACCOUNTS_FILE)
        account = find_session_account(session, accounts)
        if account is None:
            save_session({})
            return "กรุณาเข้าสู่ระบบก่อนแก้ไขโปรไฟล์"

        full_name = (form.get("full_name", "") or "").strip()
        email = (form.get("email", "") or "").strip().casefold()
        if not full_name or not email:
            return "กรุณากรอกชื่อและอีเมลให้ครบ"
        if "@" not in email or "." not in email:
            return "รูปแบบอีเมลไม่ถูกต้อง"
        for other in accounts:
            if other is account:
                continue
            other_email = (other.get("email", "") or "").strip().casefold()
            if other_email == email:
                return "อีเมลนี้มีบัญชีอื่นใช้แล้ว"

        account["full_name"] = full_name
        account["email"] = email
        account["phone"] = (form.get("phone", "") or "").strip()
        account["address"] = {
            "street": (form.get("street", "") or "").strip(),
            "district": (form.get("district", "") or "").strip(),
            "province": (form.get("province", "") or "").strip(),
            "postal_code": (form.get("postal_code", "") or "").strip(),
        }
        save_accounts(accounts, ACCOUNTS_FILE)
        session["email"] = email
        session["full_name"] = full_name
        session["address"] = account["address"]
        save_session(session)
        return "บันทึกโปรไฟล์แล้ว"

    identifier = (form.get("identifier", "") or form.get("email", "") or "").strip()
    password = (form.get("password", "") or "").strip()

    if not identifier or not password:
        return "กรุณากรอกชื่อบัญชีหรืออีเมล และรหัสผ่าน"

    accounts = load_accounts(ACCOUNTS_FILE)
    identifier_key = identifier.casefold()
    matches = []
    for account in accounts:
        email = (account.get("email", "") or "").strip().casefold()
        full_name = (account.get("full_name", "") or "").strip().casefold()
        if identifier_key == email or identifier_key == full_name:
            if password_matches(account, password):
                matches.append(account)

    if len(matches) > 1 and "@" not in identifier:
        return "ชื่อบัญชีนี้ซ้ำกัน กรุณาใช้อีเมลเข้าสู่ระบบ"
    if not matches:
        return "ชื่อบัญชี อีเมล หรือรหัสผ่านไม่ถูกต้อง"

    account = matches[0]
    if "password_hash" not in account:
        account["password_hash"] = make_password_hash(password)
        account.pop("password", None)
    if not account.get("user_id"):
        account["user_id"] = uuid.uuid4().hex
    save_accounts(accounts, ACCOUNTS_FILE)
    save_session(
        {
            "logged_in": True,
            "user_id": account["user_id"],
            "email": account.get("email", ""),
            "full_name": account.get("full_name", ""),
            "address": account.get("address", {}),
        }
    )
    return "เข้าสู่ระบบสำเร็จ"
