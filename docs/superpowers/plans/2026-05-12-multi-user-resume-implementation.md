# 多用户在线简历管理系统 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将现有单用户个人简历网站改造成支持普通用户注册、登录、独立维护简历、公开展示和超级管理员管理的多用户在线简历管理系统。

**Architecture:** 保留 Flask + Jinja2 服务端渲染架构，新增统一 `users` 账号表，用 `role` 区分普通用户和超级管理员。简历、留言、上传等业务数据通过 `user_id` 或 `target_user_id` 做数据隔离，公开页面通过 `/u/<username>` 展示指定用户的公开简历。

**Tech Stack:** Python 3、Flask、PyMySQL、Werkzeug、Flask-WTF、Flask-Limiter、MySQL 8.0、Bootstrap 5、Jinja2。

---

### Task 1: 数据库结构升级

**Files:**
- Modify: `database/schema.sql`
- Modify: `database/seed.sql`
- Modify: `app/cli.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write failing schema tests**

Add assertions that `schema.sql` contains `users`, `user_id`, `target_user_id`, and user-scoped indexes.

- [ ] **Step 2: Run schema tests to verify failure**

Run: `.venv\Scripts\python.exe -m pytest tests/test_cli.py -v`

Expected: tests fail because the current schema still uses single-user tables.

- [ ] **Step 3: Add unified user table and scoped columns**

Update `schema.sql` so it creates:

```sql
CREATE TABLE IF NOT EXISTS users (... role ENUM('user','admin') ...);
```

Add `user_id` to `profile`, `skills`, `experiences`, `projects`, `education`, `certificates`, `uploads`; add `target_user_id` to `messages`.

- [ ] **Step 4: Update seed command**

Modify `seed-db` so it creates one admin user and one demo normal user in `users`, then binds seeded profile data to the demo user.

- [ ] **Step 5: Run tests**

Run: `.venv\Scripts\python.exe -m pytest tests/test_cli.py -v`

- [ ] **Step 6: Commit**

Commit message: `feat: 增加多用户数据库结构`

### Task 2: 统一认证与权限

**Files:**
- Modify: `app/auth/forms.py`
- Modify: `app/auth/routes.py`
- Modify: `app/auth/decorators.py`
- Modify: `app/__init__.py`
- Modify: `app/templates/auth/login.html`
- Create: `app/templates/auth/register.html`
- Test: `tests/test_auth.py`

- [ ] **Step 1: Write failing auth tests**

Cover registration, login, disabled user rejection, admin route protection, and user route protection.

- [ ] **Step 2: Run auth tests to verify failure**

Run: `.venv\Scripts\python.exe -m pytest tests/test_auth.py -v`

- [ ] **Step 3: Implement register/login/logout**

Move public auth routes to `/auth`, save `user_id`、`username`、`display_name`、`role` into session, and keep `/admin/login` redirecting to `/auth/login` for compatibility.

- [ ] **Step 4: Implement decorators**

Provide `login_required` and `admin_required`; keep messages in Chinese.

- [ ] **Step 5: Run tests**

Run: `.venv\Scripts\python.exe -m pytest tests/test_auth.py -v`

- [ ] **Step 6: Commit**

Commit message: `feat: 增加用户注册登录和角色权限`

### Task 3: 用户后台数据隔离

**Files:**
- Modify: `app/admin/resources.py`
- Modify: `app/admin/routes.py`
- Modify: `app/admin/forms.py`
- Modify: `app/templates/admin/*.html`
- Test: `tests/test_admin_pages.py`
- Test: `tests/test_admin_resources.py`

- [ ] **Step 1: Write failing data-isolation tests**

Verify ordinary users only list, edit, update, and delete their own resources.

- [ ] **Step 2: Run admin tests to verify failure**

Run: `.venv\Scripts\python.exe -m pytest tests/test_admin_pages.py tests/test_admin_resources.py -v`

- [ ] **Step 3: Scope all resource SQL by current user**

Add `user_id = session["user_id"]` to user dashboard queries. Inserts automatically include current user id.

- [ ] **Step 4: Split user dashboard and admin dashboard**

Use `/dashboard` for normal users and `/admin` for super administrators.

- [ ] **Step 5: Run tests**

Run: `.venv\Scripts\python.exe -m pytest tests/test_admin_pages.py tests/test_admin_resources.py -v`

- [ ] **Step 6: Commit**

Commit message: `feat: 增加用户后台数据隔离`

### Task 4: 公开简历列表和用户主页

**Files:**
- Modify: `app/public/routes.py`
- Modify: `app/templates/public/index.html`
- Create: `app/templates/public/resume.html`
- Test: `tests/test_public.py`

- [ ] **Step 1: Write failing public tests**

Verify `/` displays public resume cards, `/u/<username>` displays one user's resume, hidden resumes return 404.

- [ ] **Step 2: Run public tests to verify failure**

Run: `.venv\Scripts\python.exe -m pytest tests/test_public.py -v`

- [ ] **Step 3: Implement public listing and user resume page**

Load data by `users.username` and scope all resume queries by `user_id`.

- [ ] **Step 4: Run tests**

Run: `.venv\Scripts\python.exe -m pytest tests/test_public.py -v`

- [ ] **Step 5: Commit**

Commit message: `feat: 增加公开简历列表和用户主页`

### Task 5: 多用户留言

**Files:**
- Modify: `app/public/routes.py`
- Modify: `app/templates/public/resume.html`
- Modify: `app/admin/routes.py`
- Modify: `app/templates/admin/messages.html`
- Test: `tests/test_public.py`
- Test: `tests/test_admin_pages.py`

- [ ] **Step 1: Write failing message tests**

Verify posting to `/u/<username>/messages` writes `target_user_id` and normal users only see their own messages.

- [ ] **Step 2: Run message tests to verify failure**

Run: `.venv\Scripts\python.exe -m pytest tests/test_public.py tests/test_admin_pages.py -v`

- [ ] **Step 3: Implement targeted messages**

Change message submission to route through usernames and store `target_user_id`.

- [ ] **Step 4: Run tests**

Run: `.venv\Scripts\python.exe -m pytest tests/test_public.py tests/test_admin_pages.py -v`

- [ ] **Step 5: Commit**

Commit message: `feat: 增加多用户留言管理`

### Task 6: 文档、迁移说明和全量验证

**Files:**
- Modify: `README.md`
- Create: `database/migrations/2026-05-12-multi-user-upgrade.sql`
- Modify: `docs/superpowers/specs/2026-05-12-multi-user-resume-system-design.md`
- Test: all tests

- [ ] **Step 1: Add Chinese migration document**

Create migration SQL for existing production database: create `users`, add scoped columns, bind existing data to demo user.

- [ ] **Step 2: Update README**

Document new system name, routes, roles, initialization, and deployment notes in Simplified Chinese.

- [ ] **Step 3: Run full verification**

Run:

```powershell
.venv\Scripts\python.exe -m pytest -v
.venv\Scripts\python.exe -m compileall app
git diff --check
```

- [ ] **Step 4: Commit**

Commit message: `docs: 更新多用户系统部署和迁移说明`
