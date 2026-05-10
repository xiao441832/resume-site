# 个人简历网站实施计划

日期：2026-05-09

## 目标

基于已确认的设计说明，完成一个 Flask + MySQL 的响应式个人简历网站。项目采用前后端不分离、服务端渲染、单 MySQL 数据库实例的架构。数据库服务器与 Web 服务器分离，数据库可以从空库开始初始化。

## 技术范围

- 前端：HTML5、CSS3、Bootstrap 5、JavaScript、jQuery、Jinja2。
- 后端：Python 3、Flask、PyMySQL、Werkzeug、Flask-WTF、Flask-Limiter。
- 数据库：MySQL 8.0 / 阿里云 RDS MySQL，字符集 `utf8mb4`。
- 部署：Linux、Nginx、Gunicorn、systemd。

## 文件职责

- `requirements.txt`：Python 依赖。
- `.env.example`：环境变量示例，不包含真实密钥。
- `run.py`：本地运行入口。
- `app/__init__.py`：Flask 应用工厂、扩展初始化、蓝图注册。
- `app/config.py`：读取环境变量并生成配置。
- `app/db.py`：MySQL 连接、查询、事务和 SQL 文件执行。
- `app/cli.py`：`flask init-db` 和 `flask seed-db`。
- `app/auth/`：后台登录、退出和登录保护。
- `app/public/`：前台首页和留言提交。
- `app/admin/`：后台仪表盘、资源管理、个人信息、留言、站点设置。
- `app/services/upload_service.py`：上传文件校验和保存。
- `app/templates/`：Jinja2 模板。
- `app/static/`：CSS、JavaScript 和上传目录。
- `database/schema.sql`：MySQL 建表脚本。
- `database/seed.sql`：默认站点设置和默认个人资料。
- `deployment/`：Gunicorn、Nginx、systemd 示例配置。
- `tests/`：自动化测试。
- `README.md`：中文安装、初始化、部署和测试说明。

## 实施任务

### 任务 1：项目骨架和应用工厂

创建基础目录、依赖文件、环境变量示例、测试配置、Flask 应用工厂和扩展初始化。生产环境要求 `SECRET_KEY` 不得为空或使用默认值，HTTPS 部署时强制安全 Cookie。

### 任务 2：数据库助手层

实现 PyMySQL 连接参数构建、应用上下文连接管理、查询函数、写入函数、事务回滚和 SQL 脚本切分。SQL 切分需要正确处理字符串中的分号。

### 任务 3：数据库结构、默认数据和 Flask CLI

提供 `database/schema.sql` 和 `database/seed.sql`。实现 `flask init-db` 和 `flask seed-db`，支持在 Web 服务器命令行初始化，也支持把 SQL 复制到阿里云 DMS 手动执行。

### 任务 4：管理员认证

实现 `/admin/login`、`/admin/logout`、登录表单、密码哈希校验、Session 写入、登录失败提示和登录保护装饰器。

### 任务 5：前台首页和留言提交

实现服务端渲染的简历首页，展示个人资料、技能、经历、项目、教育、证书和联系方式。实现留言表单，包含 CSRF、防刷限速、字段校验和 MySQL 写入。

### 任务 6：上传服务

实现上传文件扩展名、MIME 类型、大小限制、UUID 文件名和相对路径返回。图片用于头像、项目封面、证书图片；PDF 用于简历文件。

### 任务 7：后台资源框架和仪表盘

实现后台蓝图、资源配置注册表、通用新增/编辑/删除 SQL 构建、仪表盘统计和后台基础布局。

### 任务 8：后台管理页面

完成资源列表页、资源表单页、个人资料页、留言列表、留言详情和站点设置页面。后台表单使用 Flask-WTF，删除操作使用 POST 和 CSRF。

### 任务 9：部署文件和 README

补充 Gunicorn、Nginx、systemd 示例配置，并编写中文 README，说明本地安装、空数据库初始化、阿里云 RDS 注意事项、生产部署和测试命令。

### 任务 10：完整验证

运行完整测试套件、Python 语法编译检查，并使用浏览器检查前台首页、移动端导航、返回顶部和后台登录页。

## 已完成验证

- `pytest -v`：35 个测试通过。
- `python -m compileall app`：通过。
- 浏览器检查：前台首页、移动端导航、返回顶部和后台登录页均可正常渲染。
- 控制台检查：无前端错误或警告。

## 注意事项

- 数据库密码、服务器密码、后台管理员密码不得写入仓库。
- `.env` 只在服务器本地保存。
- 如果使用阿里云 RDS，需要配置白名单或使用同 VPC 内网地址。
- 上传文件保存在 Web 服务器，MySQL 只保存相对路径和元数据。
- 生产环境建议配置 HTTPS，并保持 `SESSION_COOKIE_SECURE=1`。
