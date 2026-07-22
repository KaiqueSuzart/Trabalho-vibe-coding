from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models import User, db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username, active=True).first()
        if not user or not user.check_password(password):
            flash("Usuário ou senha inválidos.", "danger")
            return render_template("login.html")

        session.clear()
        session["user_id"] = user.id
        session["user_name"] = user.name
        session["role"] = user.role
        flash(f"Bem-vindo(a), {user.name}!", "success")

        if user.role == "lojista":
            return redirect(url_for("admin.dashboard"))
        if user.role == "garcom":
            return redirect(url_for("waiter.dashboard"))
        return redirect(url_for("public.home"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Sessão encerrada.", "info")
    return redirect(url_for("public.home"))
