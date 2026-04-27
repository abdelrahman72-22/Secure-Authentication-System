import time
from functools import wraps

import jwt
from flask import current_app, jsonify, request


def _extract_token() -> str | None:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    return auth_header.split(" ", 1)[1].strip()


def generate_token(payload: dict, expires_in: int, token_type: str) -> str:
    now = int(time.time())
    data = {
        **payload,
        "iat": now,
        "exp": now + expires_in,
        "typ": token_type,
    }
    return jwt.encode(data, current_app.config["JWT_SECRET"], algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=["HS256"])


def token_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        token = _extract_token()
        if not token:
            return jsonify({"error": "Missing bearer token"}), 401

        try:
            payload = decode_token(token)
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid or expired token"}), 401

        if payload.get("typ") != "access":
            return jsonify({"error": "Wrong token type"}), 401

        request.user = payload
        return view(*args, **kwargs)

    return wrapper


def role_required(*allowed_roles: str):
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            user = getattr(request, "user", None)
            if not user:
                return jsonify({"error": "Not authenticated"}), 401
            if user.get("role") not in allowed_roles:
                return jsonify({"error": "Forbidden: insufficient role"}), 403
            return view(*args, **kwargs)

        return wrapper

    return decorator
