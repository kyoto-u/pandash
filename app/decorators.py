from functools import wraps
from flask import flash, session, redirect, url_for

def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # if "logged-in" in session:
        studnet_id = session.get('student_id')
        if studnet_id:
            return func(*args, **kwargs)
        else:
            flash('ログインが完了していません。ログインしてください。','danger')
            return redirect(url_for('login'))
    return decorated_function

def check_admin(func):
    @wraps(func)
    def decorated_function(*arg, **kwargs):
        student_id = session.get('student_id')
        if "logged-in" in session:
            if check_role(student_id) == "admin":
                return func(*arg, **kwargs)
            else:
                flash('管理者アカウントでログインしてください','danger')
                return redirect(url_for('home'))
        else:
            flash('ログインが完了していません。ログインしてください。','danger')
            return redirect(url_for('login'))
    return decorated_function

def check_oa(func):
    @wraps(func)
    def decorated_function(*arg, **kwargs):
        student_id = session.get('student_id')
        if "logged-in" in session:
            if check_role(student_id) == "oa" or "admin":
                return func(*arg, **kwargs)
            else:
                flash('管理者アカウントでログインしてください','danger')
                return redirect(url_for('home'))
        else:
            flash('ログインが完了していません。ログインしてください。','danger')
            return redirect(url_for('login'))
    return decorated_function

# role
def check_role(student_id):
    if student_id == "###":
        return "admin"
    else:
        return "student"