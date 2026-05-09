from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField("用户名", validators=[DataRequired(), Length(max=80)])
    password = PasswordField("密码", validators=[DataRequired(), Length(min=6, max=128)])
    submit = SubmitField("登录")
