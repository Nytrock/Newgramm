import datetime
import os

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
from data.create_post import PostForm
from data.sorting import SortForm
from data.API import user_resources
from data.API import post_resources

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
    t = 0
    postt2 = []
    db_sess = db_session.create_session()
    posts = db_sess.query(Post).all()
    user = db_sess.query(User).get(current_user.id)
    sub = user.subscriptions.split(',')[:-1]
    for post in posts:
        subss = post.user_id
        if str(subss) in sub:
            postt2.append(post)
        post.user = db_sess.query(User).get(post.user_id)
        post.get_likes = len(post.likes.split(',')) - 1
        post.like = str(user.id) in post.likes.split(',')
        t += 1
    return render_template("line.html", title="Лента", posts=postt2, line=True)


@app.route('/recommendations')
def recommendations():
    db_sess = db_session.create_session()
    posts = db_sess.query(Post).all()
    user = db_sess.query(User).get(current_user.id)
    user_tags = set(map(lambda x: x.id, user.themes))
    for post in posts:
        tags = set(map(lambda x: x.id, post.themes))
        post.connection = len(user_tags) - len(list(user_tags - tags))
        post.user = db_sess.query(User).get(post.user_id)
        post.get_likes = len(post.likes.split(',')) - 1
        post.like = str(user.id) in post.likes.split(',')
    posts.sort(key=lambda x: x.connection, reverse=True)
    return render_template("recommendations.html", title="Рекомендации", posts=posts, recommend=True)


@app.route('/search')
def search():
    return render_template("search.html", title="Поиск", search=True)


@app.route('/profile')
def profile():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        num_subscriptions = len(current_user.subscriptions.split(',')) - 1
        num_subscribers = len(current_user.subscribers.split(',')) - 1
        posts = db_sess.query(Post).filter(Post.user_id == current_user.id).all()
        num_likes = {post.id: len(post.likes.split(',')) - 1 for post in posts}
        return render_template("profile.html", title="Профиль", num_subscriptions=num_subscriptions,
                               num_subscribers=num_subscribers, posts=posts, likes=num_likes, user=user)
    return render_template("profile.html", title="Профиль")


@app.route('/profile/<int:id>')
def profile_user(id):
    if current_user.is_authenticated:
        if id == current_user.id:
            return redirect('/profile')
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    num_subscriptions = len(user.subscriptions.split(',')) - 1
    num_subscribers = len(user.subscribers.split(',')) - 1
    posts = db_sess.query(Post).filter(Post.user_id == id).all()
    num_likes = {post.id: len(post.likes.split(',')) - 1 for post in posts}
    me_subscribe = current_user.is_authenticated
    if me_subscribe:
        me_subscribe = f"{current_user.id}" not in user.subscribers.split(',')
    if current_user.is_authenticated:
        return render_template("profile.html", title="Чужой профиль", num_subscriptions=num_subscriptions,
                               num_subscribers=num_subscribers, posts=posts, likes=num_likes, user=user,
                               image=f'/img/users/{current_user.id}.jpg', user_image=f'/img/users/{user.id}.jpg',
                               show_button=me_subscribe)
    return render_template("profile.html", title="Чужой профиль", num_subscriptions=num_subscriptions,
                           num_subscribers=num_subscribers, posts=posts, likes=num_likes, user=user,
                           user_image=f'/img/users/{user.id}.jpg')


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
    return render_template("register.html", title="Изменить профиль", form=form,
                           image=f'/img/users/{current_user.id}.jpg', change=True)


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
                           title='Подтверждение', link='/', go='/delete_user',
                           image=f'/img/users/{current_user.id}.jpg')


@app.route('/delconfim_post/<int:id>', methods=['GET', 'POST'])
def delconfirm_post(id):
    return render_template("delete.html", text=f"Нажмите сюда, чтобы полностью и безвозвратно удалить выбранный пост",
                           title='Подтверждение', link=f'/post_view/{id}',
                           go=f'/delete_post/{id}', image=f'/img/users/{current_user.id}.jpg')


@app.route('/delete_user')
def delete():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    logout_user()
    for i in user.subscribers.split(','):
        if i != '':
            sub = db_sess.query(User).get(int(i))
            list_ = sub.subscriptions.split(',')
            list_.remove(str(user.id))
            sub.subscriptions = ','.join(list_)
            db_sess.commit()
    for i in user.subscriptions.split(','):
        if i != '':
            sub = db_sess.query(User).get(int(i))
            list_ = sub.subscribers.split(',')
            list_.remove(str(user.id))
            sub.subscribers = ','.join(list_)
            db_sess.commit()
    posts = db_sess.query(Post).filter(Post.user_id == current_user.id)
    for post in posts:
        os.remove(os.path.join(app.root_path, 'static', 'img', 'posts', f'{post.id}.jpg'))
        db_sess.delete(post)
    db_sess.delete(user)
    db_sess.commit()
    os.remove(os.path.join(app.root_path, 'static', 'img', 'users', f'{user.id}.jpg'))
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
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        user.number_of_posts += 1
        db_sess.commit()
        return redirect('/')
    return render_template("create_post.html", title="Создать пост", form=form, create=True)


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
        os.remove(os.path.join(app.root_path, 'static', 'img', 'posts', f'{post.id}.jpg'))
        db_sess.delete(post)
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        user.number_of_posts -= 1
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
    Like = False
    if posts_user.index(post) == 0:
        Previous = False
    if posts_user.index(post) == len(posts_user) - 1:
        Next = False
    if str(current_user.id) in post.likes.split(','):
        Like = True
    num_likes = len(post.likes.split(',')) - 1
    me_subscribe = f"{current_user.id}" not in user.subscribers.split(',')
    date = post.publication_date
    today = datetime.datetime.now()
    yesterday = post.publication_date - datetime.timedelta(days=1)
    if date.year == today.year and date.month == today.month and date.day == today.day:
        show_date = "Сегодня " + date.strftime("%H:%M")
    elif date.year == yesterday.year and date.month == yesterday.month and date.day == yesterday.day:
        show_date = "Вчера " + date.strftime("%H:%M")
    else:
        show_date = date.strftime("%d %B %H:%M")

    return render_template("post.html", title="Просмотр поста", post=post, image_post=img,
                           image=f'/img/users/{current_user.id}.jpg', user_image=f'/img/users/{user.id}.jpg',
                           user=user, likes=num_likes, next=Next, like=Like,
                           prev=Previous, show_button=me_subscribe, show_date=show_date)


@app.route('/like/<int:id>')
def like(id):
    db_sess = db_session.create_session()
    post = db_sess.query(Post).filter(Post.id == id).first()
    if str(current_user.id) in post.likes.split(','):
        post.likes = post.likes.replace(f'{str(current_user.id)},', '')
    else:
        post.likes += f'{current_user.id},'
    db_sess.commit()
    return redirect(f'/post_view/{id}')


@app.route('/subscribe/<string:typ>/<int:id>')
def subscribe(typ, id):
    db_sess = db_session.create_session()
    if typ == "profile":
        user = db_sess.query(User).get(id)
    elif typ == "post":
        post = db_sess.query(Post).get(id)
        user = db_sess.query(User).get(post.user_id)
    me = db_sess.query(User).get(current_user.id)
    if f"{me.id}" not in user.subscribers.split(','):
        me.subscriptions += f'{user.id},'
        user.subscribers += f'{me.id},'
    else:
        me.subscriptions = me.subscriptions.replace(f'{user.id},', '')
        user.subscribers = user.subscribers.replace(f'{me.id},', '')
    db_sess.commit()
    if typ == "profile":
        return redirect(f'/profile/{id}')
    return redirect(f'/post_view/{post.id}')


@app.route('/subscribe-from-subs/<string:typ>/<int:from_id>/<int:id>')
def subscribe_subs(typ, from_id, id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(id)
    me = db_sess.query(User).get(current_user.id)
    if f"{me.id}" not in user.subscribers.split(','):
        me.subscriptions += f'{user.id},'
        user.subscribers += f'{me.id},'
    else:
        me.subscriptions = me.subscriptions.replace(f'{user.id},', '')
        user.subscribers = user.subscribers.replace(f'{me.id},', '')
    db_sess.commit()
    if typ == "subscribers":
        return redirect(f"/view_users/{ from_id }/subscribers")
    return redirect(f'/view_users/{ from_id }/subscriptions')


@app.route('/view_users/<int:id>/<string:typ>', methods=['GET', 'POST'])
def view_users(id, typ):

    db_sess = db_session.create_session()
    form = SortForm(sorting=0)
    form.sorting.choices = [(0, "Не выбрано"), (1, "По имени"), (2, "По возрасту"), (3, "По кол-ву подписчиков"),
                             (4, "По кол-ву подписок")]
    user = db_sess.query(User).get(id)
    other = current_user.id != id
    sl = {"subscribers": f"Подписчики {user.name}",
          "subscriptions": f"Подписки {user.name}"}
    users = []
    if typ == "subscribers":
        for i in user.subscribers.split(","):
            if i != '':
                users.append(db_sess.query(User).get(int(i)))
    else:
        for i in user.subscriptions.split(","):
            if i != '':
                users.append(db_sess.query(User).get(int(i)))
    if request.method == 'POST':
        if form.sorting.data == 1:
            users.sort(key=lambda x: x.name)
        elif form.sorting.data == 2:
            users.sort(key=lambda x: x.age, reverse=True)
        elif form.sorting.data == 3:
            users.sort(key=lambda x: len(x.subscribers.split(',')))
        elif form.sorting.data == 3:
            users.sort(key=lambda x: len(x.subscriptions.split(',')))
    name = sl[typ]
    for i in users:
        i.sub = str(i.id) in current_user.subscriptions.split(',')
    return render_template("subscribers.html", title=name, users=users,
                           image=f'/img/users/{current_user.id}.jpg', view=user, type=typ, other=other, form=form)


if __name__ == '__main__':
    api.add_resource(user_resources.UsersListResource, '/api/users')
    api.add_resource(user_resources.UsersResource, '/api/users/<int:user_id>')
    api.add_resource(user_resources.UsersDelete, '/api/users/<int:user_id>/<string:password>')

    api.add_resource(post_resources.PostsListResource, '/api/posts')
    api.add_resource(post_resources.PostsResource, '/api/posts/<int:post_id>')
    api.add_resource(post_resources.PostsDelete, '/api/posts/<int:post_id>/<string:password>')

    app.run(port=8080, host='127.0.0.1')
