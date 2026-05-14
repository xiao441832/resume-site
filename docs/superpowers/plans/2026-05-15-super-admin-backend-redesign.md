# 超级管理员后台重构 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把超级管理员后台从“复用普通用户简历后台”改造成真正的网站平台管理后台。

**Architecture:** 继续复用 Flask Blueprint 和 Jinja2 模板，但在布局层区分 `admin` 和 `dashboard` 两套菜单。超级管理员只进入平台管理页面：系统控制台、用户管理、简历管理、留言管理、站点设置；普通用户继续使用个人简历维护页面。

**Tech Stack:** Python 3、Flask、Jinja2、Bootstrap 5、PyMySQL、Flask-WTF、MySQL 8.0。

---

## 文件结构

- 修改 `app/admin/routes.py`：新增简历管理路由，增强用户列表和留言查询，限制超级管理员访问旧简历 CRUD 入口。
- 修改 `app/templates/admin/layout.html`：拆分超级管理员和普通用户侧边栏菜单文案。
- 修改 `app/templates/admin/dashboard.html`：把超级管理员首页改成系统控制台。
- 修改 `app/templates/admin/users.html`：增强用户管理列表字段。
- 修改 `app/templates/admin/user_detail.html`：改成账号档案，增加数据概览和查看公开简历入口。
- 新增 `app/templates/admin/resumes.html`：全站简历管理列表。
- 修改 `app/templates/admin/messages.html`：超级管理员视角显示目标用户。
- 修改 `tests/test_admin_pages.py`：覆盖菜单、控制台、简历管理、留言目标用户列、旧入口隔离。
- 修改 `README.md`：说明超级管理员后台已重构为平台管理后台。

## Task 1: 超级管理员菜单和旧入口隔离

**Files:**
- Modify: `app/templates/admin/layout.html`
- Modify: `app/admin/routes.py`
- Test: `tests/test_admin_pages.py`

- [ ] **Step 1: 写失败测试**

在 `tests/test_admin_pages.py` 增加：

```python
def test_super_admin_sidebar_uses_platform_management_menu(client, monkeypatch):
    login_admin(client)
    monkeypatch.setattr("app.admin.routes.query_one", lambda sql, params=None: {"total": 0})
    monkeypatch.setattr("app.admin.routes.query_all", lambda sql, params=None: [])

    response = client.get("/admin")

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    for label in ("控制台", "用户管理", "简历管理", "留言管理", "站点设置"):
        assert label in html
    for label in ("个人信息", "技能", "工作 / 实习经历", "项目经历", "教育经历", "证书"):
        assert label not in html
```

再增加：

```python
def test_normal_user_sidebar_keeps_resume_management_menu(client, monkeypatch):
    login_user(client, user_id=3)
    monkeypatch.setattr("app.admin.routes.query_one", lambda sql, params=None: {"total": 0})
    monkeypatch.setattr("app.admin.routes.query_all", lambda sql, params=None: [])

    response = client.get("/dashboard")

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    for label in ("仪表盘", "个人信息", "技能", "工作 / 实习经历", "项目经历", "教育经历", "证书", "留言管理"):
        assert label in html
```

再增加：

```python
def test_super_admin_old_resume_resource_entry_returns_404(client):
    login_admin(client)

    response = client.get("/admin/skills")

    assert response.status_code == 404
```

- [ ] **Step 2: 验证测试失败**

Run:

```powershell
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_admin_pages.py::test_super_admin_sidebar_uses_platform_management_menu tests/test_admin_pages.py::test_normal_user_sidebar_keeps_resume_management_menu tests/test_admin_pages.py::test_super_admin_old_resume_resource_entry_returns_404 -v
```

Expected: FAIL，因为当前超级管理员仍显示普通用户简历菜单，`/admin/skills` 仍可进入。

- [ ] **Step 3: 实现菜单拆分和旧入口隔离**

在 `app/templates/admin/layout.html` 中：

- `area == 'admin'` 时只显示 `控制台、用户管理、简历管理、留言管理、站点设置`。
- `area == 'dashboard'` 时显示普通用户简历维护菜单。

在 `app/admin/routes.py` 的 `resource_list`、`resource_create`、`resource_edit`、`resource_delete` 开头加入：

```python
if is_admin_area():
    abort(404)
```

在 `profile()` 开头对超级管理员 `/admin/profile` 也返回 404：

```python
if is_admin_area():
    abort(404)
```

- [ ] **Step 4: 验证通过**

Run:

```powershell
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_admin_pages.py -v
```

Expected: PASS。

- [ ] **Step 5: 提交**

```bash
git add app/templates/admin/layout.html app/admin/routes.py tests/test_admin_pages.py
git commit -m "feat: 重构超级管理员后台菜单"
```

## Task 2: 系统控制台增强

**Files:**
- Modify: `app/admin/routes.py`
- Modify: `app/templates/admin/dashboard.html`
- Test: `tests/test_admin_pages.py`

- [ ] **Step 1: 写失败测试**

在 `tests/test_admin_pages.py` 增加：

```python
def test_super_admin_dashboard_is_system_console(client, monkeypatch):
    login_admin(client)

    def fake_query_one(sql, params=None):
        return {"total": 5}

    def fake_query_all(sql, params=None):
        if "FROM users" in sql:
            return [{"id": 2, "username": "demo", "display_name": "演示用户", "email": "demo@example.com", "is_active": 1, "can_publish": 1, "created_at": "2026-05-15"}]
        return [{"name": "访客", "email": "visitor@example.com", "status": "unread", "created_at": "2026-05-15", "target_username": "demo"}]

    monkeypatch.setattr("app.admin.routes.query_one", fake_query_one)
    monkeypatch.setattr("app.admin.routes.query_all", fake_query_all)

    response = client.get("/admin")

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "系统控制台" in html
    assert "快捷操作" in html
    assert "最近注册用户" in html
    assert "最近留言" in html
    assert "target_username" not in html
    assert "demo" in html
```

- [ ] **Step 2: 验证测试失败**

Run:

```powershell
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_admin_pages.py::test_super_admin_dashboard_is_system_console -v
```

Expected: FAIL，因为当前标题和快捷操作不完整，最近留言也没有目标用户信息。

- [ ] **Step 3: 实现系统控制台**

在 `dashboard()` 中把超级管理员最近留言查询改为关联目标用户：

```sql
SELECT m.*, u.username AS target_username, u.display_name AS target_display_name
FROM messages AS m
INNER JOIN users AS u ON u.id = m.target_user_id
ORDER BY m.created_at DESC
LIMIT 5
```

更新 `app/templates/admin/dashboard.html`：

- 标题改为“系统控制台”。
- 增加副标题和快捷操作按钮。
- 最近留言表格增加“目标用户”列。
- 普通用户后台仍显示“仪表盘”。

- [ ] **Step 4: 验证通过**

Run:

```powershell
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_admin_pages.py -v
```

Expected: PASS。

- [ ] **Step 5: 提交**

```bash
git add app/admin/routes.py app/templates/admin/dashboard.html tests/test_admin_pages.py
git commit -m "feat: 优化超级管理员系统控制台"
```

## Task 3: 简历管理页面

**Files:**
- Modify: `app/admin/routes.py`
- Create: `app/templates/admin/resumes.html`
- Test: `tests/test_admin_pages.py`

- [ ] **Step 1: 写失败测试**

在 `tests/test_admin_pages.py` 增加：

```python
def test_super_admin_can_view_resume_management(client, monkeypatch):
    login_admin(client)
    monkeypatch.setattr(
        "app.admin.routes.query_all",
        lambda sql, params=None: [
            {
                "user_id": 2,
                "username": "demo",
                "display_name": "演示用户",
                "name": "张三",
                "title": "Python 工程师",
                "city": "杭州",
                "user_is_active": 1,
                "can_publish": 1,
                "profile_is_active": 1,
                "is_public_blocked": 0,
                "updated_at": "2026-05-15",
            }
        ],
    )

    response = client.get("/admin/resumes")

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "简历管理" in html
    assert "演示用户" in html
    assert "Python 工程师" in html
    assert 'href="/admin/users/2"' in html
    assert 'href="/u/demo"' in html
```

再增加：

```python
def test_normal_user_cannot_view_resume_management(client):
    login_user(client, user_id=3)

    response = client.get("/admin/resumes")

    assert response.status_code == 403
```

- [ ] **Step 2: 验证测试失败**

Run:

```powershell
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_admin_pages.py::test_super_admin_can_view_resume_management tests/test_admin_pages.py::test_normal_user_cannot_view_resume_management -v
```

Expected: FAIL，因为还没有 `/admin/resumes`。

- [ ] **Step 3: 实现简历管理**

新增 `@admin_bp.route("/resumes")`：

- 支持 `status` 筛选：`public`、`hidden`、`publish_banned`、`blocked`、`account_banned`。
- 查询 `users` 和 `profile`。
- 渲染 `admin/resumes.html`。

新增 `admin/resumes.html`：

- 标题“简历管理”。
- 筛选下拉。
- 表格显示用户、简历姓名、职业标题、城市、账号状态、发布权限、公开状态、更新时间、操作。

- [ ] **Step 4: 验证通过**

Run:

```powershell
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_admin_pages.py -v
```

Expected: PASS。

- [ ] **Step 5: 提交**

```bash
git add app/admin/routes.py app/templates/admin/resumes.html tests/test_admin_pages.py
git commit -m "feat: 增加超级管理员简历管理"
```

## Task 4: 用户管理和账号档案增强

**Files:**
- Modify: `app/admin/routes.py`
- Modify: `app/templates/admin/users.html`
- Modify: `app/templates/admin/user_detail.html`
- Test: `tests/test_admin_pages.py`

- [ ] **Step 1: 写失败测试**

在 `tests/test_admin_pages.py` 增加：

```python
def test_user_management_shows_content_and_message_counts(client, monkeypatch):
    login_admin(client)
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
                "content_count": 6,
                "message_count": 2,
                "created_at": "2026-05-15",
                "last_login_at": None,
            }
        ],
    )

    response = client.get("/admin/users")

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "内容数量" in html
    assert "留言数量" in html
    assert ">6<" in html
    assert ">2<" in html
```

再增加：

```python
def test_user_detail_shows_account_archive_sections(client, monkeypatch):
    login_admin(client)

    def fake_query_one(sql, params=None):
        if "COUNT(*) AS total" in sql:
            return {"total": 1}
        return {"id": 2, "username": "demo", "email": "demo@example.com", "display_name": "演示用户", "role": "user", "is_active": 1, "can_publish": 1, "ban_reason": None, "publish_ban_reason": None, "last_login_at": None, "created_at": "2026-05-15"}

    monkeypatch.setattr("app.admin.routes.query_one", fake_query_one)
    monkeypatch.setattr("app.admin.routes.query_all", lambda sql, params=None: [])

    response = client.get("/admin/users/2")

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "账号档案" in html
    assert "简历数据概览" in html
    assert "查看公开简历" in html
```

- [ ] **Step 2: 验证测试失败**

Run:

```powershell
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_admin_pages.py::test_user_management_shows_content_and_message_counts tests/test_admin_pages.py::test_user_detail_shows_account_archive_sections -v
```

Expected: FAIL，因为当前列表和详情页没有这些内容。

- [ ] **Step 3: 实现用户管理增强**

在 `/admin/users` 查询中增加：

```sql
(SELECT COUNT(*) FROM skills WHERE user_id = u.id)
+ (SELECT COUNT(*) FROM experiences WHERE user_id = u.id)
+ (SELECT COUNT(*) FROM projects WHERE user_id = u.id)
+ (SELECT COUNT(*) FROM education WHERE user_id = u.id)
+ (SELECT COUNT(*) FROM certificates WHERE user_id = u.id)
AS content_count,
(SELECT COUNT(*) FROM messages WHERE target_user_id = u.id) AS message_count
```

在 `user_detail()` 中增加 `content_counts` 字典，包括 `skills`、`experiences`、`projects`、`education`、`certificates`、`messages`。

更新模板字段和标题。

- [ ] **Step 4: 验证通过**

Run:

```powershell
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_admin_pages.py -v
```

Expected: PASS。

- [ ] **Step 5: 提交**

```bash
git add app/admin/routes.py app/templates/admin/users.html app/templates/admin/user_detail.html tests/test_admin_pages.py
git commit -m "feat: 增强用户管理账号档案"
```

## Task 5: 留言管理目标用户列和文档

**Files:**
- Modify: `app/admin/routes.py`
- Modify: `app/templates/admin/messages.html`
- Modify: `README.md`
- Test: `tests/test_admin_pages.py`

- [ ] **Step 1: 写失败测试**

在 `tests/test_admin_pages.py` 增加：

```python
def test_super_admin_messages_show_target_user(client, monkeypatch):
    login_admin(client)
    monkeypatch.setattr(
        "app.admin.routes.query_all",
        lambda sql, params=None: [
            {
                "id": 9,
                "name": "访客",
                "email": "visitor@example.com",
                "phone": "",
                "content": "你好",
                "status": "unread",
                "created_at": "2026-05-15",
                "target_username": "demo",
                "target_display_name": "演示用户",
            }
        ],
    )

    response = client.get("/admin/messages")

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "目标用户" in html
    assert "演示用户" in html
    assert "demo" in html
```

- [ ] **Step 2: 验证测试失败**

Run:

```powershell
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_admin_pages.py::test_super_admin_messages_show_target_user -v
```

Expected: FAIL，因为当前留言列表没有目标用户列。

- [ ] **Step 3: 实现留言目标用户列和文档**

在超级管理员 `messages()` 查询中关联 `users`：

```sql
SELECT m.*, u.username AS target_username, u.display_name AS target_display_name
FROM messages AS m
INNER JOIN users AS u ON u.id = m.target_user_id
ORDER BY m.created_at DESC
```

在 `admin/messages.html` 根据 `area == 'admin'` 显示“目标用户”列。

在 `README.md` 增加后台信息架构说明：

```markdown
超级管理员后台使用平台管理菜单：控制台、用户管理、简历管理、留言管理、站点设置。普通用户后台使用简历维护菜单。
```

- [ ] **Step 4: 验证通过**

Run:

```powershell
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_admin_pages.py -v
```

Expected: PASS。

- [ ] **Step 5: 提交**

```bash
git add app/admin/routes.py app/templates/admin/messages.html README.md tests/test_admin_pages.py
git commit -m "feat: 优化后台留言管理展示"
```

## Task 6: 全量验证、线上部署和合并

**Files:**
- Verify: all files

- [ ] **Step 1: 本地全量验证**

Run:

```powershell
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest -v
D:\Github\resume-site\.venv\Scripts\python.exe -m compileall app
git diff --check
```

Expected: 57 个以上测试全部通过，编译通过，`git diff --check` 无错误。

- [ ] **Step 2: 部署到线上**

打包当前分支部署到 `/opt/resume-site`，保留线上 `.env`、`.venv` 和 `app/static/uploads`，重启 `resume-site`。

- [ ] **Step 3: 线上验证**

在服务器运行：

```bash
cd /opt/resume-site
/opt/resume-site/.venv/bin/python -m pytest -v
/opt/resume-site/.venv/bin/python -m compileall app
systemctl is-active resume-site
```

再用 HTTPS 验证：

- 超级管理员登录 `/admin` 看到“系统控制台”。
- 超级管理员侧边栏包含“用户管理、简历管理、留言管理、站点设置”。
- 超级管理员侧边栏不包含“个人信息、技能、项目经历、证书”。
- 普通用户登录 `/dashboard` 仍能看到个人简历维护菜单。
- `/admin/resumes` 可以打开。
- `/admin/messages` 显示目标用户。

- [ ] **Step 4: 合并和推送**

如果线上验证通过：

```bash
cd D:\Github\resume-site
git pull --ff-only origin master
git merge --ff-only codex/admin-backend-redesign
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest -v
git push origin master
git worktree remove D:\Github\resume-site\.worktrees\admin-backend-redesign
git branch -d codex/admin-backend-redesign
```

Expected: `master` 推送成功，工作区干净。

## 自查结果

- 设计文档中的菜单重构、控制台、用户管理、简历管理、留言管理、普通用户后台边界均有对应任务。
- 本计划没有保留待定项或占位项。
- 所有代码行为变更都先写测试，再实现。
- 不新增数据库表，部署风险集中在模板和查询逻辑。
