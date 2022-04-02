import datetime
import os

from PIL import Image
from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import Api, abort
from werkzeug.utils import secure_filename

from data import db_session
from data.db_session import global_init
from data.user_model import User
from data.theme_model import Theme
from data.post_model import Post
from data.register import RegisterForm
from data.login import LoginForm
from data.change import ChangeForm
from data.create_post import PostForm

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
    db_sess = db_session.create_session()
    num_posts = len(db_sess.query(Post).filter(Post.user_id == current_user.id).all())
    num_subscriptions = len(current_user.subscriptions.split(',')) - 1
    num_subscribers = len(current_user.subscribers.split(',')) - 1
    posts = db_sess.query(Post).filter(Post.user_id == current_user.id).all()
    num_likes = {post.id: len(post.likes.split(',')) - 1 for post in posts}
    return render_template("profile.html", title="Профиль", num_posts=num_posts, num_subscriptions=num_subscriptions,
                           num_subscribers=num_subscribers, posts=posts, likes=num_likes)


@app.route('/profile/<int:id>')
def profile_user(id):
    if id == current_user.id:
        return redirect('/profile')
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
        f = form.image.data
        if f:
            f.save(os.path.join(app.root_path, 'static', 'img', 'users', f'{user.id}.jpg'))
        db_sess.commit()
        return redirect('/')
    return render_template("register.html", title="Изменить профиль", form=form, image=f'/img/users/{ current_user.id}.jpg')


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
        user.subscriptions = ''
        user.subscribers = ''

        for i in form.themes.data:
            db_sess = db_session.create_session()
            user.themes.append(db_sess.query(Theme).filter(Theme.id == i).first())
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        f = form.image.data
        f.save(os.path.join(app.root_path, 'static', 'img', 'users', f'{user.id}.jpg'))
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
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template("login.html", title="Вход", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/delconfim_user')
def delconfirm_user():
    return render_template("delete.html", text=f"Нажмите сюда чтобы полностью и "
                                               f"безвозвратно удалить профиль {current_user.name}",
                           title='Подтверждение', link='/', go='/delete_user', image=f'/img/users/{ current_user.id}.jpg')


@app.route('/delconfim_post/<int:id>', methods=['GET', 'POST'])
def delconfirm_post(id):
    return render_template("delete.html", text=f"Нажмите сюда, чтобы полностью и безвозвратно удалить выбранный пост",
                           title='Подтверждение', link=f'/post_view/{id}',
                           go=f'/delete_post/{id}', image=f'/img/users/{ current_user.id}.jpg')


@app.route('/delete_user')
def delete():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    logout_user()
    db_sess.delete(user)
    db_sess.commit()
    return redirect('/')


@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post()
        post.user_id = current_user.id
        post.publication_date = datetime.datetime.now()
        post.likes = ''
        post.description = form.description.data
        db_sess = db_session.create_session()
        for i in form.themes.data:
            db_sess = db_session.create_session()
            post.themes.append(db_sess.query(Theme).filter(Theme.id == i).first())
        db_sess.add(post)
        db_sess.commit()
        f = form.image.data
        f.save(os.path.join(app.root_path, 'static', 'img', 'posts', f'{post.id}.jpg'))
        db_sess.commit()
        return redirect('/')
    return render_template("create_post.html", title="Создать пост", form=form)


@app.route('/change_post/<int:id>', methods=['GET', 'POST'])
def post_change(id):
    db_sess = db_session.create_session()
    post = db_sess.query(Post).filter(Post.id == id).first()
    list_ = []
    for i in post.themes:
        list_.append(str(i.id))
    form = PostForm(themes=list_)
    if request.method == "GET":
        form.description.data = post.description
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        post = db_sess.query(Post).filter(Post.id == id).first()
        post.description = form.description.data
        post.themes.clear()
        for i in form.themes.data:
            post.themes.append(db_sess.query(Theme).filter(Theme.id == i).first())
        f = form.image.data
        if f:
            f.save(os.path.join(app.root_path, 'static', 'img', 'posts', f'{post.id}.jpg'))
        db_sess.commit()
        return redirect(f'/post_view/{post.id}')
    return render_template("create_post.html", title="Изменить пост", form=form, change=True, post=post)


@app.route('/delete_post/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    post = db_sess.query(Post).filter(Post.id == id, Post.user_id == current_user.id).first()
    if post:
        db_sess.delete(post)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/post_find/<int:id>/<string:where>')
def post_find(id, where):
    db_sess = db_session.create_session()
    post = db_sess.query(Post).filter(Post.id == id).first()
    user = db_sess.query(User).filter(post.user_id == User.id).first()
    posts_user = db_sess.query(Post).filter(Post.user_id == user.id).all()
    if where == "next":
        new_id = posts_user[posts_user.index(post) + 1].id
    else:
        new_id = posts_user[posts_user.index(post) - 1].id
    return redirect(f'/post_view/{new_id}')


@app.route('/post_view/<int:id>')
def post_view(id):
    db_sess = db_session.create_session()
    post = db_sess.query(Post).filter(Post.id == id).first()
    img = f'/img/posts/{post.id}.jpg'
    user = db_sess.query(User).filter(User.id == post.user_id).first()
    posts_user = db_sess.query(Post).filter(Post.user_id == user.id).all()
    Previous = True
    Next = True
    if posts_user.index(post) == 0:
        Previous = False
    if posts_user.index(post) == len(posts_user) - 1:
        Next = False
    num_likes = len(post.likes.split(',')) - 1
    return render_template("post.html", title="Просмотр поста", post=post, image_post=img,
                           image=f'/img/users/{ current_user.id}.jpg', user=user, likes=num_likes, next=Next,
                           prev=Previous)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
