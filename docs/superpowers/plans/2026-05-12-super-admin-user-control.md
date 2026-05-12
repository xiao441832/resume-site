# 超级管理员用户管控 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将系统改造成“超级管理员 + 普通用户”两类账号，并让超级管理员可以查看全站状态、封禁账号、禁止发布和封禁公开简历。

**Architecture:** 继续使用统一 `users` 表承载登录账号，`role` 只保留 `super_admin` 和 `user`。超级管理员进入 `/admin` 管理全站；普通用户进入 `/dashboard` 管理自己的简历，公开展示由账号状态、发布权限和简历封禁状态共同决定。

**Tech Stack:** Python 3、Flask、Jinja2、PyMySQL、Flask-WTF、Werkzeug、MySQL 8.0、Bootstrap 5。

---

## 文件结构

- 修改 `database/schema.sql`：更新角色枚举，增加账号发布权限和封禁原因字段，增加公开简历封禁字段。
- 新增 `database/migrations/2026-05-12-super-admin-controls.sql`：给线上已有库执行增量迁移。
- 修改 `database/seed.sql`：保持站点设置种子数据，账号种子仍由 CLI 生成。
- 修改 `app/cli.py`：初始化超级管理员和演示普通用户，默认角色写入 `super_admin`。
- 修改 `app/auth/decorators.py`：增加 `is_super_admin()` 和 `super_admin_required()`。
- 修改 `app/auth/routes.py`：登录判断 `super_admin`，被封禁用户不能登录。
- 修改 `app/admin/routes.py`：增加用户管理、用户详情、账号状态、发布状态、公开简历状态路由；普通用户公开保存时遵守发布权限。
- 修改 `app/admin/forms.py`：增加三个超级管理员操作表单。
- 新增 `app/templates/admin/users.html`：超级管理员用户列表。
- 新增 `app/templates/admin/user_detail.html`：超级管理员用户详情和操作表单。
- 修改 `app/templates/admin/layout.html`：超级管理员后台显示“用户管理”，文案保持中文。
- 修改 `app/templates/admin/dashboard.html`：增强超级管理员系统概览数据。
- 修改 `app/templates/admin/profile.html`：普通用户后台展示发布限制和公开封禁提示。
- 修改 `app/public/routes.py`：公开列表、公开详情和留言提交过滤新增状态。
- 修改 `tests/test_auth.py`、`tests/test_admin_pages.py`、`tests/test_public.py`、`tests/test_cli.py`：补充行为测试。
- 修改 `README.md`：用中文说明超级管理员和普通用户的账号区别与功能。

## Task 1: 数据库结构和初始化角色

**Files:**
- Modify: `database/schema.sql`
- Create: `database/migrations/2026-05-12-super-admin-controls.sql`
- Modify: `app/cli.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: 写失败测试**

在 `tests/test_cli.py` 增加：

```python
def test_schema_sql_contains_super_admin_control_fields():
    schema = Path("database/schema.sql").read_text(encoding="utf-8")
    users = table_block(schema, "users")
    profile = table_block(schema, "profile")

    assert "role ENUM('super_admin','user') NOT NULL DEFAULT 'user'" in users
    assert "can_publish TINYINT(1) NOT NULL DEFAULT 1" in users
    assert "ban_reason VARCHAR(255) NULL" in users
    assert "publish_ban_reason VARCHAR(255) NULL" in users
    assert "is_public_blocked TINYINT(1) NOT NULL DEFAULT 0" in profile
    assert "public_block_reason VARCHAR(255) NULL" in profile
```

- [ ] **Step 2: 验证测试失败**

Run: `D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_cli.py::test_schema_sql_contains_super_admin_control_fields -v`

Expected: FAIL，提示新的字段片段不存在。

- [ ] **Step 3: 修改数据库脚本**

在 `database/schema.sql` 中：

```sql
role ENUM('super_admin','user') NOT NULL DEFAULT 'user',
can_publish TINYINT(1) NOT NULL DEFAULT 1,
ban_reason VARCHAR(255) NULL,
publish_ban_reason VARCHAR(255) NULL,
```

在 `profile` 表中：

```sql
is_public_blocked TINYINT(1) NOT NULL DEFAULT 0,
public_block_reason VARCHAR(255) NULL,
```

新增迁移 `database/migrations/2026-05-12-super-admin-controls.sql`，包含：

```sql
ALTER TABLE users MODIFY role ENUM('super_admin','user') NOT NULL DEFAULT 'user';
ALTER TABLE users ADD COLUMN can_publish TINYINT(1) NOT NULL DEFAULT 1 AFTER is_active;
ALTER TABLE users ADD COLUMN ban_reason VARCHAR(255) NULL AFTER can_publish;
ALTER TABLE users ADD COLUMN publish_ban_reason VARCHAR(255) NULL AFTER ban_reason;
UPDATE users SET role = 'super_admin' WHERE role = 'admin';
ALTER TABLE profile ADD COLUMN is_public_blocked TINYINT(1) NOT NULL DEFAULT 0 AFTER is_active;
ALTER TABLE profile ADD COLUMN public_block_reason VARCHAR(255) NULL AFTER is_public_blocked;
```

将 `app/cli.py` 中管理员创建角色改为 `super_admin`，演示用户仍为 `user`。

- [ ] **Step 4: 验证通过**

Run: `D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_cli.py -v`

Expected: PASS。

- [ ] **Step 5: 提交**

```bash
git add database/schema.sql database/migrations/2026-05-12-super-admin-controls.sql app/cli.py tests/test_cli.py
git commit -m "feat: 增加超级管理员账号结构"
```

## Task 2: 登录和权限语义

**Files:**
- Modify: `app/auth/decorators.py`
- Modify: `app/auth/routes.py`
- Test: `tests/test_auth.py`

- [ ] **Step 1: 写失败测试**

在 `tests/test_auth.py` 增加：

```python
def test_super_admin_login_redirects_to_admin_dashboard(client, monkeypatch):
    monkeypatch.setattr(
        "app.auth.routes.find_user_by_login",
        lambda login_name: {
            "id": 1,
            "username": "admin",
            "email": "admin@example.com",
            "password_hash": generate_password_hash("secret123"),
            "display_name": "超级管理员",
            "role": "super_admin",
            "is_active": 1,
        },
    )
    monkeypatch.setattr("app.auth.routes.mark_last_login", lambda user_id: None)

    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "secret123"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin")
```

再增加普通 `admin` 角色不再被当作超级管理员的测试，确保只认 `super_admin`。

- [ ] **Step 2: 验证测试失败**

Run: `D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_auth.py::test_super_admin_login_redirects_to_admin_dashboard -v`

Expected: FAIL，当前只判断 `role == "admin"`。

- [ ] **Step 3: 实现权限语义**

在 `app/auth/decorators.py` 增加：

```python
def is_super_admin() -> bool:
    return current_user_role() == "super_admin"

def super_admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not current_user_id():
            flash("请先登录。", "warning")
            return redirect(url_for("auth.login"))
        if not is_super_admin():
            abort(403)
        return view(*args, **kwargs)

    return wrapped_view
```

在 `app/auth/routes.py` 将登录跳转改为 `role == "super_admin"`。

- [ ] **Step 4: 验证通过**

Run: `D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_auth.py -v`

Expected: PASS。

- [ ] **Step 5: 提交**

```bash
git add app/auth/decorators.py app/auth/routes.py tests/test_auth.py
git commit -m "feat: 调整超级管理员登录权限"
```

## Task 3: 超级管理员用户管理

**Files:**
- Modify: `app/admin/forms.py`
- Modify: `app/admin/routes.py`
- Modify: `app/templates/admin/layout.html`
- Create: `app/templates/admin/users.html`
- Create: `app/templates/admin/user_detail.html`
- Test: `tests/test_admin_pages.py`

- [ ] **Step 1: 写失败测试**

在 `tests/test_admin_pages.py` 增加：

```python
def login_super_admin(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["username"] = "admin"
        session["role"] = "super_admin"
        session["display_name"] = "超级管理员"

def test_super_admin_can_view_user_list(client, monkeypatch):
    login_super_admin(client)
    monkeypatch.setattr(
        "app.admin.routes.query_all",
        lambda sql, params=None: [
            {
                "id": 2,
                "username": "demo",
                "display_name": "演示用户",
                "email": "demo@example.com",
                "is_active": 1,
                "can_publish": 1,
                "is_public_blocked": 0,
                "created_at": "2026-05-12",
                "last_login_at": None,
            }
        ],
    )

    response = client.get("/admin/users")

    assert response.status_code == 200
    assert "演示用户".encode("utf-8") in response.data
```

增加普通用户访问 `/admin/users` 返回 403 的测试。

- [ ] **Step 2: 验证测试失败**

Run: `D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_admin_pages.py::test_super_admin_can_view_user_list -v`

Expected: FAIL，当前没有 `/admin/users` 路由。

- [ ] **Step 3: 实现用户管理**

新增三个表单：

```python
class AccountStatusForm(FlaskForm):
    is_active = BooleanField("启用账号")
    ban_reason = TextAreaField("封禁原因", validators=[Optional(), Length(max=255)])
    submit = SubmitField("保存账号状态")
```

发布权限和公开简历状态使用相同模式，字段名分别为 `can_publish/publish_ban_reason`、`is_public_blocked/public_block_reason`。

在 `app/admin/routes.py` 增加：

```python
@admin_bp.route("/users")
@super_admin_required
def users():
    ...

@admin_bp.route("/users/<int:user_id>")
@super_admin_required
def user_detail(user_id):
    ...
```

并实现三个 `POST` 状态更新路由。

- [ ] **Step 4: 验证通过**

Run: `D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_admin_pages.py -v`

Expected: PASS。

- [ ] **Step 5: 提交**

```bash
git add app/admin/forms.py app/admin/routes.py app/templates/admin/layout.html app/templates/admin/users.html app/templates/admin/user_detail.html tests/test_admin_pages.py
git commit -m "feat: 增加超级管理员用户管理"
```

## Task 4: 发布限制和公开展示过滤

**Files:**
- Modify: `app/admin/routes.py`
- Modify: `app/templates/admin/profile.html`
- Modify: `app/public/routes.py`
- Test: `tests/test_public.py`
- Test: `tests/test_admin_pages.py`

- [ ] **Step 1: 写失败测试**

在 `tests/test_public.py` 增加公开过滤断言，期望 SQL 包含：

```python
assert "u.can_publish = 1" in captured_sql
assert "p.is_public_blocked = 0" in captured_sql
```

在 `tests/test_admin_pages.py` 增加普通用户被禁止发布时，提交公开状态会被强制关闭的测试。

- [ ] **Step 2: 验证测试失败**

Run: `D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_public.py tests/test_admin_pages.py -v`

Expected: FAIL，当前 SQL 和保存逻辑还没有新限制。

- [ ] **Step 3: 实现过滤和限制**

在 `app/public/routes.py` 的公开查询中增加：

```sql
AND u.can_publish = 1
AND p.is_public_blocked = 0
```

在普通用户保存个人信息前查询当前用户权限，如果 `can_publish = 0`，强制 `is_active = 0` 并提示“当前账号已被禁止发布，不能公开简历。”。

- [ ] **Step 4: 验证通过**

Run: `D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_public.py tests/test_admin_pages.py -v`

Expected: PASS。

- [ ] **Step 5: 提交**

```bash
git add app/admin/routes.py app/templates/admin/profile.html app/public/routes.py tests/test_public.py tests/test_admin_pages.py
git commit -m "feat: 限制被管控用户公开简历"
```

## Task 5: 文档、全量测试和部署准备

**Files:**
- Modify: `README.md`
- Modify: `docs/superpowers/specs/2026-05-12-super-admin-user-control-design.md`
- Test: all tests

- [ ] **Step 1: 更新中文文档**

在 `README.md` 增加“账号类型与后台权限”说明：

```markdown
## 账号类型与后台权限

系统只区分超级管理员和普通用户。超级管理员用于管理全站账号、公开简历和系统设置；普通用户用于维护自己的在线简历。
```

- [ ] **Step 2: 运行全量验证**

Run:

```powershell
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest -v
D:\Github\resume-site\.venv\Scripts\python.exe -m compileall app
git diff --check
```

Expected: 全部通过。

- [ ] **Step 3: 提交**

```bash
git add README.md docs/superpowers/specs/2026-05-12-super-admin-user-control-design.md docs/superpowers/plans/2026-05-12-super-admin-user-control.md
git commit -m "docs: 更新超级管理员功能说明"
```

- [ ] **Step 4: 部署准备**

确认待部署内容：

```bash
git status --short
git log --oneline -5
```

Expected: 工作区干净，最近提交均为中文说明。

## 自查结果

- 设计文档中的超级管理员概览、用户管理、账号封禁、禁止发布、封禁公开简历、公开展示过滤、部署影响均有对应任务。
- 本计划没有保留待定项或占位项。
- 角色名统一使用 `super_admin` 和 `user`，不再新增第三类后台角色。
