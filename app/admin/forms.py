from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    IntegerField,
    StringField,
    SubmitField,
    TextAreaField,
    URLField,
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class SkillForm(FlaskForm):
    name = StringField("技能名称", validators=[DataRequired(), Length(max=120)])
    category = StringField("分类", validators=[DataRequired(), Length(max=120)])
    proficiency = IntegerField(
        "熟练度", validators=[DataRequired(), NumberRange(min=0, max=100)]
    )
    icon = StringField("图标", validators=[Optional(), Length(max=120)])
    color = StringField("颜色", validators=[Optional(), Length(max=40)])
    sort_order = IntegerField("排序", default=0)
    is_active = BooleanField("前台展示", default=True)
    submit = SubmitField("保存")


class ExperienceForm(FlaskForm):
    company = StringField("公司", validators=[DataRequired(), Length(max=180)])
    position = StringField("职位", validators=[DataRequired(), Length(max=180)])
    location = StringField("地点", validators=[Optional(), Length(max=120)])
    start_date = DateField("开始日期", validators=[Optional()])
    end_date = DateField("结束日期", validators=[Optional()])
    is_current = BooleanField("至今")
    description = TextAreaField("描述", validators=[Optional()])
    sort_order = IntegerField("排序", default=0)
    is_active = BooleanField("前台展示", default=True)
    submit = SubmitField("保存")


class ProjectForm(FlaskForm):
    name = StringField("项目名称", validators=[DataRequired(), Length(max=180)])
    role = StringField("角色", validators=[Optional(), Length(max=160)])
    tech_stack = StringField("技术栈", validators=[Optional(), Length(max=255)])
    project_url = URLField("项目链接", validators=[Optional(), Length(max=255)])
    source_url = URLField("源码链接", validators=[Optional(), Length(max=255)])
    cover_image_path = StringField("封面路径", validators=[Optional(), Length(max=255)])
    start_date = DateField("开始日期", validators=[Optional()])
    end_date = DateField("结束日期", validators=[Optional()])
    summary = TextAreaField("简介", validators=[Optional()])
    highlights = TextAreaField("亮点", validators=[Optional()])
    sort_order = IntegerField("排序", default=0)
    is_active = BooleanField("前台展示", default=True)
    submit = SubmitField("保存")


class EducationForm(FlaskForm):
    school = StringField("学校", validators=[DataRequired(), Length(max=180)])
    major = StringField("专业", validators=[Optional(), Length(max=180)])
    degree = StringField("学历", validators=[Optional(), Length(max=120)])
    location = StringField("地点", validators=[Optional(), Length(max=120)])
    start_date = DateField("开始日期", validators=[Optional()])
    end_date = DateField("结束日期", validators=[Optional()])
    description = TextAreaField("描述", validators=[Optional()])
    sort_order = IntegerField("排序", default=0)
    is_active = BooleanField("前台展示", default=True)
    submit = SubmitField("保存")


class CertificateForm(FlaskForm):
    name = StringField("证书名称", validators=[DataRequired(), Length(max=180)])
    issuer = StringField("颁发机构", validators=[Optional(), Length(max=180)])
    issue_date = DateField("颁发日期", validators=[Optional()])
    certificate_url = URLField("证书链接", validators=[Optional(), Length(max=255)])
    image_path = StringField("图片路径", validators=[Optional(), Length(max=255)])
    description = TextAreaField("描述", validators=[Optional()])
    sort_order = IntegerField("排序", default=0)
    is_active = BooleanField("前台展示", default=True)
    submit = SubmitField("保存")
