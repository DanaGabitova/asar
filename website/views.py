from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from .models import Note, User
from . import db


views = Blueprint('views', __name__)


@views.route('/')
def index():
    return render_template('index.html', user=current_user)


@views.route('/admin')
@login_required
def admin():
    notes = []
    for note in Note.query.all():
        notes.append(note.data)
    return render_template('admin.html', user=current_user, notes=notes)


@views.route('/home')
@login_required
def home():
    notes = []
    for note in Note.query.all():
        notes.append(note.data)
    return render_template('home.html', user=current_user, notes=notes)


def check_task_show(photo):
    if not photo:
        return "Вставьте фотографию в качестве доказательства."
    if not photo.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        return "Вставьте файл формата фотографии."
    return "ok"


@views.route('/show_task')
@login_required
def show_task():
    photo = request.form.get('description')
    message = check_task_show(photo)
    if message == "ok":
        return render_template('show_task.html', user=current_user, message=message)
    return render_template('show_task.html', user=current_user, message='')


def check_task_send(description, coordinates):
    if len(coordinates) == 0:
        return 'Введите координаты.'
    if len(description) == 0:
        return 'Введите проблему.'
    return "ok"


@views.route('/send_task', methods=['GET', 'POST'])
@login_required
def send_task():
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
    return render_template('contacts.html', user=current_user)


@views.route('/contacts-login')
def contacts_login():
    return render_template('contacts-login.html', user=current_user)


@views.route('/users_list', methods=['GET', 'POST'])
def users_list():
    users = []
    for user in User.query.all():
        users.append(user.first_name)
    if request.method == 'POST':
        pass
    return render_template('users_list.html', user=current_user, users=users)
