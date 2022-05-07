from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from .models import User


auth = Blueprint('auth', __name__)


def check_user_login(user, password):
    """проверка формы авторизации пользователя.
    в качестве результата работы функции возвращаем сообщение,
    которое может содержать в себе три значения:
    user(пользователь в будущем не сможет решать проблемы),
    admin(пользователь является организацией, которая сможет решать проблемы)
    и сообщение об ошибке(пользователь ввел неверный пароль).
    вариант с несуществующим аккаунтом проверяется до входа в функцию проверки."""
    if check_password_hash(user.password, password):
        login_user(user, remember=True)
        if not user.isAdmin:
            return "user"
        else:
            return "admin"
    return "Неверный пароль. Попробуйте ещё раз."


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        """заранее устанавливаем переменной message сообщение о том,
        что аккаунта с данной почтой не существует."""
        message = "Пользователь не найден."
        if user:
            message = check_user_login(user, password)
            if message == "user":
                return redirect(url_for('views.home'))
            if message == "admin":
                return redirect(url_for('views.admin'))
        """в качестве ошибки передаем в html-файл значение переменной message."""
        return render_template("login.html", user=current_user, message=message)
    return render_template("login.html", user=current_user, message='')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.index'))


def check_user_sign_up(user, email, first_name, password1, password2):
    """проверка формы регистрации пользователя.
    в качестве результата работы функции возвращаем сообщение,
    которое может содержать в себе шесть значений:
    пять видов ошибок(таких как длина почты, пароля и тп)
    и строку "ok", которая означает, что данные, введеные пользователем,
    подходят для создания аккаунта."""
    if user:
        return "Пользователь с такой почтой уже существует."
    elif len(email) < 4:
        return "Логин должен иметь более 3 символов."
    elif len(first_name) < 2:
        return "Имя должно иметь более 1 символа."
    elif password1 != password2:
        return "Пароли не совпадают."
    elif len(password1) < 7:
        return "Пароль должен иметь как минимум 7 символов."
    return "ok"


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        isAdmin = request.form.get('isAdmin')
        if isAdmin:
            isAdmin = True
        else:
            isAdmin = False
        user = User.query.filter_by(email=email).first()
        message = check_user_sign_up(user, email, first_name, password1, password2)
        if message == "ok":
            """создание нового аккаунта, на основе данных, введеных пользователем.
            пароль хэшируем методом sha256."""
            new_user = User(email=email,
                            password=generate_password_hash(password1, method='sha256'),
                            first_name=first_name,
                            last_name=last_name,
                            isAdmin=isAdmin,
                            ban=False)
            """добавляем новый аккаунт в базу данных."""
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            return redirect(url_for('views.home'))
        else:
            return render_template("sign_up.html", user=current_user, message=message)
    return render_template("sign_up.html", user=current_user, message='')
