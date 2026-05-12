# 多用户在线简历管理系统设计说明

## 一、项目定位

当前项目是单用户个人简历网站，适合作为个人展示页，但作为毕业设计系统性不足。改造后的项目定位为“多用户在线简历管理系统”，允许多个用户注册账号、维护自己的简历内容，并通过公开链接展示给访客。

系统继续采用 Python、Flask、MySQL、Jinja2、Bootstrap 5、Nginx、Gunicorn、systemd 的前后端不分离架构，不引入 Vue、React、Angular，也不改成前后端分离项目。

## 二、改造目标

本次改造的目标是把项目从“一个管理员维护一个人的简历”升级为“多个用户分别维护自己的简历”。

核心目标如下：

- 支持普通用户注册、登录、退出。
- 每个用户拥有独立的简历数据。
- 每个用户可以维护自己的个人信息、技能、工作经历、项目经历、教育经历、证书信息。
- 每个用户可以设置简历是否公开。
- 访客可以访问不同用户的公开简历页面。
- 访客可以给指定用户提交留言。
- 普通用户只能管理自己的数据和留言。
- 超级管理员可以管理全部用户、查看全站统计、禁用异常账号。
- 保留现有 MySQL、Flask-WTF、CSRF、防暴力破解、文件上传、留言管理、生产部署能力。

## 三、不做的范围

为了让毕业设计范围可控，本系统不做招聘平台方向的复杂功能。

暂不包含：

- 企业账号。
- 职位发布。
- 简历投递。
- 在线聊天。
- 支付功能。
- 前后端分离打包部署。
- 多租户独立数据库。
- 复杂权限菜单配置。

## 四、用户角色

系统分为三类角色。

访客：

- 查看系统首页。
- 搜索公开简历。
- 访问公开简历详情页。
- 给某个用户留言。

普通用户：

- 注册账号。
- 登录和退出。
- 修改自己的账号资料。
- 维护自己的简历内容。
- 上传自己的头像、项目图片、简历附件。
- 管理发送给自己的留言。
- 设置自己的简历公开或隐藏。

超级管理员：

- 登录后台。
- 查看全站统计。
- 查看全部用户列表。
- 禁用或启用用户。
- 查看用户简历数据概况。
- 查看全站留言。
- 管理站点基础设置。

## 五、推荐页面结构

公开端：

```text
/                         系统首页，展示公开简历列表和搜索入口
/u/<username>             用户公开简历主页
/u/<username>/messages    给指定用户提交留言
```

认证端：

```text
/auth/register            用户注册
/auth/login               用户登录
/auth/logout              用户退出
```

普通用户后台：

```text
/dashboard                用户后台首页
/dashboard/profile        我的个人信息
/dashboard/skills         我的技能
/dashboard/experiences    我的工作经历
/dashboard/projects       我的项目经历
/dashboard/education      我的教育经历
/dashboard/certificates   我的证书
/dashboard/messages       我的留言
/dashboard/settings       我的简历设置
```

超级管理员后台：

```text
/admin                    管理员后台首页
/admin/users              用户管理
/admin/messages           全站留言管理
/admin/settings           站点设置
```

## 六、数据库设计调整

新增 `users` 表，作为普通用户和超级管理员的统一账号表。

推荐字段：

```text
id
username
email
password_hash
display_name
role
is_active
last_login_at
created_at
updated_at
```

`role` 推荐使用：

```text
user        普通用户
admin       超级管理员
```

原有简历相关表需要增加用户归属字段：

```text
profile.user_id
skills.user_id
experiences.user_id
projects.user_id
education.user_id
certificates.user_id
uploads.user_id
```

留言表需要改为指向被留言的用户：

```text
messages.target_user_id
```

站点设置表 `site_settings` 继续作为全站配置使用。用户个人的简历公开状态、简历标题、SEO 描述等信息建议放入 `profile` 或新增 `user_settings` 表。为了降低复杂度，第一版优先放在 `profile` 表中。

## 七、数据隔离原则

所有普通用户后台查询必须带上当前登录用户的 `user_id`。

示例规则：

```text
查询技能：WHERE user_id = 当前用户 id
编辑技能：WHERE id = 技能 id AND user_id = 当前用户 id
删除项目：WHERE id = 项目 id AND user_id = 当前用户 id
查看留言：WHERE target_user_id = 当前用户 id
```

公开简历页只能展示满足以下条件的数据：

```text
用户启用
简历公开
数据项启用
```

超级管理员可以跨用户查看数据，但普通用户不能通过修改 URL 访问其他用户的数据。

## 八、认证与权限设计

现有 `/admin/login` 更适合改造为统一登录体系。

推荐调整为：

- `/auth/login`：普通用户和管理员统一登录。
- 登录成功后按角色跳转。
- 普通用户跳转到 `/dashboard`。
- 超级管理员跳转到 `/admin`。

Session 中保存：

```text
user_id
username
display_name
role
```

新增两个权限装饰器：

```text
login_required
admin_required
```

`login_required` 用于普通用户后台和管理员后台的登录校验。`admin_required` 用于超级管理员后台。

## 九、前台展示设计

首页从单个简历展示页改为公开简历列表页。

首页内容包括：

- 系统名称。
- 搜索框。
- 公开用户简历卡片。
- 用户姓名、职位、城市、技能摘要。
- 点击进入 `/u/<username>`。

用户公开简历页复用现有首页模板结构，但数据源从“全站唯一简历”改为“指定用户的简历”。

公开简历页继续包含：

- 个人信息。
- 技能。
- 工作经历。
- 项目经历。
- 教育经历。
- 证书。
- 联系方式。
- 留言表单。

## 十、后台管理设计

普通用户后台复用现有后台 CRUD 页面，但所有资源都按当前用户过滤。

现有资源管理模块可以继续使用，但需要让资源配置支持用户归属字段。新增数据时自动写入当前用户 `id`，查询、编辑、删除时自动限制当前用户范围。

超级管理员后台不直接替代普通用户后台，而是独立保留：

- 用户列表。
- 用户启用和禁用。
- 全站数据统计。
- 全站留言查看。

## 十一、文件上传设计

上传文件继续保存在服务器 `app/static/uploads` 下。

为了避免多用户文件混乱，建议按用户分目录：

```text
uploads/users/<user_id>/avatars/
uploads/users/<user_id>/projects/
uploads/users/<user_id>/resumes/
```

`uploads` 表记录 `user_id`，普通用户只能查看自己上传的文件记录。

## 十二、留言设计

留言从“发给站点管理员”改为“发给某个简历用户”。

访问路径：

```text
POST /u/<username>/messages
```

提交时写入：

```text
target_user_id
name
email
phone
content
ip_address
user_agent
status
```

普通用户后台只显示发送给自己的留言。超级管理员后台可以查看全部留言。

## 十三、迁移策略

为了保护现有部署数据，推荐使用平滑迁移。

迁移步骤：

1. 新增 `users` 表。
2. 创建一个默认超级管理员账号。
3. 创建一个默认普通用户账号，用于承接当前单人简历数据。
4. 给简历相关表增加 `user_id` 字段。
5. 将现有 `profile`、`skills`、`projects` 等数据绑定到默认普通用户。
6. 给 `messages` 增加 `target_user_id` 字段，并绑定到默认普通用户。
7. 验证旧简历页面数据可通过 `/u/<username>` 正常访问。
8. 稳定后逐步废弃旧的 `/admin/login` 单管理员入口。

## 十四、测试策略

需要补充以下自动化测试：

- 用户注册成功。
- 用户登录成功。
- 禁用用户不能登录。
- 普通用户只能看到自己的简历数据。
- 普通用户不能编辑其他用户的数据。
- 超级管理员可以查看用户列表。
- 首页只展示公开简历。
- 隐藏简历不能被公开访问。
- 给指定用户提交留言后，只出现在该用户后台。
- 上传文件按用户目录保存。
- 迁移脚本可以把旧数据绑定到默认用户。

## 十五、部署影响

部署方式继续保持不变：

- Linux。
- Nginx。
- Gunicorn。
- systemd。
- 单 MySQL 数据库实例。

需要额外注意：

- 部署前备份数据库。
- 生产环境执行迁移 SQL 前先在本地或测试库验证。
- 如果当前线上已经有留言或简历数据，必须先导出备份。
- 更新 README 和部署文档，说明系统已经从个人简历网站升级为多用户简历系统。

## 十六、推荐实施顺序

推荐按以下顺序开发：

1. 数据库多用户改造。
2. 用户注册、登录、角色权限。
3. 普通用户后台数据隔离。
4. 公开用户简历页 `/u/<username>`。
5. 多用户留言功能。
6. 超级管理员用户管理。
7. 首页公开简历列表和搜索。
8. 文件上传按用户分目录。
9. 文档、测试和部署迁移。

这个顺序可以让系统每一步都保持可运行，避免一次性大改导致无法定位问题。
