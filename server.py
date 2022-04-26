from flask import Flask, render_template, redirect
from loginform import LoginForm
from registrationform import RegistrationForm


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect('/home')
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        return redirect('/home')
    return render_template('signup.html', form=form)

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)
