import datetime
import os

from flask import Flask
from flask import render_template, redirect, request
from flask_login import LoginManager
from flask_login import login_user, login_required, logout_user, current_user
from flask_restful import Api
from flask_restful import abort

from data import db_session
from data.API import user_resources, post_resources, comment_resources
from data.db_session import global_init
from data.user_model import User


def create_app():
    app = Flask(__name__)
    api = Api(app)
    app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
    file_path = os.path.join(app.root_path, 'db', 'NewGramm.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + file_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PROPAGATE_EXCEPTIONS'] = True
    global_init(file_path)
    login_manager = LoginManager()
    login_manager.init_app(app)
    api.add_resource(user_resources.UsersListResource, '/api/users')
    api.add_resource(user_resources.UsersResource, '/api/users/<int:user_id>')
    api.add_resource(user_resources.UsersDelete, '/api/users/<int:user_id>/<string:password>')

    api.add_resource(post_resources.PostsListResource, '/api/posts')
    api.add_resource(post_resources.PostsResource, '/api/posts/<int:post_id>')
    api.add_resource(post_resources.PostsDelete, '/api/posts/<int:post_id>/<string:password>')

    api.add_resource(comment_resources.CommentsListResource, '/api/comments')
    api.add_resource(comment_resources.CommentsResource, '/api/comments/<int:comment_id>')
    api.add_resource(comment_resources.CommentsDelete, '/api/comments/<int:comment_id>/<string:password>')

    @login_manager.user_loader
    def load_user(user_id):
        db_sess = db_session.create_session()
        return db_sess.query(User).get(user_id)

    return app

app = create_app()

from data.comment_model import Comment
from data.create_post import PostForm
from data.login import LoginForm
from data.post_model import Post
from data.register import RegisterForm
from data.change import ChangeForm
from data.search import SearchForm
from data.sorting import SortForm
from data.theme_model import Theme



def make_line():
    final_posts = []
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.id)
    user_subs = user.subscriptions.split(',')
    posts = db_sess.query(Post).filter(Post.user_id != current_user.id).all()
    for post in posts:
        another = db_sess.query(User).get(post.user_id)
        if str(another.id) in user_subs:
            post.user = db_sess.query(User).get(post.user_id)
            post.get_likes = len(post.likes.split(',')) - 1
            post.like = str(user.id) in post.likes.split(',')
            date = post.publication_date
            today = datetime.datetime.now()
            yesterday = today - datetime.timedelta(days=1)
            if date.year == today.year and date.month == today.month and date.day == today.day:
                post.date = "Сегодня " + date.strftime("%H:%M")
            elif date.year == yesterday.year and date.month == yesterday.month and date.day == yesterday.day:
                post.date = "Вчера " + date.strftime("%H:%M")
            else:
                post.date = date.strftime("%d %B %H:%M")
            comments = db_sess.query(Comment).filter(Comment.post_id == post.id).all()
            post.com = len(comments)
            final_posts.append(post)
    final_posts.sort(key=lambda x: x.publication_date, reverse=True)
    return final_posts


@app.route('/', methods=['GET', 'POST'])
def line():
    form = SortForm()
    form.sorting.choices = [(0, "Не выбрано"), (1, "По дате выкладывания"), (2, "По популярности")]
    if current_user.is_authenticated:
        posts = make_line()
    else:
        posts = []

    if request.method == 'POST':
        if form.sorting.data == 1:
            posts.sort(key=lambda x: x.publication_date, reverse=True)
        elif form.sorting.data == 2:
            posts.sort(key=lambda x: len(x.likes.split(',')), reverse=True)
    return render_template("line.html", title="Лента", line=True, posts=posts, form=form)


@app.route('/line_view/<int:id>', methods=['POST', 'GET'])
def line_view(id):
    posts = list(map(lambda x: x.id, make_line()))
    db_sess = db_session.create_session()
    sorting = SortForm()
    sorting.sorting.choices = [(0, "Не выбрано"), (1, "Сначала новые"), (2, "Сначала старые")]
    if request.method == "POST":
        if request.form.get("comment") != '' and request.form.get("comment") is not None:
            new_comment = Comment()
            new_comment.user_id = current_user.id
            new_comment.post_id = id
            new_comment.text = request.form.get("comment")
            new_comment.create_date = datetime.datetime.now()
            db_sess.add(new_comment)
            db_sess.commit()

    post = db_sess.query(Post).get(id)
    index = posts.index(id)
    user = db_sess.query(User).filter(User.id == post.user_id).first()
    Previous = index != 0
    Next = index != len(posts) - 1
    Like = str(current_user.id) in post.likes.split(',')
    num_likes = len(post.likes.split(',')) - 1
    me_subscribe = f"{current_user.id}" not in user.subscribers.split(',')
    date = post.publication_date
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    if date.year == today.year and date.month == today.month and date.day == today.day:
        show_date = "Сегодня " + date.strftime("%H:%M")
    elif date.year == yesterday.year and date.month == yesterday.month and date.day == yesterday.day:
        show_date = "Вчера " + date.strftime("%H:%M")
    else:
        show_date = date.strftime("%d %B %H:%M")
    final_comments = []
    if post.enable_comments:
        comments = db_sess.query(Comment).filter(Comment.post_id == post.id)
        for comment in comments:
            comment.user = db_sess.query(User).get(comment.user_id)
            date = comment.create_date
            if date.year == today.year and date.month == today.month and date.day == today.day:
                comment.show_date = "Сегодня " + date.strftime("%H:%M")
            elif date.year == yesterday.year and date.month == yesterday.month and date.day == yesterday.day:
                comment.show_date = "Вчера " + date.strftime("%H:%M")
            else:
                comment.show_date = date.strftime("%d %B %H:%M")
            final_comments.append(comment)

    if request.method == "POST":
        if sorting.sorting.data == 1:
            final_comments.sort(key=lambda x: x.create_date, reverse=True)
        elif sorting.sorting.data == 2:
            final_comments.sort(key=lambda x: x.create_date)

    return render_template("post.html", title="Просмотр поста", post=post, like=Like,
                           user=user, likes=num_likes, next=Next, next_href=f"/post_find/{post.id}/next_line",
                           prev=Previous, prev_href=f"/post_find/{post.id}/prev_line",
                           show_button=me_subscribe, show_date=show_date, where_like="line",
                           close_href="/", line=True, comments=final_comments,
                           enabled_com=post.enable_comments, num_com=len(final_comments), form=sorting)


def make_recommendations():
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.id)
    user_subs = user.subscriptions.split(',')
    posts = db_sess.query(Post).filter(Post.user_id != current_user.id).all()
    final_posts = []
    user_tags = set(map(lambda x: x.id, user.themes))
    for post in posts:
        another = db_sess.query(User).get(post.user_id)
        if str(another.id) not in user_subs:
            post.sub = f"{user.id}" not in another.subscribers.split(',')
            tags = set(map(lambda x: x.id, post.themes))
            post.connection = len(user_tags) - len(list(user_tags - tags))
            post.user = db_sess.query(User).get(post.user_id)
            post.get_likes = len(post.likes.split(',')) - 1
            post.like = str(user.id) in post.likes.split(',')
            date = post.publication_date
            today = datetime.datetime.now()
            yesterday = today - datetime.timedelta(days=1)
            if date.year == today.year and date.month == today.month and date.day == today.day:
                post.date = "Сегодня " + date.strftime("%H:%M")
            elif date.year == yesterday.year and date.month == yesterday.month and date.day == yesterday.day:
                post.date = "Вчера " + date.strftime("%H:%M")
            else:
                post.date = date.strftime("%d %B %H:%M")
            comments = db_sess.query(Comment).filter(Comment.post_id == post.id).all()
            post.com = len(comments)
            final_posts.append(post)

    final_posts.sort(key=lambda x: (x.connection, x.publication_date), reverse=True)
    return final_posts


@app.route('/recommendations')
def recommendations():
    if current_user.is_authenticated:
        posts = make_recommendations()
    else:
        posts = []
    return render_template("recommendations.html", title="Рекомендации", posts=posts, recommend=True)


@app.route('/recommendations_view/<int:id>', methods=['POST', 'GET'])
def recommendations_view(id):
    posts = list(map(lambda x: x.id, make_recommendations()))
    db_sess = db_session.create_session()
    sorting = SortForm()
    sorting.sorting.choices = [(0, "Не выбрано"), (1, "Сначала новые"), (2, "Сначала старые")]
    if request.method == "POST":
        if request.form.get("comment") != '' and request.form.get("comment") is not None:
            new_comment = Comment()
            new_comment.user_id = current_user.id
            new_comment.post_id = id
            new_comment.text = request.form.get("comment")
            new_comment.create_date = datetime.datetime.now()
            db_sess.add(new_comment)
            db_sess.commit()

    post = db_sess.query(Post).get(id)
    index = posts.index(id)
    user = db_sess.query(User).filter(User.id == post.user_id).first()
    Previous = index != 0
    Next = index != len(posts) - 1
    Like = str(current_user.id) in post.likes.split(',')
    num_likes = len(post.likes.split(',')) - 1
    me_subscribe = f"{current_user.id}" not in user.subscribers.split(',')
    date = post.publication_date
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    if date.year == today.year and date.month == today.month and date.day == today.day:
        show_date = "Сегодня " + date.strftime("%H:%M")
    elif date.year == yesterday.year and date.month == yesterday.month and date.day == yesterday.day:
        show_date = "Вчера " + date.strftime("%H:%M")
    else:
        show_date = date.strftime("%d %B %H:%M")
    final_comments = []
    if post.enable_comments:
        comments = db_sess.query(Comment).filter(Comment.post_id == post.id)
        for comment in comments:
            comment.user = db_sess.query(User).get(comment.user_id)
            date = comment.create_date
            if date.year == today.year and date.month == today.month and date.day == today.day:
                comment.show_date = "Сегодня " + date.strftime("%H:%M")
            elif date.year == yesterday.year and date.month == yesterday.month and date.day == yesterday.day:
                comment.show_date = "Вчера " + date.strftime("%H:%M")
            else:
                comment.show_date = date.strftime("%d %B %H:%M")
            final_comments.append(comment)

    if request.method == "POST":
        if sorting.sorting.data == 1:
            final_comments.sort(key=lambda x: x.create_date, reverse=True)
        elif sorting.sorting.data == 2:
            final_comments.sort(key=lambda x: x.create_date)

    return render_template("post.html", title="Просмотр поста", post=post, like=Like,
                           user=user, likes=num_likes, next=Next, next_href=f"/post_find/{post.id}/next_rec",
                           prev=Previous, prev_href=f"/post_find/{post.id}/prev_rec", recommend=True,
                           show_button=me_subscribe, show_date=show_date, where_like="rec",
                           close_href="/recommendations", comments=final_comments,
                           enabled_com=post.enable_comments, num_com=len(final_comments), form=sorting)


@app.route('/search/<string:text>/<int:select>', methods=['GET', 'POST'])
def search(text, select):
    message = ""
    users = []
    if select == 0:
        form = SearchForm(types=0)
    else:
        form = SearchForm(types=select, name=text)
    form.types.choices = [(0, "не выбрано"), (1, "имени"), (2, "почте")]
    if request.method == 'POST' or select != 0:
        db_sess = db_session.create_session()
        text = form.name.data
        select = form.types.data
        user_id = 0
        if current_user.is_authenticated:
            user_id = current_user.id
        if form.types.data == 0:
            message = "Выберите тип поиска"
        elif form.types.data == 1:
            users = db_sess.query(User).filter(User.name.like(f'%{text}%'), User.id != user_id).all()
            message = f"По вашему запросу найдено {len(users)} совпадений."
        elif form.types.data == 2:
            users = db_sess.query(User).filter(User.email.like(f'%{text}%'), User.id != user_id).all()
            message = f"По вашему запросу найдено {len(users)} совпадений."
    if current_user.is_authenticated:
        for user in users:
            user.sub = f"{user.id}" not in current_user.subscriptions.split(',')
    return render_template("search.html", title="Поиск", search=True, form=form, message=message, users=users,
                           select=select, text=text)


@app.route('/subscribe-from-search/<string:text>/<int:select>/<int:id>')
def subscribe_search(text, select, id):
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
    return redirect(f'/search/{text}/{select}')


@app.route('/profile')
def profile():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        num_subscriptions = len(current_user.subscriptions.split(',')) - 1
        num_subscribers = len(current_user.subscribers.split(',')) - 1
        posts = db_sess.query(Post).filter(Post.user_id == current_user.id).all()
        num_likes = {post.id: len(post.likes.split(',')) - 1 for post in posts}
        num_comments = {post.id: len(db_sess.query(Comment).filter(Comment.post_id == post.id).all()) for post in posts}
        return render_template("profile.html", title="Профиль", num_subscriptions=num_subscriptions,
                               num_subscribers=num_subscribers, posts=posts, likes=num_likes, user=user,
                               comments=num_comments)
    return render_template("profile.html", title="Профиль", num_subscriptions=-1)


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
    num_comments = {post.id: len(db_sess.query(Comment).filter(Comment.post_id == post.id).all()) for post in posts}
    if me_subscribe:
        me_subscribe = f"{current_user.id}" not in user.subscribers.split(',')
    if current_user.is_authenticated:
        return render_template("profile.html", title="Чужой профиль", num_subscriptions=num_subscriptions,
                               num_subscribers=num_subscribers, posts=posts, likes=num_likes, user=user,
                               show_button=me_subscribe, comments=num_comments)
    return render_template("profile.html", title="Чужой профиль", num_subscriptions=num_subscriptions,
                           num_subscribers=num_subscribers, posts=posts, likes=num_likes, user=user,
                           comments=num_comments)


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


@app.route('/delconfim_comment/<int:id>/<string:way>', methods=['GET', 'POST'])
def delconfirm_comment(id, way):
    db_sess = db_session.create_session()
    comment = db_sess.query(Comment).get(id)
    if way == "rec":
        text = "recommendations"
    else:
        text = way
    return render_template("delete.html", text=f"Нажмите сюда, чтобы удалить выбранный комментарий",
                           title='Подтверждение', link=f'/{text}_view/{comment.post_id}',
                           go=f'/delete_comment/{id}/{way}')


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
    comments = db_sess.query(Comment).filter(Comment.user_id == user.id)
    db_sess.delete(comments)
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
        post.enable_comments = form.comments.data
        db_sess = db_session.create_session()
        for i in form.themes.data:
            post.themes.append(db_sess.query(Theme).get(i))
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
        form.comments.data = post.enable_comments
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        post = db_sess.query(Post).filter(Post.id == id).first()
        post.description = form.description.data
        post.enable_comments = form.comments.data
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
def post_delete(id):
    db_sess = db_session.create_session()
    post = db_sess.query(Post).filter(Post.id == id, Post.user_id == current_user.id).first()
    if post:
        os.remove(os.path.join(app.root_path, 'static', 'img', 'posts', f'{post.id}.jpg'))
        comments = db_sess.query(Comment).filter(Comment.post_id == post.id)
        db_sess.delete(comments)
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
    post = db_sess.query(Post).get(id)
    if "post" in where:
        user = db_sess.query(User).filter(post.user_id == User.id).first()
        posts_user = db_sess.query(Post).filter(Post.user_id == user.id).all()
        if "next" in where:
            new_id = posts_user[posts_user.index(post) + 1].id
        else:
            new_id = posts_user[posts_user.index(post) - 1].id
        return redirect(f'/post_view/{new_id}')
    elif "line" in where:
        posts = list(map(lambda x: x.id, make_line()))
        if "next" in where:
            new_id = posts[posts.index(post.id) + 1]
        else:
            new_id = posts[posts.index(post.id) - 1]
        return redirect(f'/line_view/{new_id}')
    else:
        posts = list(map(lambda x: x.id, make_recommendations()))
        if "next" in where:
            new_id = posts[posts.index(post.id) + 1]
        else:
            new_id = posts[posts.index(post.id) - 1]
        return redirect(f'/recommendations_view/{new_id}')


@app.route('/delete_comment/<int:id>/<string:way>')
def delete_comment(id, way):
    db_sess = db_session.create_session()
    comment = db_sess.query(Comment).get(id)
    post_id = comment.post_id
    db_sess.delete(comment)
    db_sess.commit()
    if way == "rec":
        text = "recommendations"
    else:
        text = way
    return redirect(f"/{text}_view/{post_id}")


@app.route('/post_view/<int:id>', methods=['POST', 'GET'])
def post_view(id):
    db_sess = db_session.create_session()
    sorting = SortForm()
    sorting.sorting.choices = [(0, "Не выбрано"), (1, "Сначала новые"), (2, "Сначала старые")]
    if request.method == "POST":
        if request.form.get("comment") != '' and request.form.get("comment") is not None:
            new_comment = Comment()
            new_comment.user_id = current_user.id
            new_comment.post_id = id
            new_comment.text = request.form.get("comment")
            new_comment.create_date = datetime.datetime.now()
            db_sess.add(new_comment)
            db_sess.commit()

    post = db_sess.query(Post).filter(Post.id == id).first()
    user = db_sess.query(User).filter(User.id == post.user_id).first()
    posts_user = db_sess.query(Post).filter(Post.user_id == user.id).all()
    Previous = posts_user.index(post) != 0
    Next = posts_user.index(post) != len(posts_user) - 1
    Like = True
    me_subscribe = True
    if current_user.is_authenticated:
        Like = str(current_user.id) in post.likes.split(',')
        me_subscribe = f"{current_user.id}" not in user.subscribers.split(',')
    num_likes = len(post.likes.split(',')) - 1
    date = post.publication_date
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    if date.year == today.year and date.month == today.month and date.day == today.day:
        show_date = "Сегодня " + date.strftime("%H:%M")
    elif date.year == yesterday.year and date.month == yesterday.month and date.day == yesterday.day:
        show_date = "Вчера " + date.strftime("%H:%M")
    else:
        show_date = date.strftime("%d %B %H:%M")
    final_comments = []
    if post.enable_comments:
        comments = db_sess.query(Comment).filter(Comment.post_id == post.id)
        for comment in comments:
            comment.user = db_sess.query(User).get(comment.user_id)
            date = comment.create_date
            if date.year == today.year and date.month == today.month and date.day == today.day:
                comment.show_date = "Сегодня " + date.strftime("%H:%M")
            elif date.year == yesterday.year and date.month == yesterday.month and date.day == yesterday.day:
                comment.show_date = "Вчера " + date.strftime("%H:%M")
            else:
                comment.show_date = date.strftime("%d %B %H:%M")
            final_comments.append(comment)

    if request.method == "POST":
        if sorting.sorting.data == 1:
            final_comments.sort(key=lambda x: x.create_date, reverse=True)
        elif sorting.sorting.data == 2:
            final_comments.sort(key=lambda x: x.create_date)

    return render_template("post.html", title="Просмотр поста", post=post, like=Like,
                           user=user, likes=num_likes, next=Next, next_href=f"/post_find/{post.id}/next_post",
                           prev=Previous, prev_href=f"/post_find/{post.id}/prev_post",
                           show_button=me_subscribe, show_date=show_date, where_like="post",
                           close_href=f"/profile/{post.user_id}", comments=final_comments,
                           enabled_com=post.enable_comments, num_com=len(final_comments), form=sorting)


@app.route('/like/<int:id>/<string:where>')
def like(id, where):
    db_sess = db_session.create_session()
    post = db_sess.query(Post).filter(Post.id == id).first()
    if str(current_user.id) in post.likes.split(','):
        post.likes = post.likes.replace(f'{str(current_user.id)},', '')
    else:
        post.likes += f'{current_user.id},'
    db_sess.commit()
    if where == "post":
        return redirect(f'/post_view/{id}')
    if where == "line":
        return redirect(f'/line_view/{id}')
    return redirect(f'/recommendations_view/{id}')


@app.route('/subscribe/<string:typ>/<int:id>')
def subscribe(typ, id):
    db_sess = db_session.create_session()
    if typ == "profile" or typ == "search":
        user = db_sess.query(User).get(id)
    else:
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
    elif typ == "post":
        return redirect(f'/post_view/{post.id}')
    elif typ == "rec":
        return redirect("/recommendations")
    elif typ == "line":
        return redirect('/')
    elif typ == "search":
        return redirect('/search')


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
        return redirect(f"/view_users/{from_id}/subscribers")
    return redirect(f'/view_users/{from_id}/subscriptions')


@app.route('/view_users/<int:id>/<string:typ>', methods=['GET', 'POST'])
def view_users(id, typ):
    db_sess = db_session.create_session()
    form = SortForm()
    form.sorting.choices = [(0, "Не выбрано"), (1, "По имени"), (2, "По возрасту"), (3, "По кол-ву подписчиков"),
                            (4, "По кол-ву подписок")]
    user = db_sess.query(User).get(id)
    other = True
    if current_user.is_authenticated:
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
    if current_user.is_authenticated:
        for i in users:
            i.sub = str(i.id) in current_user.subscriptions.split(',')
    return render_template("subscribers.html", title=name, users=users,
                           view=user, type=typ, other=other, form=form)
