# 个人简历网站

这是一个基于 Flask + MySQL 的响应式个人简历网站，采用 Bootstrap 后台管理页面和 Jinja2 服务端渲染。项目适合部署在 Web 服务器与数据库服务器分离的环境中，例如 Linux Web 服务器连接阿里云 RDS MySQL。

## 技术栈

- 前端：HTML5、CSS3、Bootstrap 5、JavaScript、jQuery、Jinja2。
- 后端：Python 3、Flask、PyMySQL、Werkzeug、Flask-WTF、Flask-Limiter。
- 数据库：MySQL 8.0 或阿里云 RDS MySQL，字符集使用 `utf8mb4`。
- 部署：Linux、Nginx、Gunicorn、systemd。

本项目是前后端不分离的服务端渲染架构。数据库地址、账号、密码等信息通过 `.env` 配置，代码仓库中不会保存真实密钥。

## 本地安装

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

复制 `.env.example` 后，请在 `.env` 中配置：

- `SECRET_KEY`
- `MYSQL_HOST`、`MYSQL_PORT`、`MYSQL_USER`、`MYSQL_PASSWORD`、`MYSQL_DATABASE`
- `ADMIN_USERNAME`、`ADMIN_PASSWORD`、`ADMIN_EMAIL`

不要提交 `.env`，也不要把数据库密码、服务器密码、后台管理员密码发到聊天或工单中。

## 数据库初始化

你的数据库可以先是空库。项目会提供建表 SQL 和初始化数据。

使用阿里云 DMS：

1. 打开 DMS，选择已经创建好的空数据库。
2. 执行 `database/schema.sql` 创建数据表。
3. 在 Web 服务器的 `.env` 中填写 RDS 地址、端口、数据库名、用户名和密码。
4. 在部署目录中运行 `flask --app run seed-db` 初始化管理员和默认内容。

使用 Web 服务器命令行：

```bash
flask --app run init-db
flask --app run seed-db
```

如果使用阿里云 RDS，请把 Web 服务器公网 IP 加入 RDS 白名单；如果 Web 服务器和 RDS 在同一 VPC，优先使用内网地址。

## 本地运行

```powershell
flask --app run run --debug
```

- 前台地址：`http://127.0.0.1:5000/`
- 后台登录：`http://127.0.0.1:5000/admin/login`

## 生产部署概览

```bash
cd /opt/resume-site
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

生产环境请编辑 `/opt/resume-site/.env`。建议使用足够长的随机 `SECRET_KEY`，设置 `SESSION_COOKIE_SECURE=1`。如果有多个 Gunicorn worker 或多台 Web 服务器，建议把 `RATELIMIT_STORAGE_URI` 配置为 Redis。

部署示例文件位于 `deployment/`：

- `gunicorn.conf.py`
- `nginx.conf.example`
- `resume-site.service.example`

常见服务启动步骤：

```bash
sudo cp deployment/resume-site.service.example /etc/systemd/system/resume-site.service
sudo systemctl daemon-reload
sudo systemctl enable --now resume-site
sudo nginx -t
sudo systemctl reload nginx
```

## 测试

```bash
pytest -v
python -m compileall app
```
