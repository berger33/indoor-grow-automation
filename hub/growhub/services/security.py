"""Autenticação local, perfis e sessões assinadas sem serviço externo."""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import IntEnum

from ..domain.sensors import IDENTIFIER


class UserRole(IntEnum):
    VIEWER = 1
    OPERATOR = 2
    ADMIN = 3


@dataclass(frozen=True, slots=True)
class UserAccount:
    user_id: str
    display_name: str
    role: UserRole
    password_hash: str
    enabled: bool = True


class PasswordHasher:
    iterations = 600_000

    def hash(self, password: str, *, salt: bytes | None = None) -> str:
        if len(password) < 12:
            raise ValueError("senha deve ter ao menos 12 caracteres")
        actual_salt = salt or os.urandom(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), actual_salt, self.iterations)
        return f"pbkdf2_sha256${self.iterations}${actual_salt.hex()}${digest.hex()}"

    def verify(self, password: str, encoded: str) -> bool:
        try:
            algorithm, raw_iterations, raw_salt, expected = encoded.split("$")
            if algorithm != "pbkdf2_sha256" or int(raw_iterations) != self.iterations:
                return False
            actual = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(raw_salt), self.iterations).hex()
        except (ValueError, TypeError):
            return False
        return hmac.compare_digest(actual, expected)


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


class AuthService:
    def __init__(self, signing_key: bytes, users: tuple[UserAccount, ...] = ()) -> None:
        if len(signing_key) < 32:
            raise ValueError("chave de sessão deve possuir ao menos 32 bytes")
        self._key = signing_key
        self._users = {user.user_id: user for user in users}
        self._hasher = PasswordHasher()

    def add_user(self, user_id: str, display_name: str, role: UserRole, password: str) -> UserAccount:
        if IDENTIFIER.fullmatch(user_id) is None or user_id in self._users or not display_name.strip():
            raise ValueError("usuário inválido ou duplicado")
        account = UserAccount(user_id, display_name, role, self._hasher.hash(password))
        self._users[user_id] = account
        return account

    def authenticate(self, user_id: str, password: str) -> UserAccount | None:
        account = self._users.get(user_id)
        if account is None or not account.enabled or not self._hasher.verify(password, account.password_hash):
            return None
        return account

    def issue(self, account: UserAccount, *, now: datetime, lifetime: timedelta = timedelta(hours=8)) -> str:
        if now.tzinfo is None or now.utcoffset() is None or lifetime <= timedelta(0):
            raise ValueError("sessão exige horário com timezone e duração positiva")
        payload = _encode(json.dumps({"sub": account.user_id, "role": int(account.role), "exp": int((now + lifetime).timestamp())}, separators=(",", ":")).encode())
        signature = _encode(hmac.new(self._key, payload.encode(), hashlib.sha256).digest())
        return f"{payload}.{signature}"

    def verify(self, token: str, *, now: datetime) -> UserAccount | None:
        try:
            payload, signature = token.split(".")
            expected = _encode(hmac.new(self._key, payload.encode(), hashlib.sha256).digest())
            if not hmac.compare_digest(signature, expected):
                return None
            data = json.loads(_decode(payload))
            account = self._users[data["sub"]]
            if now.tzinfo is None or now.utcoffset() is None:
                return None
            if int(data["exp"]) <= int(now.timestamp()) or int(data["role"]) != int(account.role):
                return None
            return account if account.enabled else None
        except (ValueError, KeyError, TypeError, binascii.Error, json.JSONDecodeError, UnicodeDecodeError):
            return None
