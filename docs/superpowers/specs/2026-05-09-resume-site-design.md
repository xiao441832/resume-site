# Python + MySQL 个人简历网站设计说明

日期：2026-05-09

## 1. 目标

开发一个基于 Python、Flask、MySQL、Bootstrap 和 Jinja2 的响应式个人简历网站。网站采用服务端渲染，包含前台简历展示页面和自定义后台管理系统。

数据库已经在独立数据库服务器上创建好，但目前是空库。因此项目需要提供清晰的数据表结构、初始化数据和初始化流程，既支持通过阿里云 DMS 手动执行 SQL，也支持在 Web 服务器命令行中通过 Flask CLI 初始化。

## 2. 已确认技术栈

前端：

- HTML5：页面结构。
- CSS3：页面样式。
- Bootstrap 5：响应式布局、按钮、表格、表单和卡片。
- JavaScript 与 jQuery：轻量交互、图片预览、删除确认、返回顶部等。
- Jinja2：由 Flask 在服务端渲染模板。

后端：

- Python 3。
- Flask。
- PyMySQL：连接 MySQL。
- Werkzeug：密码哈希和基础安全工具。
- Flask-WTF：表单校验和 CSRF 防护。
- Flask-Limiter：登录和留言限速。
- Gunicorn：生产环境运行 Flask 应用。
- Nginx：反向代理和静态资源服务。

数据库：

- MySQL 8.0。
- 兼容阿里云 RDS MySQL。
- 可通过 DMS 在线执行建表 SQL。
- 使用 `utf8mb4` 字符集，支持中文和特殊字符。

部署：

- Linux Web 服务器。
- Gunicorn 应用进程。
- Nginx 反向代理。
- systemd 服务管理。
- Flask 服务端渲染、B/S 架构、单 MySQL 数据库实例。

明确不使用：

- Vue。
- React。
- Angular。
- 前端路由。
- 前端状态管理。
- 前后端分离打包部署。

## 3. 实现方式

采用模块化 Flask 应用，使用蓝图拆分前台、登录认证和后台管理。数据库访问使用 PyMySQL 和参数化 SQL，不引入 ORM，便于检查 SQL 行为，也便于将 `database/schema.sql` 直接复制到阿里云 DMS 执行。

项目提供两种初始化方式：

- `database/schema.sql`：用于 DMS 或命令行建表。
- `flask init-db` 与 `flask seed-db`：用于在 Web 服务器命令行初始化表和默认数据。

## 4. 项目结构

```text
resume-site/
  app/
    __init__.py
    config.py
    db.py
    auth/
    public/
    admin/
    services/
    templates/
    static/
  database/
    schema.sql
    seed.sql
  deployment/
    nginx.conf.example
    resume-site.service.example
    gunicorn.conf.py
  tests/
  .env.example
  requirements.txt
  run.py
  README.md
```

主要职责：

- `public`：前台简历首页和留言提交。
- `auth`：管理员登录、退出、Session 管理和登录限速。
- `admin`：后台管理页面和 CRUD 功能。
- `db.py`：MySQL 连接、查询、事务和 SQL 脚本执行。
- `services/upload_service.py`：上传文件校验、命名和保存。
- `database`：适合 DMS 执行的建表和初始化 SQL。
- `deployment`：生产部署示例。

## 5. 数据库设计

所有表使用 MySQL 8.0、InnoDB、`utf8mb4`、`utf8mb4_unicode_ci`。主键使用 `BIGINT UNSIGNED AUTO_INCREMENT`。需要排序的内容使用 `sort_order`，前台可见状态使用 `is_active`。

核心表：

- `admin_users`：管理员账号，保存用户名、密码哈希、显示名、邮箱、启用状态和最后登录时间。密码不明文保存。
- `profile`：个人资料，通常只有一条启用记录，保存姓名、标题、城市、联系方式、头像路径、简历文件路径、简介和求职状态。
- `skills`：技能名称、分类、熟练度、图标、颜色、排序和展示状态。
- `experiences`：工作或实习经历。
- `projects`：项目经历、技术栈、项目链接、源码链接、封面图、简介和亮点。
- `education`：教育经历。
- `certificates`：证书信息。
- `messages`：访客留言、来源 IP、浏览器信息、处理状态和管理员备注。

辅助表：

- `uploads`：上传文件记录，只保存文件元数据和相对路径。
- `site_settings`：站点标题、SEO 描述、备案信息、留言开关等键值配置。

数据库安全要求：

- 所有运行时 SQL 使用参数化查询。
- 使用专用 MySQL 账号，并限制在简历数据库范围内。
- 上传文件只保存到 Web 服务器，MySQL 中只保存相对路径。
- 不在 MySQL 中保存上传文件二进制内容。
- 初始管理员通过环境变量和 `flask seed-db` 创建。

## 6. 前台网站设计

前台为单页简历首页，由 `GET /` 渲染。

页面模块：

- 导航栏：站点名称和页面锚点。
- 个人简介区：头像、姓名、职位标题、城市、简介、联系按钮和简历下载按钮。
- 技能区：按分类展示技能，使用徽章或进度条。
- 经历区：用时间线展示工作或实习经历。
- 项目区：卡片网格展示项目封面、技术栈、简介、亮点和链接。
- 教育区：紧凑列表或时间线。
- 证书区：卡片或列表，可展示图片和外链。
- 联系区：姓名、邮箱、手机号和留言内容表单。
- 页脚：版权、备案信息和社交链接。
- 返回顶部按钮：由 JavaScript/jQuery 控制。

响应式要求：

- 桌面端：内容居中，项目卡片两到三列。
- 平板端：项目卡片两列。
- 移动端：导航折叠，内容单列展示。
- 头像和封面图保持稳定尺寸，减少布局跳动。

## 7. 后台管理设计

后台路径统一在 `/admin` 下，所有管理页面都要求登录。

页面：

- `/admin/login`：管理员登录。
- `/admin`：仪表盘，展示技能、项目、留言和未读留言数量。
- `/admin/profile`：管理个人资料、头像和简历 PDF。
- `/admin/skills`：管理技能。
- `/admin/experiences`：管理工作和实习经历。
- `/admin/projects`：管理项目经历和项目封面。
- `/admin/education`：管理教育经历。
- `/admin/certificates`：管理证书和证书图片。
- `/admin/messages`：查看留言、更新状态、添加备注、删除留言。
- `/admin/settings`：管理站点标题、SEO 描述、备案信息和留言开关。
- `/admin/logout`：退出登录。

后台界面：

- Bootstrap 5 顶栏和侧边栏。
- 表格列表页、状态徽章、编辑/删除按钮。
- Bootstrap 表单页面。
- 删除确认提示。
- 上传图片预览。
- Flash 消息以 Bootstrap alert 展示。

## 8. 路由和数据流

前台：

- `GET /`：读取启用的个人资料、技能、经历、项目、教育、证书和站点设置，渲染首页。
- `POST /messages`：校验 CSRF 和表单字段，执行限速，检查留言开关，写入 `messages` 表并返回提示。

认证：

- `GET /admin/login`：渲染登录表单。
- `POST /admin/login`：校验账号密码，写入 Session，更新最后登录时间。
- `POST /admin/logout`：清空 Session。

后台：

- `GET /admin`：仪表盘。
- `GET|POST /admin/profile`：编辑个人资料。
- `GET /admin/<module>`：列表页。
- `GET|POST /admin/<module>/new`：新增记录。
- `GET|POST /admin/<module>/<id>/edit`：编辑记录。
- `POST /admin/<module>/<id>/delete`：删除记录。
- 留言状态、站点设置和上传文件通过对应后台路由处理。

上传流程：

1. 管理员上传头像、简历 PDF、项目封面或证书图片。
2. 服务端校验扩展名、MIME 类型和文件大小。
3. 文件使用 UUID 命名，保存到 `app/static/uploads/`。
4. MySQL 保存相对路径和上传元数据。
5. 生产环境由 Nginx 提供静态访问。

## 9. 安全设计

- 使用 Werkzeug `generate_password_hash` 和 `check_password_hash` 处理管理员密码。
- 所有表单使用 Flask-WTF CSRF 防护。
- 登录限速，例如 `5 per minute`。
- 留言提交限速，例如 `3 per minute`。
- 所有数据库查询使用参数化 SQL。
- 上传文件限制为图片和简历 PDF。
- 限制上传大小，例如图片 2 MB，PDF 5 MB。
- 上传文件名使用 UUID。
- `SECRET_KEY` 从环境变量读取。
- 开启 `SESSION_COOKIE_HTTPONLY=True`。
- HTTPS 生产环境开启 `SESSION_COOKIE_SECURE=True`。
- `.env` 不进入版本控制，只提交 `.env.example`。

## 10. 部署设计

Web 服务器和数据库服务器分开部署。

Web 服务器：

- Linux。
- Python 虚拟环境。
- Flask 应用。
- Gunicorn 进程。
- Nginx 反向代理和静态资源服务。
- systemd 管理进程。

数据库服务器：

- 阿里云 RDS MySQL 8.0 或兼容 MySQL 8.0。
- 数据库名已存在，当前为空库。
- 通过 DMS 或 Flask CLI 初始化。

部署步骤：

1. 确认 RDS 数据库存在并使用 `utf8mb4`。
2. 在 DMS 执行 `database/schema.sql`，或在 Web 服务器运行 `flask init-db`。
3. 在 Web 服务器配置 `.env`。
4. 运行 `flask seed-db` 创建初始管理员和默认内容。
5. 使用 systemd 启动 Gunicorn。
6. 配置 Nginx 代理域名到 Gunicorn，并服务静态资源和上传文件。
7. 登录 `/admin/login` 更新简历内容。

## 11. 测试策略

- 数据库助手测试：连接参数、SQL 切分、事务回滚。
- 登录认证测试：登录成功、登录失败、受保护路由。
- 前台测试：首页渲染、上传路径、外链过滤、留言提交。
- 后台测试：资源配置、列表渲染、个人信息、留言状态、站点设置。
- 上传测试：允许类型、禁止类型、MIME 不匹配、大小限制。

## 12. 验收标准

- 前台首页能从 MySQL 读取数据并通过 Jinja2 渲染。
- 页面在桌面、平板、移动端响应式展示。
- 管理员可以登录和退出。
- 管理员可以维护个人资料、技能、经历、项目、教育、证书、留言和站点设置。
- 密码哈希保存，不明文存储。
- 表单启用 CSRF 防护。
- 登录和留言提交有限速。
- SQL 使用参数化查询。
- 上传文件保存在 Web 服务器，MySQL 只保存路径。
- 项目包含 `schema.sql`、`seed.sql`、`flask init-db` 和 `flask seed-db`。
- 项目包含 Gunicorn、Nginx、systemd 部署示例。
- 项目包含 `.env.example`，不提交真实密钥。
