from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import (
    BooleanField,
    DateField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
    URLField,
)
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional


class AccountStatusForm(FlaskForm):
    is_active = BooleanField("启用账号")
    ban_reason = TextAreaField("封禁原因", validators=[Optional(), Length(max=255)])
    submit = SubmitField("保存账号状态")


class PublishStatusForm(FlaskForm):
    can_publish = BooleanField("允许发布公开简历")
    publish_ban_reason = TextAreaField(
        "禁止发布原因", validators=[Optional(), Length(max=255)]
    )
    submit = SubmitField("保存发布权限")


class ResumeBlockForm(FlaskForm):
    is_public_blocked = BooleanField("封禁公开简历")
    public_block_reason = TextAreaField(
        "公开简历封禁原因", validators=[Optional(), Length(max=255)]
    )
    submit = SubmitField("保存公开简历状态")


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


class ProfileForm(FlaskForm):
    name = StringField("姓名", validators=[DataRequired(), Length(max=120)])
    title = StringField("职业标题", validators=[DataRequired(), Length(max=160)])
    city = StringField("城市", validators=[Optional(), Length(max=120)])
    email = StringField("邮箱", validators=[Optional(), Email(), Length(max=255)])
    phone = StringField("电话", validators=[Optional(), Length(max=80)])
    wechat = StringField("微信", validators=[Optional(), Length(max=120)])
    github_url = URLField("GitHub", validators=[Optional(), Length(max=255)])
    website_url = URLField("个人网站", validators=[Optional(), Length(max=255)])
    avatar = FileField("头像")
    resume_file = FileField("简历文件")
    summary = TextAreaField("个人简介", validators=[Optional()])
    job_status = StringField("求职状态", validators=[Optional(), Length(max=160)])
    is_active = BooleanField("前台展示", default=True)
    submit = SubmitField("保存")


class MessageStatusForm(FlaskForm):
    status = SelectField(
        "状态",
        choices=[
            ("unread", "未读"),
            ("read", "已读"),
            ("handled", "已处理"),
            ("spam", "垃圾留言"),
        ],
        validators=[DataRequired()],
    )
    admin_note = TextAreaField("备注", validators=[Optional()])
    submit = SubmitField("保存")


class SettingForm(FlaskForm):
    site_title = StringField("站点标题", validators=[DataRequired(), Length(max=255)])
    seo_description = StringField("SEO 描述", validators=[Optional(), Length(max=500)])
    icp_text = StringField("备案号", validators=[Optional(), Length(max=255)])
    messages_enabled = BooleanField("开启留言")
    submit = SubmitField("保存")
