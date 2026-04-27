import base64
import io

import bcrypt
import jwt
import pyotp
import qrcode
from flask import Blueprint, current_app, jsonify, request
from sqlite3 import IntegrityError

from .security import decode_token, generate_token
from .user_model import ALLOWED_ROLES, UserCreate, create_user, find_by_id, find_by_identifier


auth_bp = Blueprint("auth", __name__)


def _json_required_fields(data: dict, required: list[str]):
    missing = [field for field in required if not data.get(field)]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400
    return None


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    missing_response = _json_required_fields(data, ["name", "identifier", "password", "role"])
    if missing_response:
        return missing_response

    role = data["role"].strip()
    if role not in ALLOWED_ROLES:
        return jsonify({"error": "Invalid role. Allowed roles: Admin, Manager, User"}), 400

    password_hash = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    totp_secret = pyotp.random_base32()
    try:
        user_id = create_user(
            UserCreate(
                name=data["name"],
                identifier=data["identifier"],
                password_hash=password_hash,
                role=role,
                two_fa_secret=totp_secret,
            )
        )
    except IntegrityError:
        return jsonify({"error": "Email/username already exists"}), 409

    otp_uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(
        name=data["identifier"], issuer_name="DI Project Auth"
    )
    image = qrcode.make(otp_uri)
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="PNG")
    qr_data_url = "data:image/png;base64," + base64.b64encode(image_bytes.getvalue()).decode("ascii")

    return (
        jsonify(
            {
                "message": "Registration successful. Scan the QR code to enable 2FA.",
                "userId": user_id,
                "qrCodeDataUrl": qr_data_url,
                "manualSecret": totp_secret,
            }
        ),
        201,
    )


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    missing_response = _json_required_fields(data, ["identifier", "password"])
    if missing_response:
        return missing_response

    user = find_by_identifier(data["identifier"])
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    if not bcrypt.checkpw(data["password"].encode("utf-8"), user["password_hash"].encode("utf-8")):
        return jsonify({"error": "Invalid credentials"}), 401

    temp_token = generate_token(
        payload={"sub": str(user["id"]), "stage": "2fa"},
        expires_in=current_app.config["TEMP_TOKEN_EXPIRES_SECONDS"],
        token_type="temp",
    )

    return jsonify(
        {
            "message": "Password verified. Submit your 2FA code.",
            "tempToken": temp_token,
        }
    )


@auth_bp.post("/verify-2fa")
def verify_2fa():
    data = request.get_json(silent=True) or {}
    missing_response = _json_required_fields(data, ["tempToken", "code"])
    if missing_response:
        return missing_response

    try:
        payload = decode_token(data["tempToken"])
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid or expired temporary token"}), 401

    if payload.get("typ") != "temp" or payload.get("stage") != "2fa":
        return jsonify({"error": "Invalid token stage"}), 401

    user = find_by_id(int(payload["sub"]))
    if not user:
        return jsonify({"error": "User not found"}), 404

    valid = pyotp.TOTP(user["two_fa_secret"]).verify(str(data["code"]).strip(), valid_window=1)
    if not valid:
        return jsonify({"error": "Invalid 2FA code"}), 401

    access_token = generate_token(
        payload={"sub": str(user["id"]), "name": user["name"], "role": user["role"]},
        expires_in=current_app.config["JWT_EXPIRES_SECONDS"],
        token_type="access",
    )

    return jsonify(
        {
            "message": "Authentication successful",
            "accessToken": access_token,
            "user": {"id": user["id"], "name": user["name"], "role": user["role"]},
        }
    )
