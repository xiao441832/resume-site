# 全站前端美化 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把公开首页、个人公开简历页、普通用户后台和超级管理员后台统一美化为深蓝 + 科技蓝的稳重专业型界面。

**Architecture:** 继续使用 Flask + Jinja2 服务端渲染，不改变业务路由和数据库结构。美化集中在公共 CSS 变量、模板结构类名、Bootstrap Icons 图标、后台布局和响应式样式上，后端仅在必要时保持现有模板变量不变。

**Tech Stack:** HTML5、CSS3、Bootstrap 5、Bootstrap Icons CDN、JavaScript、jQuery、Jinja2、Python 3、Flask、pytest、Playwright 浏览器验证。

---

## 文件结构

- 修改 `app/static/css/main.css`：定义深蓝科技蓝设计变量，统一按钮、卡片、表格、表单、徽章、前台 Hero、后台布局和响应式样式。
- 修改 `app/templates/base.html`：为公开页面加入 Bootstrap Icons CDN。
- 修改 `app/templates/public/index.html`：优化公开首页导航、Hero、搜索框和公开简历卡片。
- 修改 `app/templates/public/resume.html`：优化个人公开简历页 Hero、联系卡、技能、经历、项目、留言表单。
- 修改 `app/templates/admin/layout.html`：优化后台整体 shell、深色侧边栏、菜单图标、顶部操作区和移动端布局。
- 修改 `app/templates/admin/dashboard.html`：优化普通用户仪表盘和超级管理员控制台统计卡、快捷操作和近期表格。
- 修改 `app/templates/admin/users.html`、`app/templates/admin/resumes.html`、`app/templates/admin/messages.html`：统一后台列表页筛选区、表格、徽章和操作按钮。
- 修改 `app/templates/admin/user_detail.html`：优化账号档案页信息卡和操作表单。
- 修改 `app/templates/admin/resource_list.html`、`app/templates/admin/resource_form.html`、`app/templates/admin/profile.html`、`app/templates/admin/message_detail.html`、`app/templates/admin/settings.html`：统一普通用户后台 CRUD、个人信息、留言详情和站点设置表单。
- 新增 `tests/test_frontend_polish.py`：只验证视觉结构、图标资源、关键类名和菜单边界，不用测试具体像素值。

## Task 1: 全局视觉变量和图标库

**Files:**
- Modify: `app/templates/base.html`
- Modify: `app/templates/admin/layout.html`
- Modify: `app/static/css/main.css`
- Create: `tests/test_frontend_polish.py`

- [ ] **Step 1: 写失败测试**

在 `tests/test_frontend_polish.py` 新增：

```python
def login_admin(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["username"] = "admin"
        session["display_name"] = "管理员"
        session["role"] = "super_admin"


def test_public_pages_load_bootstrap_icons(client, monkeypatch):
    monkeypatch.setattr("app.public.routes.get_settings", lambda: {"site_title": "简历系统"})
    monkeypatch.setattr("app.public.routes.load_public_resumes", lambda keyword="": [])

    response = client.get("/")

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "bootstrap-icons" in html


def test_admin_pages_load_bootstrap_icons(client, monkeypatch):
    login_admin(client)
    monkeypatch.setattr("app.admin.routes.query_one", lambda sql, params=None: {"total": 0})
    monkeypatch.setattr("app.admin.routes.query_all", lambda sql, params=None: [])

    response = client.get("/admin")

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "bootstrap-icons" in html


def test_main_css_contains_blue_theme_tokens():
    css = open("app/static/css/main.css", encoding="utf-8").read()

    assert "--brand: #2563eb" in css
    assert "--ink: #152238" in css
    assert "--soft: #f6f8fb" in css
    assert "--line: #dce3ed" in css
```

- [ ] **Step 2: 运行测试确认失败**

Run:

```powershell
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_frontend_polish.py -v
```

Expected: FAIL，原因是当前模板没有 Bootstrap Icons CDN，CSS 变量仍是旧的墨绿色系。

- [ ] **Step 3: 实现全局图标和设计变量**

在 `app/templates/base.html` 的 Bootstrap CSS 之后加入：

```html
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">
```

在 `app/templates/admin/layout.html` 的 Bootstrap CSS 之后加入同一行。

在 `app/static/css/main.css` 顶部替换 `:root` 为：

```css
:root {
  --brand: #2563eb;
  --brand-strong: #1d4ed8;
  --brand-soft: #dbeafe;
  --ink: #152238;
  --muted: #64748b;
  --line: #dce3ed;
  --paper: #ffffff;
  --soft: #f6f8fb;
  --surface: #f8fafc;
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
  --sidebar: #152238;
  --sidebar-muted: #94a3b8;
}
```

继续在同一 CSS 文件中更新 `body`、`a`、`.btn`、`.btn-primary`、`.content-card`、`.site-footer` 等基础样式，保持圆角 8px 左右，按钮主色改为 `--brand`，阴影改为轻量蓝灰阴影。

- [ ] **Step 4: 运行测试确认通过**

Run:

```powershell
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_frontend_polish.py -v
```

Expected: PASS。

- [ ] **Step 5: 提交**

```bash
git add app/templates/base.html app/templates/admin/layout.html app/static/css/main.css tests/test_frontend_polish.py
git commit -m "style: 增加全站蓝色视觉基础"
```

## Task 2: 公开首页美化

**Files:**
- Modify: `app/templates/public/index.html`
- Modify: `app/static/css/main.css`
- Test: `tests/test_frontend_polish.py`

- [ ] **Step 1: 写失败测试**

在 `tests/test_frontend_polish.py` 新增：

```python
def test_public_homepage_uses_polished_landing_components(client, monkeypatch):
    monkeypatch.setattr("app.public.routes.get_settings", lambda: {"site_title": "简历系统"})
    monkeypatch.setattr(
        "app.public.routes.load_public_resumes",
        lambda keyword="": [
            {
                "username": "demo",
                "display_name": "演示用户",
                "name": "张三",
                "title": "Python 工程师",
                "city": "杭州",
                "summary": "关注 Flask 和 MySQL 项目。",
                "avatar_path": "",
            }
        ],
    )

    response = client.get("/")

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "public-hero" in html
    assert "search-panel" in html
    assert "resume-card" in html
    assert "bi-search" in html
    assert "bi-person-badge" in html
```

- [ ] **Step 2: 运行测试确认失败**

Run:

```powershell
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_frontend_polish.py::test_public_homepage_uses_polished_landing_components -v
```

Expected: FAIL，原因是公开首页还没有这些美化类名和图标。

- [ ] **Step 3: 改造公开首页模板**

在 `app/templates/public/index.html` 中：

- 导航栏改为 `navbar public-navbar navbar-expand-lg sticky-top`
- Hero 区改为 `section class="hero-section public-hero"`
- 搜索表单卡片改为 `content-card search-panel`
- 搜索按钮加入 `<i class="bi bi-search"></i>`
- 公开简历卡片 article 改为 `content-card resume-card h-100`
- 城市前加入 `<i class="bi bi-geo-alt"></i>`
- 查看按钮加入 `<i class="bi bi-person-badge"></i>`

核心结构示例：

```html
<section class="hero-section public-hero">
  <div class="container">
    <div class="row align-items-center g-4">
      <div class="col-lg-7">
        <p class="eyebrow mb-2">Resume Platform</p>
        <h1 class="display-5 fw-bold mb-3">{{ settings.site_title|default('多用户在线简历管理系统') }}</h1>
        <p class="lead hero-summary mb-0">维护简历内容，生成公开展示页面，让作品和经历更清楚地呈现。</p>
      </div>
      <div class="col-lg-5">
        <form class="content-card search-panel" method="get" action="{{ url_for('public.index') }}">
          ...
        </form>
      </div>
    </div>
  </div>
</section>
```

- [ ] **Step 4: 补充首页 CSS**

在 `app/static/css/main.css` 中添加：

```css
.public-navbar {
  backdrop-filter: blur(16px);
  background: rgba(255, 255, 255, 0.92) !important;
}

.eyebrow {
  color: var(--brand);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0;
  text-transform: uppercase;
}

.public-hero {
  background: linear-gradient(180deg, #f6f8fb 0%, #ffffff 100%);
}

.search-panel {
  border-color: rgba(37, 99, 235, 0.18);
}

.resume-card {
  display: flex;
  flex-direction: column;
}

.resume-card .btn {
  margin-top: auto;
  width: fit-content;
}
```

- [ ] **Step 5: 运行测试确认通过**

Run:

```powershell
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_frontend_polish.py -v
```

Expected: PASS。

- [ ] **Step 6: 提交**

```bash
git add app/templates/public/index.html app/static/css/main.css tests/test_frontend_polish.py
git commit -m "style: 美化公开简历首页"
```

## Task 3: 个人公开简历页美化

**Files:**
- Modify: `app/templates/public/resume.html`
- Modify: `app/static/css/main.css`
- Test: `tests/test_frontend_polish.py`

- [ ] **Step 1: 写失败测试**

在 `tests/test_frontend_polish.py` 新增：

```python
def test_public_resume_uses_polished_resume_components(client, monkeypatch):
    monkeypatch.setattr(
        "app.public.routes.load_user_resume_data",
        lambda username: {
            "owner": {"id": 2, "username": "demo", "display_name": "演示用户"},
            "profile": {
                "name": "张三",
                "title": "Python 工程师",
                "city": "杭州",
                "email": "demo@example.com",
                "phone": "13800138000",
                "wechat": "demo",
                "github_url": "",
                "website_url": "",
                "avatar_path": "",
                "resume_file_path": "",
                "summary": "热爱后端开发。",
                "job_status": "正在寻找机会",
            },
            "skills_by_category": {"后端": [{"name": "Flask", "proficiency": 90}]},
            "experiences": [],
            "projects": [],
            "education": [],
            "certificates": [],
            "settings": {"site_title": "简历系统", "messages_enabled": "1"},
        },
    )

    response = client.get("/u/demo")

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "resume-hero" in html
    assert "contact-panel" in html
    assert "resume-section" in html
    assert "bi-envelope" in html
    assert "bi-chat-dots" in html
```

- [ ] **Step 2: 运行测试确认失败**

Run:

```powershell
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_frontend_polish.py::test_public_resume_uses_polished_resume_components -v
```

Expected: FAIL，原因是个人简历页还没有新类名和图标。

- [ ] **Step 3: 改造个人简历模板**

在 `app/templates/public/resume.html` 中：

- Hero 区改为 `hero-section resume-hero`
- 右侧信息卡改为 `profile-panel contact-panel`
- 各主要 section 增加 `resume-section`
- 邮件按钮加入 `<i class="bi bi-envelope"></i>`
- 下载按钮加入 `<i class="bi bi-download"></i>`
- 留言按钮加入 `<i class="bi bi-chat-dots"></i>`
- 联系信息 dt 前加入合适图标，例如 `bi-geo-alt`、`bi-phone`、`bi-wechat`、`bi-github`

- [ ] **Step 4: 补充简历页 CSS**

在 `app/static/css/main.css` 中添加：

```css
.resume-hero {
  padding-top: 76px;
}

.contact-panel {
  border-top: 4px solid var(--brand);
}

.profile-meta i {
  color: var(--brand);
  margin-right: 6px;
}

.resume-section .section-title {
  color: var(--ink);
}

.timeline-dot {
  background: var(--brand);
  border-color: var(--brand-soft);
}
```

- [ ] **Step 5: 运行测试确认通过**

Run:

```powershell
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_frontend_polish.py -v
```

Expected: PASS。

- [ ] **Step 6: 提交**

```bash
git add app/templates/public/resume.html app/static/css/main.css tests/test_frontend_polish.py
git commit -m "style: 美化个人公开简历页"
```

## Task 4: 后台整体布局和菜单美化

**Files:**
- Modify: `app/templates/admin/layout.html`
- Modify: `app/static/css/main.css`
- Test: `tests/test_frontend_polish.py`

- [ ] **Step 1: 写失败测试**

在 `tests/test_frontend_polish.py` 新增：

```python
def test_admin_layout_uses_product_backend_shell(client, monkeypatch):
    login_admin(client)
    monkeypatch.setattr("app.admin.routes.query_one", lambda sql, params=None: {"total": 0})
    monkeypatch.setattr("app.admin.routes.query_all", lambda sql, params=None: [])

    response = client.get("/admin")

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "admin-shell" in html
    assert "admin-sidebar" in html
    assert "admin-topbar" in html
    assert "bi-speedometer2" in html
    assert "bi-people" in html
    assert "bi-file-earmark-person" in html
    assert "个人信息" not in html
```

- [ ] **Step 2: 运行测试确认失败**

Run:

```powershell
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_frontend_polish.py::test_admin_layout_uses_product_backend_shell -v
```

Expected: FAIL，原因是后台布局还没有产品化 shell 和图标。

- [ ] **Step 3: 改造后台布局模板**

在 `app/templates/admin/layout.html` 中：

- `body` 改为 `class="admin-body"`
- 顶部导航改为 `admin-topbar`
- 外层容器改为 `admin-shell`
- 侧边栏改为 `admin-sidebar`
- 菜单链接改为 `admin-nav-link`
- 超级管理员菜单增加图标：
  - 控制台：`bi-speedometer2`
  - 用户管理：`bi-people`
  - 简历管理：`bi-file-earmark-person`
  - 留言管理：`bi-chat-left-text`
  - 站点设置：`bi-gear`
- 普通用户菜单增加图标：
  - 仪表盘：`bi-grid`
  - 个人信息：`bi-person-vcard`
  - 技能：`bi-lightning-charge`
  - 工作 / 实习经历：`bi-briefcase`
  - 项目经历：`bi-kanban`
  - 教育经历：`bi-mortarboard`
  - 证书：`bi-award`
  - 留言管理：`bi-chat-left-text`

- [ ] **Step 4: 补充后台布局 CSS**

在 `app/static/css/main.css` 中添加：

```css
.admin-body {
  background: var(--soft);
}

.admin-shell {
  min-height: calc(100vh - 57px);
}

.admin-sidebar {
  background: var(--sidebar);
  color: #fff;
}

.admin-nav-link {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--sidebar-muted);
  border: 0;
  border-radius: 8px;
  margin-bottom: 4px;
  background: transparent;
}

.admin-nav-link:hover,
.admin-nav-link:focus {
  color: #fff;
  background: rgba(255, 255, 255, 0.08);
}

.admin-topbar {
  background: #fff;
  border-bottom: 1px solid var(--line);
}

@media (max-width: 991.98px) {
  .admin-sidebar {
    min-height: auto !important;
  }
}
```

- [ ] **Step 5: 运行测试确认通过**

Run:

```powershell
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_frontend_polish.py tests/test_admin_pages.py -v
```

Expected: PASS。

- [ ] **Step 6: 提交**

```bash
git add app/templates/admin/layout.html app/static/css/main.css tests/test_frontend_polish.py
git commit -m "style: 美化后台整体布局和菜单"
```

## Task 5: 后台卡片、表格和表单美化

**Files:**
- Modify: `app/templates/admin/dashboard.html`
- Modify: `app/templates/admin/users.html`
- Modify: `app/templates/admin/resumes.html`
- Modify: `app/templates/admin/messages.html`
- Modify: `app/templates/admin/user_detail.html`
- Modify: `app/templates/admin/resource_list.html`
- Modify: `app/templates/admin/resource_form.html`
- Modify: `app/templates/admin/profile.html`
- Modify: `app/templates/admin/message_detail.html`
- Modify: `app/templates/admin/settings.html`
- Modify: `app/static/css/main.css`
- Test: `tests/test_frontend_polish.py`

- [ ] **Step 1: 写失败测试**

在 `tests/test_frontend_polish.py` 新增：

```python
def test_admin_dashboard_uses_metric_cards(client, monkeypatch):
    login_admin(client)
    monkeypatch.setattr("app.admin.routes.query_one", lambda sql, params=None: {"total": 0})
    monkeypatch.setattr("app.admin.routes.query_all", lambda sql, params=None: [])

    response = client.get("/admin")

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "metric-card" in html
    assert "page-heading" in html
    assert "bi-activity" in html


def test_admin_list_pages_use_polished_tables(client, monkeypatch):
    login_admin(client)
    monkeypatch.setattr("app.admin.routes.query_all", lambda sql, params=None: [])

    response = client.get("/admin/users")

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "filter-toolbar" in html
    assert "table-polished" in html
    assert "status-badge" in html
```

- [ ] **Step 2: 运行测试确认失败**

Run:

```powershell
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_frontend_polish.py::test_admin_dashboard_uses_metric_cards tests/test_frontend_polish.py::test_admin_list_pages_use_polished_tables -v
```

Expected: FAIL，原因是后台页面还没有统一的统计卡、筛选工具栏和表格类名。

- [ ] **Step 3: 改造后台页面模板**

按以下规则更新后台模板：

- 页面标题容器统一使用 `page-heading`
- 统计卡统一使用 `content-card metric-card`
- 列表筛选区统一使用 `filter-toolbar`
- 表格统一增加 `table-polished`
- 状态徽章统一增加 `status-badge`
- 表单卡片统一使用 `content-card form-panel`
- 主要按钮加入对应 Bootstrap Icons，例如保存 `bi-check2-circle`、查看 `bi-eye`、删除 `bi-trash`

示例：

```html
<div class="page-heading">
  <div>
    <h1 class="h3 mb-1">系统控制台</h1>
    <div class="text-secondary">查看全站运行状态，处理用户、公开简历和留言事务。</div>
  </div>
</div>
```

- [ ] **Step 4: 补充后台组件 CSS**

在 `app/static/css/main.css` 中添加：

```css
.page-heading {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.metric-card {
  min-height: 118px;
}

.metric-card i {
  color: var(--brand);
  font-size: 1.35rem;
}

.filter-toolbar {
  padding: 16px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--paper);
}

.table-polished thead th {
  color: var(--muted);
  font-size: 0.82rem;
  font-weight: 700;
  background: var(--surface);
}

.status-badge {
  border-radius: 999px;
  font-weight: 600;
}

.form-panel .form-label {
  color: var(--ink);
  font-weight: 600;
}
```

- [ ] **Step 5: 运行测试确认通过**

Run:

```powershell
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_frontend_polish.py tests/test_admin_pages.py -v
```

Expected: PASS。

- [ ] **Step 6: 提交**

```bash
git add app/templates/admin app/static/css/main.css tests/test_frontend_polish.py
git commit -m "style: 统一后台卡片表格和表单样式"
```

## Task 6: 响应式和浏览器视觉验证

**Files:**
- Modify: `app/static/css/main.css`
- Verify: all templates

- [ ] **Step 1: 补充响应式 CSS**

在 `app/static/css/main.css` 中检查并补充：

```css
@media (max-width: 767.98px) {
  .hero-section {
    padding: 48px 0 40px;
  }

  .display-5 {
    font-size: 2rem;
  }

  .content-card,
  .profile-panel,
  .filter-toolbar {
    padding: 18px;
  }

  .table-responsive {
    border-radius: 8px;
  }

  .page-heading .btn,
  .filter-toolbar .btn {
    width: 100%;
  }
}
```

- [ ] **Step 2: 本地完整验证**

Run:

```powershell
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest -v
D:\Github\resume-site\.venv\Scripts\python.exe -m compileall app
git diff --check
```

Expected: 66 个以上测试全部通过，编译通过，`git diff --check` 无输出。

- [ ] **Step 3: 启动本地服务**

Run:

```powershell
$env:FLASK_ENV='testing'
$env:SECRET_KEY='local-visual-check-secret'
D:\Github\resume-site\.venv\Scripts\python.exe -m flask --app run run --host 127.0.0.1 --port 5010
```

Expected: Flask 服务在 `http://127.0.0.1:5010` 启动。

- [ ] **Step 4: Playwright 截图验证**

使用浏览器打开并截图：

- `http://127.0.0.1:5010/`
- `http://127.0.0.1:5010/auth/login`
- 登录超级管理员后访问 `/admin`
- 登录普通用户后访问 `/dashboard`
- 桌面宽度 `1440x900`
- 手机宽度 `390x844`

检查：

- 没有文字重叠。
- 后台侧边栏在手机端不挤压内容。
- 表格小屏幕可以横向滚动。
- 按钮文字不溢出。
- 图标能正常显示。

- [ ] **Step 5: 修复视觉问题并重新验证**

如果截图发现问题，修改 `app/static/css/main.css` 或对应模板，然后重新运行：

```powershell
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_frontend_polish.py tests/test_admin_pages.py -v
D:\Github\resume-site\.venv\Scripts\python.exe -m compileall app
```

Expected: PASS。

- [ ] **Step 6: 提交**

```bash
git add app/static/css/main.css app/templates tests/test_frontend_polish.py
git commit -m "style: 完善全站响应式视觉细节"
```

## Task 7: 部署、线上验证、合并推送

**Files:**
- Verify: all files

- [ ] **Step 1: 本地最终验证**

Run:

```powershell
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest -v
D:\Github\resume-site\.venv\Scripts\python.exe -m compileall app
git diff --check
git status --short --branch
```

Expected: 测试全通过，编译通过，`git diff --check` 无输出，当前分支没有未提交代码。

- [ ] **Step 2: 部署到线上**

打包当前分支并部署到 `/opt/resume-site`，保留线上 `.env`、`.venv`、`app/static/uploads`，然后重启服务：

```bash
systemctl restart resume-site
systemctl restart nginx
systemctl is-active resume-site
systemctl is-active nginx
```

Expected: 两个服务均为 `active`。

- [ ] **Step 3: 服务器验证**

Run:

```bash
cd /opt/resume-site
./.venv/bin/python -m pytest -v
./.venv/bin/python -m compileall app
systemctl is-active resume-site
systemctl is-active nginx
```

Expected: 服务器测试全通过，编译通过，服务 active。

- [ ] **Step 4: HTTPS 页面验证**

验证线上页面：

- `/` 能看到美化后的公开首页。
- `/u/<username>` 能看到美化后的个人简历页。
- `/admin` 能看到深蓝科技蓝超级管理员后台。
- `/dashboard` 能看到普通用户后台菜单和统计卡。
- 超级管理员后台不出现普通用户的“个人信息、技能、证书”等维护菜单。
- 普通用户后台不出现超级管理员“用户管理、简历管理、站点设置”等平台菜单。

- [ ] **Step 5: 合并推送**

如果线上验证通过：

```bash
cd D:\Github\resume-site
git pull --ff-only origin master
git merge --ff-only codex/frontend-polish
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest -v
git push origin master
git worktree remove D:\Github\resume-site\.worktrees\frontend-polish
git branch -d codex/frontend-polish
```

Expected: `master` 推送成功，专用 worktree 清理完成。

## 自查结果

- 设计文档要求的全站美化、深蓝科技蓝、Bootstrap Icons、前台首页、公开简历、普通用户后台、超级管理员后台、响应式和验证流程均有任务覆盖。
- 本计划不新增数据库表，不改变后端业务逻辑，不引入 Vue/React/Angular。
- 每个任务都有失败测试、实现步骤、验证命令和中文提交说明。
- 视觉验收包含本地测试、编译、浏览器截图、服务器测试和 HTTPS 页面检查。
