# Resume Site

Flask + MySQL responsive personal resume website with a Bootstrap administrator backend.

## Tech Stack

- Frontend: HTML5, CSS3, Bootstrap 5, JavaScript, jQuery, Jinja2.
- Backend: Python 3, Flask, PyMySQL, Werkzeug, Flask-WTF, Flask-Limiter.
- Database: MySQL 8.0 or Aliyun RDS MySQL, using `utf8mb4`.
- Deployment: Linux, Nginx, Gunicorn, systemd.

The application is server-rendered. The web server and MySQL server can be separate machines; configure the database host in `.env`.

## Local Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set:

- `SECRET_KEY`
- `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`
- `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `ADMIN_EMAIL`

Do not commit `.env`, and do not put database passwords in chat or issue trackers.

## Database Initialization

Your existing database can start empty.

Using Aliyun DMS:

1. Open DMS and select the existing empty database.
2. Execute `database/schema.sql`.
3. Configure `.env` on the web server with the RDS endpoint and credentials.
4. Run `flask --app run seed-db` from the deployed project directory.

Using command line from the web server:

```bash
flask --app run init-db
flask --app run seed-db
```

For Aliyun RDS, add the web server IP to the RDS whitelist or keep both servers in the same VPC and use the internal RDS endpoint when available.

## Run Locally

```powershell
flask --app run run --debug
```

- Public site: `http://127.0.0.1:5000/`
- Admin login: `http://127.0.0.1:5000/admin/login`

## Production Outline

```bash
cd /opt/resume-site
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `/opt/resume-site/.env` for production. Use a long random `SECRET_KEY`, set `SESSION_COOKIE_SECURE=1`, and set `RATELIMIT_STORAGE_URI` to Redis if multiple Gunicorn workers or multiple web instances are used.

Example deployment files live in `deployment/`:

- `gunicorn.conf.py`
- `nginx.conf.example`
- `resume-site.service.example`

Typical service steps:

```bash
sudo cp deployment/resume-site.service.example /etc/systemd/system/resume-site.service
sudo systemctl daemon-reload
sudo systemctl enable --now resume-site
sudo nginx -t
sudo systemctl reload nginx
```

## Tests

```bash
pytest -v
python -m compileall app
```
