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
                return redirect(url_for('root'))
        else:
            flash('ログインが完了していません。ログインしてください。','danger')
            return redirect(url_for('login'))
    return decorated_function

def check_oa(func):
    @wraps(func)
    def decorated_function(*arg, **kwargs):
        student_id = session.get('student_id')
        if "logged-in" in session:
            if check_role(student_id) == "oa" or check_role(student_id) == "admin":
                return func(*arg, **kwargs)
            else:
                flash('管理者アカウントでログインしてください','danger')
                return redirect(url_for('root'))
        else:
            flash('ログインが完了していません。ログインしてください。','danger')
            return redirect(url_for('login'))
    return decorated_function

# role
def check_role(student_id):
    if student_id == "###":
        return "admin"
    # trial_release ではここで認証済みユーザーのアクセスだけを許可する
    f = open('users_oa.txt', 'r', encoding='UTF-8')
    auth_users = f.readlines()
    f.close()
    authenticated = False
    for auth_user in auth_users:
        if auth_user == f'{student_id}\n'or auth_user == student_id:
            authenticated = True
            break
    
    if authenticated:
        return "oa"
    else:
        return "student"