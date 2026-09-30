import json

import app as webapp

def test_signup_and_signin_flow(tmp_path, monkeypatch):
    accounts_file = tmp_path / "accounts.json"
    session_file = tmp_path / "session.json"
    original_load_page = webapp.load_page

    def load_page_with_test_files(name):
        module, error = original_load_page(name)
        if module is not None and name == "signup":
            module.ACCOUNTS_FILE = str(accounts_file)
        elif module is not None and name == "signin":
            module.ACCOUNTS_FILE = str(accounts_file)
            module.SESSION_FILE = str(session_file)
        return module, error

    monkeypatch.setattr(webapp, "load_page", load_page_with_test_files)
    client = webapp.app.test_client()

    signup = client.post(
        "/signup",
        data={
            "full_name": "สมชาย ใจดี",
            "email": "somchai@example.com",
            "password": "123456",
            "phone": "0812345678",
            "address": "123/45",
            "district": "เมือง",
            "province": "อุบลราชธานี",
            "postal_code": "34000",
        },
        follow_redirects=True,
    )
    signup_text = signup.data.decode("utf-8")
    assert signup.status_code == 200
    assert "สมัครสมาชิกสำเร็จ" in signup_text or "Sign up" in signup_text

    with open(accounts_file, encoding="utf-8") as f:
        accounts = json.load(f)
    assert len(accounts) == 1
    assert accounts[0]["email"] == "somchai@example.com"

    signin = client.post(
        "/signin",
        data={
            "email": "somchai@example.com",
            "password": "123456",
        },
        follow_redirects=True,
    )
    signin_text = signin.data.decode("utf-8")
    assert signin.status_code == 200
    assert "เข้าสู่ระบบสำเร็จ" in signin_text or "Sign in" in signin_text

    with open(session_file, encoding="utf-8") as f:
        session = json.load(f)
    assert session["email"] == "somchai@example.com"
