# Python + MySQL Personal Resume Site Design

Date: 2026-05-09

## 1. Goal

Build a responsive personal resume website using Python, Flask, MySQL, Bootstrap, Jinja2, and server-side rendering. The site has a public resume homepage and a custom administrator backend for managing resume content.

The database already exists on a separate database server, but it is empty. The project must therefore include a clear database schema, seed data, and an initialization workflow that supports both manual execution through Aliyun DMS and command-line initialization from the web server.

## 2. Confirmed Technology Stack

Frontend:

- HTML5 for page structure.
- CSS3 for page styling.
- Bootstrap 5 for responsive layout, buttons, tables, forms, and cards.
- JavaScript and optional jQuery for lightweight interactions.
- Jinja2 templates rendered by Flask.

Backend:

- Python 3.
- Flask.
- PyMySQL for MySQL access.
- Werkzeug for password hashing and basic security utilities.
- Flask-WTF for form validation and CSRF protection.
- Flask-Limiter for login and message submission rate limiting.
- Gunicorn for production runtime.
- Nginx for reverse proxy and static file service.

Database:

- MySQL 8.0.
- Aliyun RDS MySQL compatible deployment.
- DMS for online schema execution and data management.
- `utf8mb4` character set for Chinese and special characters.

Deployment:

- Linux web server.
- Gunicorn application process.
- Nginx reverse proxy.
- systemd service management.
- Flask server-side rendering, B/S architecture, one MySQL database instance.

Explicit frontend exclusions:

- No Vue.
- No React.
- No Angular.
- No frontend router.
- No frontend state management.
- No separated frontend/backend build deployment.

## 3. Recommended Implementation Approach

Use a modular Flask application with explicit SQL and PyMySQL.

This approach keeps the project aligned with the requested stack and makes database behavior easy to inspect. It avoids ORM abstraction and keeps SQL files usable in Aliyun DMS. The backend will be split into Flask blueprints for public pages, authentication, and administration.

The project will provide both:

- `database/schema.sql` for DMS/manual table creation.
- Flask CLI commands such as `flask init-db` and `flask seed-db` for command-line initialization.

## 4. Project Structure

```text
resume-site/
  app/
    __init__.py
    config.py
    db.py
    auth/
      routes.py
      forms.py
    public/
      routes.py
      forms.py
    admin/
      routes.py
      forms.py
    services/
      upload_service.py
    templates/
      base.html
      public/
        index.html
      admin/
        layout.html
        dashboard.html
        list.html
        form.html
      auth/
        login.html
    static/
      css/
        main.css
      js/
        main.js
      uploads/
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

Primary boundaries:

- `public`: public resume homepage and message submission.
- `auth`: administrator login, logout, session handling, and login rate limiting.
- `admin`: backend CRUD screens.
- `db.py`: central MySQL connection, query, and transaction helpers.
- `services/upload_service.py`: file upload validation and storage.
- `database`: schema and seed SQL suitable for DMS execution.
- `deployment`: production deployment examples.

## 5. Database Design

All tables use MySQL 8.0, InnoDB, `utf8mb4`, and `utf8mb4_unicode_ci`. Primary keys use `BIGINT UNSIGNED AUTO_INCREMENT`. Sortable content uses `sort_order`. Publicly visible content uses `is_active`.

Core tables:

- `admin_users`: administrator accounts. Stores username, password hash, display name, email, enabled state, last login time, and timestamps. Passwords are never stored in plain text.
- `profile`: personal profile, normally one active row. Stores name, title, city, email, phone, WeChat, GitHub, personal site, avatar path, resume file path, summary, and job status.
- `skills`: skill name, category, proficiency percentage, optional icon/color, sort order, visible state, and timestamps.
- `experiences`: work or internship experience. Stores company, position, location, start date, end date, current flag, description, sort order, visible state, and timestamps.
- `projects`: project experience. Stores project name, role, technology stack, project URL, source URL, cover image, start/end dates, summary, highlights, sort order, visible state, and timestamps.
- `education`: school, major, degree, location, start/end dates, description, sort order, visible state, and timestamps.
- `certificates`: certificate name, issuer, issue date, certificate URL, certificate image, description, sort order, visible state, and timestamps.
- `messages`: visitor messages. Stores name, email, optional phone, content, IP address, user agent, status, administrator note, and timestamps.

Auxiliary tables:

- `uploads`: uploaded file records. Stores original filename, saved filename, relative path, MIME type, file size, upload purpose, uploader ID, and created time.
- `site_settings`: key-value site settings. Stores setting key, value, type, description, and updated time.

Database safety requirements:

- Use parameterized SQL for all runtime queries.
- Use a dedicated MySQL account with permissions limited to the resume database.
- Store only relative paths for uploaded files; files live on the web server.
- Do not store uploaded binary data in MySQL.
- Create initial administrator through seed data or `flask seed-db`.
- The initial administrator password is supplied through environment configuration.

## 6. Public Website Design

The public site is a single responsive resume homepage served from `GET /`.

Sections:

- Navigation bar with site name and anchors for skills, experience, projects, education, certificates, and contact.
- Hero/profile area with avatar, name, title, city, summary, contact button, and resume download button.
- Skills grouped by category, displayed with badges or Bootstrap progress bars.
- Work/internship timeline with company, position, date range, location, and description.
- Project card grid with cover image, name, tech stack, summary, highlights, project URL, and source URL.
- Education section using a compact list or timeline.
- Certificates section using cards or a list, optionally with images and external links.
- Contact/message form with name, email, optional phone, and message content.
- Footer with copyright, record filing information, and social links.
- Back-to-top button controlled by JavaScript/jQuery.

Responsive behavior:

- Desktop: centered content container, project cards in two or three columns.
- Tablet: project cards in two columns.
- Mobile: collapsed navigation, one-column content, compact timeline layout.
- Avatar and cover images use stable aspect ratios to reduce layout shifts.

## 7. Administrator Backend Design

The custom administrator backend is under `/admin` and requires login.

Pages:

- `/admin/login`: administrator login page using Flask-WTF, CSRF protection, and Flask-Limiter.
- `/admin`: dashboard with counts for skills, projects, messages, unread messages, and recent messages.
- `/admin/profile`: edit personal profile, avatar, and resume PDF.
- `/admin/skills`: list, create, edit, delete, show/hide, and sort skills.
- `/admin/experiences`: manage work and internship experience.
- `/admin/projects`: manage project experience and project cover images.
- `/admin/education`: manage education records.
- `/admin/certificates`: manage certificates and certificate images.
- `/admin/messages`: view messages, mark status, add administrator note, and delete messages.
- `/admin/settings`: manage site title, SEO description, record filing text, and message form availability.
- `/admin/logout`: log out and clear session.

Backend UI:

- Bootstrap 5 top bar and sidebar.
- Table list pages with search field, status badges, edit/delete buttons, and enable/disable controls.
- Bootstrap form pages.
- Delete confirmation dialogs.
- Upload image preview using JavaScript/jQuery.
- Flask flash messages rendered as Bootstrap alerts.

## 8. Routes and Data Flow

Public routes:

- `GET /`: read active profile, skills, experiences, projects, education, certificates, and settings, then render the public homepage.
- `POST /messages`: validate CSRF and form fields, apply rate limit, check whether messages are enabled, insert into `messages`, and return a success or failure flash message.

Authentication routes:

- `GET /admin/login`: render login form.
- `POST /admin/login`: validate credentials, set session, update last login time.
- `POST /admin/logout`: clear session.

Administration routes:

- `GET /admin`: dashboard.
- `GET|POST /admin/profile`: edit profile.
- `GET /admin/<module>`: list records.
- `GET|POST /admin/<module>/new`: create record.
- `GET|POST /admin/<module>/<id>/edit`: edit record.
- `POST /admin/<module>/<id>/delete`: delete record.
- `POST /admin/<module>/<id>/toggle`: enable or disable record.
- `POST /admin/<module>/<id>/sort`: adjust sort order.
- `POST /admin/messages/<id>/status`: update message status.

Public display flow:

1. Browser requests `/`.
2. Flask reads visible resume content from remote MySQL.
3. Jinja2 renders HTML.
4. Bootstrap and custom CSS handle layout.
5. JavaScript/jQuery handles small interactions.

Message submission flow:

1. Visitor submits the message form.
2. Flask-WTF validates CSRF and field constraints.
3. Flask-Limiter applies a submission rate limit.
4. Flask inserts the message into MySQL.
5. The user sees a flash success or error message.

Administrator flow:

1. Administrator logs in.
2. Session stores administrator ID.
3. Protected routes require an authenticated session.
4. Submitted forms pass Flask-WTF validation.
5. PyMySQL executes parameterized CRUD SQL.
6. Flask redirects with a flash message.

Upload flow:

1. Administrator uploads an avatar, resume PDF, project cover, or certificate image.
2. The server validates extension, MIME type, and file size.
3. The file is saved under `app/static/uploads/` using a UUID filename.
4. MySQL stores the relative path and upload metadata.
5. In production, Nginx serves uploaded static files.

## 9. Security Design

- Use Werkzeug `generate_password_hash` and `check_password_hash` for administrator passwords.
- Use Flask-WTF CSRF protection for all forms.
- Rate-limit login attempts, for example `5 per minute`.
- Rate-limit message submissions, for example `3 per minute`.
- Use parameterized SQL for every database query.
- Restrict upload types to images (`jpg`, `jpeg`, `png`, `webp`, `gif`) and PDF for resume files.
- Restrict upload sizes, for example 2 MB for images and 5 MB for PDF files.
- Generate uploaded filenames with UUIDs.
- Read `SECRET_KEY` from environment variables.
- Enable `SESSION_COOKIE_HTTPONLY=True`.
- Enable `SESSION_COOKIE_SECURE=True` in HTTPS production deployments.
- Keep `.env` out of version control and provide `.env.example`.
- Use a least-privilege database account for the resume database.

## 10. Deployment Design

The web server and database server are separate.

Web server:

- Linux.
- Python virtual environment.
- Flask application.
- Gunicorn process.
- Nginx reverse proxy and static file service.
- systemd process management.

Database server:

- Aliyun RDS MySQL 8.0 or compatible MySQL 8.0 server.
- Existing database name, currently empty.
- Database initialized through DMS or Flask CLI.

Configuration:

- `.env` stores database host, port, database name, username, password, Flask secret key, administrator seed username, and administrator seed password.
- `.env.example` documents required environment variables without real secrets.

Deployment files:

- `deployment/gunicorn.conf.py`
- `deployment/nginx.conf.example`
- `deployment/resume-site.service.example`

Initialization workflow:

1. Confirm the RDS database exists and uses `utf8mb4`.
2. Execute `database/schema.sql` in Aliyun DMS, or run `flask init-db` from the web server.
3. Configure `.env` on the web server.
4. Run `flask seed-db` to create the initial administrator and optional sample content.
5. Start Gunicorn through systemd.
6. Configure Nginx to proxy the domain to Gunicorn and serve static/uploads.
7. Log in to `/admin/login` and update resume content.

## 11. Testing Strategy

Tests should focus on behavior and risk:

- Database helper tests for parameterized query execution and transaction handling.
- Authentication tests for login success, login failure, logout, and protected route access.
- Public route tests for homepage rendering with seeded resume data.
- Message form tests for valid submission, invalid submission, disabled message setting, and rate-limited behavior.
- Admin CRUD tests for at least one representative content module, then shared helper coverage for other modules.
- Upload service tests for allowed file types, blocked file types, max size behavior, and UUID naming.

Implementation should use test-driven development for new behavior: write the failing test first, confirm it fails for the expected reason, implement the smallest change, then confirm the test passes.

## 12. Acceptance Criteria

- The public homepage renders resume data from MySQL through Jinja2.
- The homepage is responsive on desktop, tablet, and mobile.
- The administrator can log in and log out.
- The administrator can manage profile, skills, experiences, projects, education, certificates, messages, uploads, and settings.
- Passwords are hashed and never stored in plain text.
- Forms use CSRF protection.
- Login and message submission are rate-limited.
- SQL uses parameterized queries.
- Uploads are validated and stored on the web server, with only paths stored in MySQL.
- The project includes `schema.sql`, `seed.sql`, `flask init-db`, and `flask seed-db`.
- The project includes deployment examples for Gunicorn, Nginx, and systemd.
- The project includes `.env.example` and does not commit real secrets.
