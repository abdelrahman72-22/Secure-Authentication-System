from flask import Blueprint, redirect, render_template


pages_bp = Blueprint("pages", __name__)


@pages_bp.get("/")
def root():
    return redirect("/login")


@pages_bp.get("/register")
def register_page():
    return render_template("register.html")


@pages_bp.get("/login")
def login_page():
    return render_template("login.html")


@pages_bp.get("/verify-2fa")
def verify_2fa_page():
    return render_template("verify_2fa.html")


@pages_bp.get("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")


@pages_bp.get("/profile")
def profile_page():
    return render_template("profile.html")


@pages_bp.get("/admin")
def admin_page():
    return render_template("admin.html")


@pages_bp.get("/manager")
def manager_page():
    return render_template("manager.html")


@pages_bp.get("/user")
def user_page():
    return render_template("user.html")
