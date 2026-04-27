from dataclasses import dataclass
from typing import Optional

from .db import get_connection


ALLOWED_ROLES = {"Admin", "Manager", "User"}


@dataclass
class UserCreate:
    name: str
    identifier: str
    password_hash: str
    role: str
    two_fa_secret: str


def split_identifier(identifier: str) -> tuple[Optional[str], Optional[str]]:
    value = identifier.strip()
    if "@" in value:
        return value.lower(), None
    return None, value.lower()


def create_user(payload: UserCreate) -> int:
    email, username = split_identifier(payload.identifier)
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            INSERT INTO users (name, email, username, password_hash, role, two_fa_secret)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                payload.name.strip(),
                email,
                username,
                payload.password_hash,
                payload.role,
                payload.two_fa_secret,
            ),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def find_by_identifier(identifier: str):
    email, username = split_identifier(identifier)
    conn = get_connection()
    try:
        if email:
            row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        else:
            row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def find_by_id(user_id: int):
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
