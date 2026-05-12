# 多用户在线简历管理系统

这是一个基于 Flask + MySQL 的多用户在线简历管理系统，采用 Bootstrap 5 和 Jinja2 服务端渲染。系统支持普通用户注册、登录、维护自己的简历内容，并通过公开链接展示个人简历；超级管理员可以管理全站用户和基础设置。

## 一、技术栈

- 前端：HTML5、CSS3、Bootstrap 5、JavaScript、jQuery、Jinja2。
- 后端：Python 3、Flask、PyMySQL、Werkzeug、Flask-WTF、Flask-Limiter。
- 数据库：MySQL 8.0 或阿里云 RDS MySQL，字符集使用 `utf8mb4`。
- 部署：Linux、Nginx、Gunicorn、systemd。
- 架构：前后端不分离，Flask 服务端渲染，B/S 架构，单 MySQL 数据库实例。

## 二、主要功能

- 用户注册、登录、退出。
- 普通用户维护自己的个人信息、技能、工作经历、项目经历、教育经历、证书信息。
- 普通用户管理发送给自己的留言。
- 每个用户拥有独立公开简历页：`/u/<username>`。
- 首页展示公开简历列表，并支持关键词搜索。
- 访客可以给指定用户提交留言。
- 超级管理员可以登录 `/admin` 查看全站数据和站点设置。
- 普通用户数据通过 `user_id` 隔离，不能访问或修改其他用户的数据。

## 三、核心访问地址

```text
/                         公开简历列表
/u/<username>             用户公开简历页
/u/<username>/messages    指定用户留言提交地址
/auth/register            用户注册
/auth/login               用户登录
/dashboard                普通用户后台
/admin                    超级管理员后台
```

旧地址 `/admin/login` 会自动跳转到统一登录页 `/auth/login`。

## 四、本地安装

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

复制 `.env.example` 后，请在 `.env` 中配置：

- `SECRET_KEY`
- `MYSQL_HOST`、`MYSQL_PORT`、`MYSQL_USER`、`MYSQL_PASSWORD`、`MYSQL_DATABASE`
- `ADMIN_USERNAME`、`ADMIN_PASSWORD`、`ADMIN_EMAIL`、`ADMIN_DISPLAY_NAME`
- `DEFAULT_USER_USERNAME`、`DEFAULT_USER_PASSWORD`、`DEFAULT_USER_EMAIL`、`DEFAULT_USER_DISPLAY_NAME`

不要提交 `.env`，也不要把数据库密码、服务器密钥、后台管理员密码发到公开位置。

## 五、数据库初始化

如果是全新的空数据库，执行：

```bash
flask --app run init-db
flask --app run seed-db
```

`init-db` 会创建多用户数据库表。`seed-db` 会创建：

- 一个超级管理员账号，来源于 `ADMIN_*` 环境变量。
- 一个默认普通用户账号，来源于 `DEFAULT_USER_*` 环境变量。
- 默认站点设置和默认普通用户简历信息。

如果使用阿里云 RDS，请把 Web 服务器公网 IP 加入 RDS 白名单；如果 Web 服务器和 RDS 在同一 VPC，优先使用内网地址。

## 六、旧版数据库升级

如果数据库已经运行过旧版单用户简历网站，请先备份数据库，再执行：

```sql
database/migrations/2026-05-12-multi-user-upgrade.sql
```

该脚本会：

- 创建 `users` 表。
- 从旧 `admin_users` 表迁移一个超级管理员账号。
- 创建默认普通用户 `demo`。
- 给简历、留言、上传相关表补充 `user_id` 或 `target_user_id`。
- 把旧版已有简历数据绑定到默认普通用户。

该迁移脚本只建议在备份后执行一次。执行完成后，请再运行应用测试或手动检查 `/u/demo` 页面是否能正常打开。

## 七、本地运行

```powershell
flask --app run run --debug
```

- 前台地址：`http://127.0.0.1:5000/`
- 用户注册：`http://127.0.0.1:5000/auth/register`
- 用户登录：`http://127.0.0.1:5000/auth/login`
- 普通用户后台：`http://127.0.0.1:5000/dashboard`
- 超级管理员后台：`http://127.0.0.1:5000/admin`

## 八、生产部署概览

```bash
cd /opt/resume-site
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

生产环境请编辑 `/opt/resume-site/.env`。建议使用足够长的随机 `SECRET_KEY`，并设置：

```text
SESSION_COOKIE_SECURE=1
```

如果 systemd 服务使用 `www-data` 运行应用，请让 `.env` 对服务用户可读，但不要公开给其他用户：

```bash
sudo chown root:www-data /opt/resume-site/.env
sudo chmod 640 /opt/resume-site/.env
```

部署示例文件位于 `deployment/`：

- `gunicorn.conf.py`
- `nginx.conf.example`
- `resume-site.service.example`

常见服务命令：

```bash
sudo systemctl status resume-site
sudo systemctl restart resume-site
sudo systemctl status nginx
sudo systemctl restart nginx
sudo nginx -t
```

## 九、测试

```bash
pytest -v
python -m compileall app
```

当前测试覆盖：

- 数据库结构契约。
- 用户注册和登录。
- 角色权限。
- 用户后台数据隔离。
- 公开简历列表和用户主页。
- 多用户留言。
- 上传文件校验。
