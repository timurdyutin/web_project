from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    email = StringField("Почта", validators=[DataRequired()], render_kw={"id": "login__email", "type": "text", "class": "form__input", "placeholder": "Почта"})
    password = PasswordField('Пароль', validators=[DataRequired()], render_kw={"id": "login__password", "type": "password", "class": "form__input", "placeholder": "Пароль"})
    submit = SubmitField('Войти', render_kw={"type": "submit", "value": "Войти!"})