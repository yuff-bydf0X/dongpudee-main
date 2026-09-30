"""Read and write the local account file and verify account passwords."""

import hashlib
import hmac
import json
import secrets

PASSWORD_ITERATIONS = 240000


def load_accounts(path):
    try:
        with open(path, encoding="utf-8") as f:
            accounts = json.load(f)
    except (OSError, json.JSONDecodeError):
        return []
    if isinstance(accounts, list):
        return accounts
    return []


def save_accounts(accounts, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(accounts, f, ensure_ascii=False, indent=2)


def make_password_hash(password):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), PASSWORD_ITERATIONS
    )
    return "pbkdf2_sha256${}${}${}".format(
        PASSWORD_ITERATIONS, salt, digest.hex()
    )


def password_matches(account, password):
    stored_hash = account.get("password_hash", "")
    if not stored_hash:
        old_password = str(account.get("password", ""))
        return hmac.compare_digest(
            old_password.encode("utf-8"), password.encode("utf-8")
        )

    try:
        algorithm, iterations, salt, expected = stored_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt), int(iterations)
        )
    except (TypeError, ValueError):
        return False
    return hmac.compare_digest(digest.hex(), expected)