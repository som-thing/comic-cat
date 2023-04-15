from flask import Flask, make_response, jsonify, render_template, redirect, request, abort
from flask_login import LoginManager, current_user, login_user, logout_user, login_required

from data import db_session
from data.discussions import Discussions
from data.posts import Posts
from data.users import User
from forms.discussion import DiscussionForm
from forms.user import RegisterForm, LoginForm

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
    discs = db_sess.query(Discussions)
    return render_template("discussions.html", discs=discs)


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


@app.route('/discs', methods=['GET', 'POST'])
@login_required
def add_news():
    form = DiscussionForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        discs = Discussions()
        discs.title = form.title.data
        discs.content = form.content.data
        current_user.discussions.append(discs)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('discs.html', title='Добавление новости',
                           form=form)


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
            db_sess.merge(current_user)
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
    return render_template("user.html", user=user)


"""@app.route('/discs/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = DiscussionForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        discs = db_sess.query(Discussions).filter(Discussions.id == id,
                                                  Discussions.user == current_user
                                                  ).first()
        if discs:
            form.title.data = discs.title
            form.content.data = discs.content
            form.is_private.data = discs.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        discs = db_sess.query(Discussions).filter(Discussions.id == id,
                                                  Discussions.user == current_user
                                                  ).first()
        if discs:
            discs.title = form.title.data
            discs.content = form.content.data
            discs.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('discs.html',
                           title='Редактирование новости',
                           form=form
                           )"""


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
    return redirect('/')


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
