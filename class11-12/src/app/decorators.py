from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash("You need admin privileges to access this page.", "error")
            return redirect(url_for("main.dashboard"))
        return f(*args, **kwargs)
    return decorated_function


def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_teacher():
            flash("You need teacher privileges to access this page.", "error")
            return redirect(url_for("main.dashboard"))
        return f(*args, **kwargs)
    return decorated_function


def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_student():
            flash("You need student privileges to access this page.", "error")
            return redirect(url_for("main.dashboard"))
        return f(*args, **kwargs)
    return decorated_function


def admin_or_teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or (not current_user.is_admin() and not current_user.is_teacher()):
            flash("You need admin or teacher privileges to access this page.", "error")
            return redirect(url_for("main.dashboard"))
        return f(*args, **kwargs)
    return decorated_function
