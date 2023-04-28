import os
import hashlib

from flask import Flask, make_response, jsonify, render_template, redirect, request, abort
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from sqlalchemy import desc

from data import db_session
from data.discussions import Discussions
from data.genres import Genres
from data.posts import Posts
from data.users import User
from data.comics import Comics
from data.pages import Pages
from forms.discussion import DiscussionForm
from forms.user import RegisterForm, LoginForm
from forms.comics import ComicsForm
from forms.pages import PageForm
from werkzeug.utils import secure_filename
from pathlib import Path

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/blogs.sqlite")
    app.run()


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    comics = db_sess.query(Comics)
    return render_template("main_page.html", comics=comics)


@app.route("/discussions/")
def discussions():
    db_sess = db_session.create_session()
    discs = db_sess.query(Discussions)
    return render_template("discussions.html", discs=discs)


@app.route("/comics/", methods=['GET', 'POST'])
@login_required
def comics():
    db_sess = db_session.create_session()
    genres = db_sess.query(Genres).all()
    groups_list = [(i.id, i.name) for i in genres]

    form = ComicsForm()
    form.genres.choices = groups_list

    if form.validate_on_submit():

        hash_dir = hashlib.md5(form.name.data.encode('utf-8')).hexdigest()
        f = form.cover.data
        filename = secure_filename(f.filename)

        Path('static/comics/' + hash_dir + '/').mkdir(parents=True, exist_ok=True)

        f.save(os.path.join(
            'static/comics/' + hash_dir + '/', filename
        ))

        db_sess = db_session.create_session()

        comic = Comics(
            name=form.name.data,
            namefind=form.name.data.lower(),
            about=form.about.data,
            genres_id=form.genres.data,
            cover='comics/' + hash_dir + '/' + filename
        )

        current_user.comics.append(comic)
        db_sess.merge(comic)
        db_sess.commit()
        return redirect('/')
    return render_template("comics.html", form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/discussions/discs', methods=['GET', 'POST'])
@login_required
def add_disc():
    form = DiscussionForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        discs = Discussions()
        discs.title = form.title.data
        discs.content = form.content.data
        current_user.discussions.append(discs)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/discussions')
    return render_template('discs.html', title='Добавление новости',
                           form=form)


@app.route('/find', methods=['GET', 'POST'])
def find():
    if request.method == 'POST':
        content = request.form.get("findtext")
        if content:
            content = content.lower()
            db_sess = db_session.create_session()
            findcomics = db_sess.query(Comics).filter(Comics.namefind.contains(f"{content}"))
            return render_template("main_page.html", comics=findcomics)
    return redirect('/')


@app.route('/discussions/<int:id>', methods=['GET', 'POST'])
def discussion(id):
    db_sess = db_session.create_session()
    disc = db_sess.query(Discussions).filter(Discussions.id == id)[0]
    if request.method == 'POST':
        content = request.form.get("content")
        if content:
            post = Posts()
            post.content = content
            current_user.posts.append(post)
            post1 = db_sess.merge(post)
            disc.posts.append(post1)
            db_sess.merge(disc)
            db_sess.commit()
        return redirect(f'/discussions/{id}')
    posts = db_sess.query(Posts).filter(Posts.discussion_id == id)
    leng = len([i for i in posts])
    return render_template("discussion.html", posts=posts, disc=disc, leng=leng)


@app.route('/users/<int:id>')
def user(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id)[0]
    comics = list(db_sess.query(Comics).filter(Comics.user_id == id))
    return render_template("user.html", user=user, comics=comics)


@app.route("/comics/<int:id>")
def comic(id):
    db_sess = db_session.create_session()
    comic = db_sess.query(Comics).filter(Comics.id == id)[0]
    try:
        pages = db_sess.query(Pages).filter(Pages.comics_id == id).order_by(desc(Pages.number)).limit(1)[0]
    except IndexError:
        pages = 0
    return render_template("comic.html", comic=comic, pages=pages)


@app.route("/comics/<int:id>/read")
def read(id):
    db_sess = db_session.create_session()
    comic = db_sess.query(Comics).filter(Comics.id == id)[0]
    pages = list(db_sess.query(Pages).filter(Pages.comics_id == id).order_by(Pages.number))
    link = f"/comics/{id}"
    return render_template("read.html", pages=pages, link=link, comic=comic)


@app.route("/add_page/<int:id>", methods=['GET', 'POST'])
@login_required
def add_page(id):
    form = PageForm()
    db_sess = db_session.create_session()
    comic = db_sess.query(Comics).filter(Comics.id == id)[0]
    try:
        pages = db_sess.query(Pages).filter(Pages.comics_id == id).order_by(desc(Pages.number)).limit(1)[0]
    except IndexError:
        pages = 0

    if form.validate_on_submit():
        hash_dir = hashlib.md5(comic.name.encode('utf-8')).hexdigest()
        f = form.page.data
        filename = secure_filename(f.filename)

        Path('static/comics/' + hash_dir + '/').mkdir(parents=True, exist_ok=True)

        f.save(os.path.join(
            'static/comics/' + hash_dir + '/', filename
        ))

        db_sess = db_session.create_session()

        page = Pages(
            number=int(form.number.data),
            comics_id=id,
            page='comics/' + hash_dir + '/' + filename
        )

        db_sess.merge(page)
        db_sess.commit()
        return redirect(f'/add_page/{comic.id}')
    return render_template("add_page.html", comic=comic, form=form, pages=pages)


@app.route('/comic_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def comic_delete(id):
    db_sess = db_session.create_session()
    comic = db_sess.query(Comics).filter(Comics.id == id,
                                         Comics.user == current_user
                                         ).first()
    if comic:
        db_sess.delete(comic)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/disc_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def disc_delete(id):
    db_sess = db_session.create_session()
    discs = db_sess.query(Discussions).filter(Discussions.id == id,
                                              Discussions.user == current_user
                                              ).first()
    if discs:
        db_sess.delete(discs)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/discussions')


@app.route('/post_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def post_delete(id):
    db_sess = db_session.create_session()
    post = db_sess.query(Posts).filter(Posts.id == id,
                                       Posts.user == current_user
                                       ).first()
    if post:
        db_sess.delete(post)
        db_sess.commit()
    else:
        abort(404)
    return redirect(f'/discussions/{post.discussion_id}')


if __name__ == '__main__':
    main()

