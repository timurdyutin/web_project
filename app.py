from flask import Flask, render_template, redirect, request, abort

from flask_login import LoginManager, login_user, current_user, login_required
from flask_login import logout_user
from flask_restful import abort, Api
from login_form import LoginForm
from register_form import RegisterForm
from add_book_form import AddBookForm
from data.user import User
from data.book import Book
from data import db_session
import json
import os

db_session.global_init("db/web_base.sqlite")
app = Flask(__name__)
app.config["SECRET_KEY"] = "yandexlyceum_secret_key"
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)


def delete_book_from_cd(path):
    print("ok")


def get_text(book, preview=True):
    with open(book.path, "r", encoding="utf-8", errors="ignore") as file:
        if preview:
            try:
                part = [line.strip() for line in file.readlines()][1][0:100]
            except:
                part = "Слишком короткий отрывок"
        else:
            part = [line.strip() for line in file.readlines()][1]
        return part


def add_new_book(book, text, directory="books"):
    with open(f"{directory}/{book.name}.txt", "w", encoding="utf-8") as file:
        file.write(book.author)
        file.write("book.author")
        file.write(text)
    return f"{directory}/{book.name}.txt"


def prepare_books(directory="books"):
    session = db_session.create_session()
    names = [f"{obj.name}.txt" for obj in session.query(Book).all()]
    for book in os.listdir(directory):
        if book not in names:
            with open(f"{directory}/{book}", encoding="utf-8", errors="ignore") as file:
                new_book = Book()
                new_book.name = book.split(".")[0]
                new_book.author = file.readline().strip()
                new_book.path = f"{directory}/{book}"
                session.add(new_book)
    session.commit()
    
prepare_books()


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect("/")
    form = LoginForm()
    print(form.data)
    if form.submit.data is True:
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect("/")
        return render_template(
            "login.html", message="Неправильный логин или пароль", form=form
        )
    return render_template("login.html", title="Авторизация", form=form)


@app.route("/register", methods=["GET", "POST"])
def reqister():
    if current_user.is_authenticated:
        return redirect("/")
    form = RegisterForm()
    if form.submit.data is True:
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template(
                "register.html",
                title="Регистрация!",
                form=form,
                message="Такой пользователь уже есть",
            )
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect("/login")
    return render_template("register.html", title="Регистрация!", form=form)


@app.route("/choose_book")
@login_required
def choose_book():
    session = db_session.create_session()
    user = session.query(User).filter(User.id == current_user.id).first()
    added_books = [book.id for book in user.added_books]
    try:
        all_books = added_books + [int(id) for id in user.liked_books.split(", ")]
    except:
        all_books = added_books
    recommended_books = [
        book for book in session.query(Book).filter(Book.id not in all_books) if book.is_private is False
    ]
    print(recommended_books)
    return render_template(
        "choose_book.html", recommended_books=recommended_books, get_text=get_text
    )


@app.route("/like_book/<int:id>")
@login_required
def like_book(id):
    session = db_session.create_session()
    user = session.query(User).filter(User.id == current_user.id).first()
    try:
        liked_books = user.liked_books.split(", ")
    except:
        liked_books = []
    if str(id) not in liked_books:
        liked_books.append(id)
        user.liked_books = ", ".join([str(i) for i in liked_books])
        session.commit()
    print(liked_books)
    return redirect("/")


@app.route("/delete_book/<int:id>", methods=["GET", "POST"])
@login_required
def delete_book(id):
    session = db_session.create_session()
    book = session.query(Book).filter(Book.id == id).first()
    if book:
        if book.user_id == current_user.id:
            delete_book_from_cd(book.path)
            session.delete(book)
            session.commit()
        else:
            liked_books = (
                session.query(User)
                .filter(User.id == current_user.id)
                .first()
                .liked_books.split(", ")
            )
            liked_books.remove(str(id))
            session.query(User).filter(
                User.id == current_user.id
            ).first().liked_books = ", ".join(liked_books)
            session.commit()
        return redirect("/")
    else:
        abort(404, message=f"Книга {id} не найдена")


@app.route("/read_book/<int:id>")
@login_required
def read_book(id):
    session = db_session.create_session()
    book = session.query(Book).filter(Book.id == id).first()
    if book:
        text = get_text(book, preview=False)
        return render_template("read_book.html", text=text, author=book.author, name=book.name)
    else:
        abort(404, message=f"Книга {id} не найдена")


@app.route("/add_book", methods=["GET", "POST"])
@login_required
def add_book():
    form = AddBookForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        book = Book()
        book.name = form.name.data
        book.author = form.author.data
        book.text = form.text.data
        book.is_private = form.is_private.data
        path = add_new_book(book, book.text)
        book.path = path
        user = session.query(User).filter(User.id == current_user.id).first()
        user.added_books.append(book)
        session.merge(user)
        session.commit()
        return redirect("/")
    return render_template("add_book.html", title="Добавление своей книги", form=form)


@app.route("/")
def index():
    if current_user.is_authenticated:
        session = db_session.create_session()
        added_books = (
            session.query(User).filter(User.id == current_user.id).first().added_books
        )
        try:
            liked_books = (
                session.query(User)
                .filter(User.id == current_user.id)
                .first()
                .liked_books.split(", ")
            )
        except Exception as error:
            liked_books = []
        return render_template(
            "my_books.html",
            added_books=[book for book in added_books if book != ""],
            liked_books=[book for book in liked_books if book != ""],
            title="Мои книги",
            session=session,
            Book=Book,
            len=len,
        )
    else:
        return redirect("/login")
