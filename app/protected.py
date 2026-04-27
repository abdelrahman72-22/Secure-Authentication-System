from flask import Blueprint, jsonify, request

from .security import role_required, token_required


protected_bp = Blueprint("protected", __name__)


@protected_bp.get("/dashboard")
@token_required
def dashboard():
    user = request.user
    return jsonify({"message": f"Welcome to dashboard, {user['name']}", "user": user})


@protected_bp.get("/profile")
@token_required
def profile():
    user = request.user
    return jsonify({"message": "Profile data", "profile": user})


@protected_bp.get("/admin")
@token_required
@role_required("Admin")
def admin():
    return jsonify({"message": "Admin-only content"})


@protected_bp.get("/manager")
@token_required
@role_required("Manager")
def manager():
    return jsonify({"message": "Manager-only content"})


@protected_bp.get("/user")
@token_required
@role_required("User")
def user_page():
    return jsonify({"message": "User-only content"})
