from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import Api, abort

from data import db_session
from data.db_session import global_init
from data.user_model import User
from data.theme_model import Theme
from data.post_model import Post
from data.register import RegisterForm
from data.login import LoginForm
from data.change import ChangeForm

app = Flask(__name__)
api = Api(app)
global_init("db/Newgramm.db")
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def line():
    return render_template("line.html", title="Лента")


@app.route('/recommendations')
def recommendations():
    return render_template("recommendations.html", title="Рекомендации")


@app.route('/search')
def search():
    return render_template("search.html", title="Поиск")


@app.route('/profile')
def profile():
    return render_template("profile.html", title="Профиль")


@app.route('/profile/<int:id>')
def profile_user(id):
    return render_template("profile.html", title="Чужой профиль")


@app.route('/profile/change', methods=['GET', 'POST'])
def profile_change():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    list_ = []
    for i in user.themes:
        list_.append(str(i.id))
    form = ChangeForm(themes=list_)
    if request.method == "GET":
        form.name.data = user.name
        form.description.data = user.description
        form.age.data = user.age
        form.email.data = user.email
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        user.themes.clear()
        user.name = form.name.data
        user.description = form.description.data
        user.age = form.age.data
        user.email = form.email.data
        for i in form.themes.data:
            user.themes.append(db_sess.query(Theme).filter(Theme.id == i).first())
        db_sess.commit()
        return redirect('/')
    return render_template("register.html", title="Изменить профиль", form=form)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template("register.html", title="Регистрация", form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Register', form=form,
                                   message="Этот пользователь уже существует")
        user = User(
            name=form.name.data,
            description=form.description.data,
            age=form.age.data,
            email=form.email.data,
        )
        for i in form.themes.data:
            db_sess = db_session.create_session()
            user.themes.append(db_sess.query(Theme).filter(Theme.id == i).first())
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        login_user(user)
        return redirect('/')
    return render_template("register.html", title="Регистрация", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template("login.html", title="Вход", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/create_post')
def create_post():
    return render_template("create_post.html", title="Создать пост")


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
