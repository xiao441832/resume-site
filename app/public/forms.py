from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional


class MessageForm(FlaskForm):
    name = StringField("姓名", validators=[DataRequired(), Length(max=120)])
    email = StringField("邮箱", validators=[DataRequired(), Email(), Length(max=255)])
    phone = StringField("手机号", validators=[Optional(), Length(max=80)])
    content = TextAreaField("留言内容", validators=[DataRequired(), Length(min=5, max=2000)])
    submit = SubmitField("提交留言")
