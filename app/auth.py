import base64
import io
import time 
import bcrypt
import jwt
import pyotp
import qrcode
from flask import Blueprint, current_app, jsonify, request
from sqlite3 import IntegrityError

from .security import decode_token, generate_token
from .user_model import (
    ALLOWED_ROLES, UserCreate, create_user, 
    find_by_id, find_by_identifier, update_last_2fa
)

auth_bp = Blueprint("auth", __name__)

def _json_required_fields(data: dict, required: list[str]):
    missing = [field for field in required if not data.get(field)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400
    return None

@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    missing = _json_required_fields(data, ["name", "identifier", "password", "role"])
    if missing: return missing

    role = data["role"].strip()
    if role not in ALLOWED_ROLES: return jsonify({"error": "Invalid role"}), 400

    pwd_hash = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    secret = pyotp.random_base32()
    
    try:
        user_id = create_user(UserCreate(data["name"], data["identifier"], pwd_hash, role, secret))
    except IntegrityError:
        return jsonify({"error": "User already exists"}), 409

    uri = pyotp.totp.TOTP(secret).provisioning_uri(name=data["identifier"], issuer_name="SecureAuth")
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    qr_url = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

    return jsonify({"qrCodeDataUrl": qr_url, "manualSecret": secret}), 201

@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    user = find_by_identifier(data.get("identifier", ""))
    if not user or not bcrypt.checkpw(data.get("password", "").encode("utf-8"), user["password_hash"].encode("utf-8")):
        return jsonify({"error": "Invalid credentials"}), 401

    temp_token = generate_token({"sub": str(user["id"]), "stage": "2fa"}, 60, "temp")
    return jsonify({"message": "Proceed to 2FA", "tempToken": temp_token})

@auth_bp.post("/verify-2fa")
def verify_2fa():
    data = request.get_json(silent=True) or {}
    try:
        payload = decode_token(data.get("tempToken", ""))
    except: return jsonify({"error": "Invalid token"}), 401

    user = find_by_id(int(payload["sub"]))
    if not user: return jsonify({"error": "User not found"}), 404

    totp = pyotp.TOTP(user["two_fa_secret"])
    current_step = int(time.time() / 30)

    # valid_window=0 يمنع الكود من العمل بمجرد تغيره في تطبيق Google Auth
    if not totp.verify(str(data["code"]).strip(), valid_window=0):
        return jsonify({"error": "Code expired or invalid"}), 401

    # حماية من التكرار (Replay Protection) في نفس الـ 30 ثانية
    if user.get("last_2fa_at") is not None and int(user["last_2fa_at"]) >= current_step:
        return jsonify({"error": "Code already used. Wait 30 seconds."}), 401

    update_last_2fa(user["id"], current_step)

    token = generate_token({"sub": str(user["id"]), "name": user["name"], "role": user["role"]}, 3600, "access")
    return jsonify({"accessToken": token, "user": {"name": user["name"], "role": user["role"]}})