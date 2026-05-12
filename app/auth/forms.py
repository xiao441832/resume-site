from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp


class LoginForm(FlaskForm):
    username = StringField("用户名", validators=[DataRequired(), Length(max=80)])
    password = PasswordField("密码", validators=[DataRequired(), Length(min=6, max=128)])
    submit = SubmitField("登录")


class RegisterForm(FlaskForm):
    username = StringField(
        "用户名",
        validators=[
            DataRequired(),
            Length(min=3, max=80),
            Regexp(
                r"^[A-Za-z0-9_]+$",
                message="用户名只能包含字母、数字和下划线。",
            ),
        ],
    )
    email = StringField("邮箱", validators=[DataRequired(), Email(), Length(max=255)])
    display_name = StringField("显示名称", validators=[DataRequired(), Length(max=120)])
    password = PasswordField("密码", validators=[DataRequired(), Length(min=6, max=128)])
    confirm_password = PasswordField(
        "确认密码",
        validators=[DataRequired(), EqualTo("password", message="两次输入的密码不一致。")],
    )
    submit = SubmitField("注册")
