from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired

class AddBookForm(FlaskForm):
    name = StringField('Название книги', validators=[DataRequired()])
    author = StringField('Автор книги', validators=[DataRequired()])
    text = TextAreaField("Текст книги", validators=[DataRequired()])
    is_private = BooleanField("Только для меня")
    submit = SubmitField('Обновить')