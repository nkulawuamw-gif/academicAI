import pytest
from app.core.security import hash_password, verify_password, create_access_token, decode_token


def test_password_hashing():
    password = "test_password_123"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)


def test_access_token():
    data = {"sub": "test_user_id", "role": "student"}
    token = create_access_token(data)
    decoded = decode_token(token)
    assert decoded["sub"] == "test_user_id"
    assert decoded["role"] == "student"
    assert "exp" in decoded


def test_invalid_token():
    decoded = decode_token("invalid_token_here")
    assert decoded is None
