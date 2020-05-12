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

db_session.global_init("db/qb.sqlite")
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)

def add_new_book(name, text): 
    with open(f"books/{name}.txt", "w") as file:
        file.write(text)
    return f"books/{name}.txt"


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)

@app.route('/login', methods=['GET', 'POST'])
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
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)

@app.route('/register', methods=['GET', 'POST'])
def reqister():
    if current_user.is_authenticated:
        return redirect("/")
    form = RegisterForm()
    if form.submit.data is True:
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация!',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            email=form.email.data
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация!', form=form)

@app.route("/choose_book", methods=['GET', 'POST'])
def choose_books():   
    if current_user.is_authenticated: 
        session = db_session.create_session()
        user_books = session.query(User).filter(User.id == current_user.id).first()
        recommended_books = [book for book in session.query(Book) if book.id not in user_books]
        return render_template("choose_book.html", recommended_books=recommended_books)
    
@app.route("/add_book", methods=['GET', 'POST'])
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
        path = add_new_book(form.name.data, form.text.data)
        book.path = path
        session.commit()
        return redirect('/choose_book')
    return render_template('add_book.html', title='Добавление своей книги', 
                           form=form)

@app.route("/")
def index():   
    user_books = []
    if current_user.is_authenticated: 
        session = db_session.create_session()
        user_books = session.query(User).filter(User.id == current_user.id).first().books
        print(type(user_books))
        return render_template("my_books.html", user_books=user_books.split(", "), title="Мои книги", session=session, Book=Book)
    else:
        return redirect("/login")    
    

