from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user, AnonymousUserMixin

from .models import Note, User
from . import db


views = Blueprint('views', __name__)


@views.route('/')
def index():
    """
    главная страница для всех
    незарегистрированных пользователей.
    """

    return render_template('index.html', user=current_user)


@views.route('/about')
def about():
    """страница с картой с проблемами."""

    return render_template('about.html', user=current_user)


@views.route('/admin')
@login_required
def admin():
    """
    страница для админов
    на ней можно увидеть заявки, отправленные
    всеми пользователями и всех пользователей.
    """

    if current_user.isAdmin:
        notes = []
        for note in Note.query.all():
            notes.append(note.description)
        return render_template('admin.html', user=current_user, notes=notes)
    return redirect(url_for('.home'))


@views.route('/home')
@login_required
def home():
    """
    главная страница для всех
    зарегистрированных пользователей.
    """

    notes = []
    for note in Note.query.all():
        notes.append(note.description)
    return render_template('home.html', user=current_user, notes=notes)


def check_task_show(photo, task_id, notes):
    """
    функция для проверки формы
    для решения проблемы.
    """

    if not photo:
        return "Вставьте фотографию в качестве доказательства."
    if not photo.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        return "Вставьте файл формата фотографии."
    if not task_id <= len(notes):
        return "Введите id проблемы корректно."
    return "ok"


@views.route('/show_task', methods=['GET', 'POST'])
@login_required
def show_task():
    """
    страница для показа всех проблем и отправки
    формы для их решений для админов.
    """

    full_notes = []
    notes = []
    """
    массивы для полного списка проблем(notes)
    и для описаний и статуса проблем().
    """

    for note in Note.query.all():
        full_notes.append(note)
        notes.append([note.description, note.status])

    if request.method == 'POST':
        photo = request.form.get('photo')
        task_id = int(request.form.get('task-id'))
        message = check_task_show(photo, task_id, notes)
        if message == "ok":
            note = full_notes[task_id - 1]
            updated_note = note
            updated_note.status = 'pending'
            db.session.delete(note)
            db.session.add(updated_note)
            db.session.commit()
            return render_template('show_task.html', user=current_user, notes=notes, message='',
                                   isAdmin=current_user.isAdmin)
        return render_template('show_task.html', user=current_user, notes=notes, message=message,
                               isAdmin=current_user.isAdmin)
    return render_template('show_task.html', user=current_user, notes=notes, message='', isAdmin=current_user.isAdmin)


def check_task_send(description, coordinates):
    """
    функция для проверки формы
    для отправки проблемы.
    """

    if len(coordinates) == 0:
        return 'Введите координаты.'
    if len(description) == 0:
        return 'Введите проблему.'
    return "ok"


@views.route('/send_task', methods=['GET', 'POST'])
@login_required
def send_task():
    """страница для отправки проблемы."""

    if request.method == 'POST':
        description = request.form.get('description')
        coordinates = request.form.get('coordinates')
        message = check_task_send(description, coordinates)
        if message == "ok":
            new_note = Note(coordinates=coordinates, description=description, status='In progress',
                            user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            return redirect(url_for('views.home'))
        return render_template('send_task.html', user=current_user, message=message)
    return render_template('send_task.html', user=current_user, message='')


@views.route('/contacts')
def contacts():
    """страница для показа контактов для
    незарегистрированных пользователей."""

    return render_template('contacts.html', user=current_user)


@views.route('/contacts-login')
def contacts_login():
    """страница для показа контактов для
    зарегистрированных пользователей."""

    return render_template('contacts-login.html', user=current_user)


@views.route('/users_list', methods=['GET', 'POST'])
def users_list():
    """страница со списком всех пользователей для админов."""

    if isinstance(current_user, AnonymousUserMixin):
        return redirect(url_for('.index'))
    if current_user.isAdmin:
        users = []
        for user in User.query.all():
            users.append(user.first_name)
        return render_template('users_list.html', user=current_user, users=users)
    return redirect(url_for('.home'))
