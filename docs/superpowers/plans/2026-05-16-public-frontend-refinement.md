# 前台页面二次精修 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将公开首页和个人公开简历详情页进一步优化为蓝白简洁、现代 SaaS 风格，减少空旷感并提升毕业设计展示完成度。

**Architecture:** 本次只改前台 Jinja2 模板、公共 CSS 和结构测试，不修改数据库字段和后端业务逻辑。首页保留原有搜索参数和简历跳转逻辑，详情页保留原有联系方式变量、留言表单字段、CSRF 和提交地址。

**Tech Stack:** Flask、Jinja2、HTML5、CSS3、Bootstrap 5、Bootstrap Icons、pytest、Playwright 浏览器验证。

---

## 文件结构

- 修改 `app/templates/public/index.html`：统一前台导航，增强首页 Banner、搜索卡片、平台特性、公开简历卡片和空状态。
- 修改 `app/templates/public/resume.html`：统一详情页导航，增强首屏布局、右侧 sticky 信息卡、内容模块、空状态和联系我区域。
- 修改 `app/static/css/main.css`：新增前台二次精修样式，复用现有蓝白变量，补充卡片高度、行数省略、hover、sticky、响应式规则。
- 修改 `tests/test_frontend_polish.py`：增加首页和详情页结构断言，保证关键 class、图标、空状态和原有 Jinja2 变量入口不被破坏。

## Task 1: 首页 Banner、导航和公开简历卡片精修

**Files:**
- Modify: `tests/test_frontend_polish.py`
- Modify: `app/templates/public/index.html`
- Modify: `app/static/css/main.css`

- [ ] **Step 1: 写首页结构失败测试**

在 `tests/test_frontend_polish.py` 中更新 `test_public_homepage_uses_polished_landing_components`，并新增首页空状态测试：

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
                "summary": "关注 Flask 和 MySQL 项目，能够独立完成简历系统开发和部署。",
                "avatar_path": "",
            }
        ],
    )

    response = client.get("/")

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "public-navbar" in html
    assert "public-nav-link" in html
    assert "public-hero" in html
    assert "hero-feature-list" in html
    assert "hero-feature" in html
    assert "search-panel" in html
    assert "resume-grid" in html
    assert "resume-card" in html
    assert "resume-card-summary" in html
    assert "resume-card-action" in html
    assert "resume-avatar" in html
    assert "bi-search" in html
    assert "bi-people" in html
    assert "bi-shield-check" in html
    assert 'href="/u/demo"' in html


def test_public_homepage_uses_polished_empty_state(client, monkeypatch):
    monkeypatch.setattr("app.public.routes.get_settings", lambda: {"site_title": "简历系统"})
    monkeypatch.setattr("app.public.routes.load_public_resumes", lambda keyword="": [])

    response = client.get("/")

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "empty-state" in html
    assert "暂无公开简历" in html
    assert "用户公开发布后将在这里展示" in html
```

- [ ] **Step 2: 运行首页测试确认失败**

Run:

```powershell
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_frontend_polish.py::test_public_homepage_uses_polished_landing_components tests/test_frontend_polish.py::test_public_homepage_uses_polished_empty_state -v
```

Expected: FAIL，原因是首页还没有 `hero-feature-list`、`resume-card-summary`、`resume-card-action`、`empty-state` 等二次精修结构。

- [ ] **Step 3: 改造首页模板**

在 `app/templates/public/index.html` 中保留原有 `method="get"`、`action="{{ url_for('public.index') }}"`、`name="q"` 和 `href="{{ url_for('public.user_resume', username=resume.username) }}"`。

首页导航使用以下结构：

```html
<nav class="navbar public-navbar navbar-expand-lg sticky-top">
  <div class="container">
    <a class="navbar-brand fw-semibold" href="{{ url_for('public.index') }}">{{ settings.site_title|default('多用户简历系统') }}</a>
    <div class="d-flex align-items-center gap-2 ms-auto public-nav-actions">
      <a class="public-nav-link active" href="{{ url_for('public.index') }}#public-resumes">公开简历</a>
      <a class="btn btn-outline-primary btn-sm" href="{{ url_for('auth.login') }}">登录</a>
      <a class="btn btn-primary btn-sm" href="{{ url_for('auth.register') }}">注册</a>
    </div>
  </div>
</nav>
```

Banner 左侧增加平台特性：

```html
<div class="hero-feature-list">
  <div class="hero-feature"><i class="bi bi-people"></i><span>多用户</span></div>
  <div class="hero-feature"><i class="bi bi-window-check"></i><span>公开展示</span></div>
  <div class="hero-feature"><i class="bi bi-shield-check"></i><span>安全可靠</span></div>
</div>
```

搜索卡片保留原有表单逻辑，并增加更清晰的标题和说明：

```html
<form class="content-card search-panel" method="get" action="{{ url_for('public.index') }}">
  <div class="mb-3">
    <label class="form-label mb-1" for="q">搜索公开简历</label>
    <div class="text-muted small">按姓名、岗位、城市或简介快速查找。</div>
  </div>
  <div class="input-group search-control">
    <input id="q" class="form-control" type="search" name="q" value="{{ keyword }}" placeholder="姓名、岗位、城市或简介">
    <button class="btn btn-primary" type="submit"><i class="bi bi-search"></i> 搜索</button>
  </div>
</form>
```

公开简历列表使用 `resume-grid` 和统一卡片结构：

```html
<div class="row g-4 resume-grid">
  {% for resume in resumes %}
    <div class="col-12 col-md-6 col-xl-4">
      <article class="content-card resume-card h-100">
        <div class="resume-card-header">
          {% set avatar_url = static_upload_url(resume.avatar_path) %}
          {% if avatar_url %}
            <img class="resume-avatar" src="{{ avatar_url }}" alt="{{ resume.name or resume.display_name }}">
          {% else %}
            <div class="resume-avatar resume-avatar-placeholder">{{ (resume.name or resume.display_name)|first }}</div>
          {% endif %}
          <div class="min-w-0">
            <h3 class="h5 mb-1 text-truncate">{{ resume.name or resume.display_name }}</h3>
            <p class="text-muted mb-0 text-truncate">{{ resume.title }}</p>
          </div>
        </div>
        {% if resume.city %}
          <p class="text-muted small mb-2"><i class="bi bi-geo-alt"></i> {{ resume.city }}</p>
        {% endif %}
        {% if resume.summary %}
          <p class="resume-card-summary">{{ resume.summary }}</p>
        {% else %}
          <p class="resume-card-summary text-muted">该用户暂未填写个人简介。</p>
        {% endif %}
        <a class="btn btn-outline-primary btn-sm resume-card-action" href="{{ url_for('public.user_resume', username=resume.username) }}"><i class="bi bi-person-badge"></i> 查看简历</a>
      </article>
    </div>
  {% else %}
    <div class="col-12">
      <div class="content-card empty-state">
        <i class="bi bi-folder2-open"></i>
        <h3 class="h5 mb-2">暂无公开简历</h3>
        <p class="mb-0 text-muted">用户公开发布后将在这里展示。</p>
      </div>
    </div>
  {% endfor %}
</div>
```

- [ ] **Step 4: 补充首页 CSS**

在 `app/static/css/main.css` 中补充以下样式，放在现有公开页面样式附近：

```css
:root {
  --shadow-sm: 0 8px 22px rgba(21, 34, 56, 0.06);
  --shadow-md: 0 16px 36px rgba(21, 34, 56, 0.09);
  --radius: 10px;
}

.public-navbar {
  min-height: 64px;
  border-bottom: 1px solid rgba(220, 227, 237, 0.75);
}

.public-nav-actions {
  flex-wrap: wrap;
  justify-content: flex-end;
}

.public-nav-link {
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  padding: 4px 10px;
  border-radius: 8px;
  color: var(--muted);
  font-size: 0.95rem;
  font-weight: 600;
  text-decoration: none;
}

.public-nav-link:hover,
.public-nav-link:focus,
.public-nav-link.active {
  color: var(--brand);
  background: var(--brand-soft);
  text-decoration: none;
}

.public-hero {
  border-bottom: 1px solid rgba(220, 227, 237, 0.65);
  background:
    radial-gradient(circle at 12% 18%, rgba(37, 99, 235, 0.1), transparent 28%),
    linear-gradient(180deg, #eff6ff 0%, #ffffff 100%);
}

.hero-feature-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 24px;
}

.hero-feature {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border: 1px solid rgba(37, 99, 235, 0.14);
  border-radius: 999px;
  color: var(--ink);
  background: rgba(255, 255, 255, 0.76);
  box-shadow: var(--shadow-sm);
  font-weight: 600;
}

.hero-feature i {
  color: var(--brand);
}

.search-panel {
  border-radius: var(--radius);
  box-shadow: var(--shadow-md);
}

.resume-card {
  min-height: 320px;
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}

.resume-card:hover {
  transform: translateY(-4px);
  border-color: rgba(37, 99, 235, 0.22);
  box-shadow: var(--shadow-md);
}

.resume-card-header {
  display: grid;
  grid-template-columns: 76px minmax(0, 1fr);
  gap: 14px;
  align-items: center;
  margin-bottom: 18px;
}

.resume-avatar {
  width: 76px;
  height: 76px;
  border-radius: 12px;
  object-fit: cover;
  background: var(--soft);
}

.resume-avatar-placeholder {
  display: grid;
  place-items: center;
  color: #fff;
  background: linear-gradient(135deg, var(--brand), var(--brand-strong));
  font-size: 2rem;
  font-weight: 700;
}

.resume-card-summary {
  display: -webkit-box;
  min-height: 6rem;
  margin-bottom: 18px;
  overflow: hidden;
  color: var(--ink);
  line-height: 1.5;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 4;
}

.resume-card-action {
  align-self: flex-start;
}

.empty-state {
  display: grid;
  place-items: center;
  min-height: 180px;
  text-align: center;
}

.empty-state i {
  margin-bottom: 12px;
  color: var(--brand);
  font-size: 2rem;
}

.min-w-0 {
  min-width: 0;
}
```

- [ ] **Step 5: 运行首页测试确认通过**

Run:

```powershell
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_frontend_polish.py tests/test_public.py -v
```

Expected: PASS。

- [ ] **Step 6: 提交首页精修**

```bash
git add app/templates/public/index.html app/static/css/main.css tests/test_frontend_polish.py
git commit -m "style: 精修前台首页展示效果"
```

## Task 2: 个人公开简历详情页精修

**Files:**
- Modify: `tests/test_frontend_polish.py`
- Modify: `app/templates/public/resume.html`
- Modify: `app/static/css/main.css`

- [ ] **Step 1: 写详情页结构失败测试**

在 `tests/test_frontend_polish.py` 中更新 `test_public_resume_uses_polished_resume_components`，并新增空模块结构测试：

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
                "github_url": "https://github.com/demo",
                "website_url": "https://example.com",
                "avatar_path": "",
                "resume_file_path": "",
                "summary": "热爱后端开发，关注 Flask 和 MySQL。",
                "job_status": "正在寻找机会",
            },
            "skills_by_category": {"后端": [{"name": "Flask", "proficiency": 90}]},
            "experiences": [{"company": "演示公司", "position": "后端实习生", "location": "杭州", "description": "参与后台开发。"}],
            "projects": [{"name": "简历系统", "role": "开发", "tech_stack": "Flask", "project_url": "", "source_url": "", "cover_image_path": "", "summary": "多用户简历展示。"}],
            "education": [{"school": "演示大学", "major": "软件工程", "degree": "本科", "description": "学习 Web 开发。"}],
            "certificates": [{"name": "Web 开发证书", "issuer": "演示机构", "issue_date": "2026-05-16", "description": "项目实践。"}],
            "settings": {"site_title": "简历系统", "messages_enabled": "1"},
        },
    )

    response = client.get("/u/demo")

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "public-navbar" in html
    assert "resume-hero" in html
    assert "resume-hero-layout" in html
    assert "resume-actions" in html
    assert "profile-panel-sticky" in html
    assert "contact-panel" in html
    assert "resume-module" in html
    assert "module-title" in html
    assert "contact-card" in html
    assert "contact-form-card" in html
    assert "bi-envelope" in html
    assert "bi-chat-dots" in html
    assert 'href="mailto:demo@example.com"' in html
    assert 'href="https://github.com/demo"' in html


def test_public_resume_uses_polished_empty_module_states(client, monkeypatch):
    monkeypatch.setattr(
        "app.public.routes.load_user_resume_data",
        lambda username: {
            "owner": {"id": 2, "username": "demo", "display_name": "演示用户"},
            "profile": {
                "name": "张三",
                "title": "Python 工程师",
                "city": "",
                "email": "",
                "phone": "",
                "wechat": "",
                "github_url": "",
                "website_url": "",
                "avatar_path": "",
                "resume_file_path": "",
                "summary": "",
                "job_status": "",
            },
            "skills_by_category": {},
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
    assert html.count("module-empty-state") >= 5
    assert "该模块暂未填写，完善后将在此展示。" in html
```

- [ ] **Step 2: 运行详情页测试确认失败**

Run:

```powershell
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_frontend_polish.py::test_public_resume_uses_polished_resume_components tests/test_frontend_polish.py::test_public_resume_uses_polished_empty_module_states -v
```

Expected: FAIL，原因是详情页还没有 `resume-hero-layout`、`profile-panel-sticky`、`contact-card`、`module-empty-state` 等二次精修结构。

- [ ] **Step 3: 改造详情页导航和首屏**

在 `app/templates/public/resume.html` 中把导航改为与首页一致的公开导航，保留原有页面锚点：

```html
<nav class="navbar public-navbar navbar-expand-lg sticky-top">
  <div class="container">
    <a class="navbar-brand fw-semibold" href="{{ url_for('public.index') }}">{{ settings.site_title|default('多用户简历系统') }}</a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#mainNav" aria-controls="mainNav" aria-expanded="false" aria-label="切换导航">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="mainNav">
      <ul class="navbar-nav ms-auto align-items-lg-center gap-lg-1">
        <li class="nav-item"><a class="public-nav-link" href="{{ url_for('public.index') }}">首页</a></li>
        <li class="nav-item"><a class="public-nav-link" href="{{ url_for('public.index') }}#public-resumes">公开简历</a></li>
        <li class="nav-item"><a class="public-nav-link" href="#skills">技能</a></li>
        <li class="nav-item"><a class="public-nav-link" href="#projects">项目</a></li>
        <li class="nav-item"><a class="public-nav-link" href="#contact">联系</a></li>
        <li class="nav-item"><a class="btn btn-outline-primary btn-sm ms-lg-2" href="{{ url_for('auth.login') }}">登录</a></li>
        <li class="nav-item"><a class="btn btn-primary btn-sm" href="{{ url_for('auth.register') }}">注册</a></li>
      </ul>
    </div>
  </div>
</nav>
```

首屏行增加 `resume-hero-layout` 和 `resume-actions`：

```html
<div class="row align-items-start g-4 resume-hero-layout">
  <div class="col-lg-8">
    <p class="eyebrow mb-2">{{ profile.job_status|default('开放机会') }}</p>
    <h1 class="display-5 fw-bold mb-3">{{ profile.name|default(owner.display_name) }}</h1>
    <p class="lead mb-3">{{ profile.title|default('') }}</p>
    {% if profile.summary %}
      <p class="hero-summary">{{ profile.summary }}</p>
    {% else %}
      <p class="hero-summary text-muted">该用户暂未填写个人简介，完善后将在这里展示。</p>
    {% endif %}
    <div class="d-flex flex-wrap gap-2 mt-4 resume-actions">
      <a class="btn btn-outline-secondary" href="{{ url_for('public.index') }}"><i class="bi bi-house"></i> 返回首页</a>
      {% if profile.email %}<a class="btn btn-primary" href="mailto:{{ profile.email }}"><i class="bi bi-envelope"></i> 发送邮件</a>{% endif %}
      {% set resume_url = static_upload_url(profile.resume_file_path) %}
      {% if resume_url %}<a class="btn btn-outline-secondary" href="{{ resume_url }}"><i class="bi bi-download"></i> 下载简历</a>{% endif %}
      <a class="btn btn-outline-secondary" href="#contact"><i class="bi bi-chat-dots"></i> 留言</a>
    </div>
  </div>
  <div class="col-lg-4">
    <div class="profile-panel contact-panel profile-panel-sticky">
      {% set avatar_url = static_upload_url(profile.avatar_path) %}
      {% if avatar_url %}
        <img class="profile-avatar" src="{{ avatar_url }}" alt="{{ profile.name }}">
      {% else %}
        <div class="profile-avatar profile-avatar-placeholder">{{ profile.name|default(owner.display_name)|first }}</div>
      {% endif %}
      <dl class="profile-meta mb-0">
        {% if profile.city %}<div><dt><i class="bi bi-geo-alt"></i>城市</dt><dd>{{ profile.city }}</dd></div>{% endif %}
        {% if profile.email %}<div><dt><i class="bi bi-envelope"></i>邮箱</dt><dd><a href="mailto:{{ profile.email }}">{{ profile.email }}</a></dd></div>{% endif %}
        {% if profile.phone %}<div><dt><i class="bi bi-phone"></i>电话</dt><dd>{{ profile.phone }}</dd></div>{% endif %}
        {% if profile.wechat %}<div><dt><i class="bi bi-wechat"></i>微信</dt><dd>{{ profile.wechat }}</dd></div>{% endif %}
        {% set github_url = safe_public_url(profile.github_url) %}
        {% if github_url %}<div><dt><i class="bi bi-github"></i>GitHub</dt><dd><a href="{{ github_url }}">{{ github_url }}</a></dd></div>{% endif %}
        {% set website_url = safe_public_url(profile.website_url) %}
        {% if website_url %}<div><dt><i class="bi bi-link-45deg"></i>网站</dt><dd><a href="{{ website_url }}">{{ website_url }}</a></dd></div>{% endif %}
      </dl>
    </div>
  </div>
</div>
```

- [ ] **Step 4: 改造联系方式卡片**

在右侧信息卡中保留 `static_upload_url`、`safe_public_url` 和原有变量，整理为统一列表：

```html
<dl class="profile-meta mb-0">
  {% if profile.city %}<div><dt><i class="bi bi-geo-alt"></i>城市</dt><dd>{{ profile.city }}</dd></div>{% endif %}
  {% if profile.email %}<div><dt><i class="bi bi-envelope"></i>邮箱</dt><dd><a href="mailto:{{ profile.email }}">{{ profile.email }}</a></dd></div>{% endif %}
  {% if profile.phone %}<div><dt><i class="bi bi-phone"></i>电话</dt><dd>{{ profile.phone }}</dd></div>{% endif %}
  {% if profile.wechat %}<div><dt><i class="bi bi-wechat"></i>微信</dt><dd>{{ profile.wechat }}</dd></div>{% endif %}
  {% set github_url = safe_public_url(profile.github_url) %}
  {% if github_url %}<div><dt><i class="bi bi-github"></i>GitHub</dt><dd><a href="{{ github_url }}">{{ github_url }}</a></dd></div>{% endif %}
  {% set website_url = safe_public_url(profile.website_url) %}
  {% if website_url %}<div><dt><i class="bi bi-link-45deg"></i>网站</dt><dd><a href="{{ website_url }}">{{ website_url }}</a></dd></div>{% endif %}
</dl>
```

- [ ] **Step 5: 改造详情页内容模块和空状态**

每个模块使用 `resume-module`、`module-title` 和 `module-empty-state`。以专业技能为例：

```html
<section id="skills" class="section-block resume-section">
  <div class="container">
    <div class="module-heading">
      <h2 class="section-title module-title"><i class="bi bi-lightning-charge"></i> 专业技能</h2>
    </div>
    <div class="row g-4">
      {% for category, skills in skills_by_category.items() %}
        <div class="col-lg-6">
          <div class="content-card resume-module h-100">
            <h3 class="h5 mb-3">{{ category }}</h3>
            {% for skill in skills %}
              <div class="skill-row">
                <div class="d-flex justify-content-between gap-3">
                  <span class="fw-medium">{{ skill.name }}</span>
                  <span class="text-muted">{{ skill.proficiency }}%</span>
                </div>
                <div class="progress" role="progressbar" aria-label="{{ skill.name }}" aria-valuenow="{{ skill.proficiency }}" aria-valuemin="0" aria-valuemax="100">
                  <div class="progress-bar" style="width: {{ skill.proficiency }}%;"></div>
                </div>
              </div>
            {% endfor %}
          </div>
        </div>
      {% else %}
        <div class="col-12">
          <div class="content-card module-empty-state">该模块暂未填写，完善后将在此展示。</div>
        </div>
      {% endfor %}
    </div>
  </div>
</section>
```

工作经历、项目作品、教育背景、证书荣誉都采用同一句空状态文案：

```html
<div class="content-card module-empty-state">该模块暂未填写，完善后将在此展示。</div>
```

- [ ] **Step 6: 改造联系我区域**

将联系我区域改为左右两个白色卡片。保留表单 `method`、`action`、`form.hidden_tag()` 和所有 WTForms 字段：

```html
<section id="contact" class="section-block resume-section">
  <div class="container">
    <div class="module-heading">
      <h2 class="section-title module-title"><i class="bi bi-chat-dots"></i> 联系我</h2>
    </div>
    <div class="content-card contact-card">
      <div class="row g-4 align-items-start">
        <div class="col-lg-5">
          <p class="text-muted">欢迎通过邮件、电话或留言沟通合作机会。</p>
          <div class="contact-list">
            {% if profile.email %}<div><span>邮箱</span><a href="mailto:{{ profile.email }}">{{ profile.email }}</a></div>{% endif %}
            {% if profile.phone %}<div><span>电话</span><strong>{{ profile.phone }}</strong></div>{% endif %}
          </div>
        </div>
        <div class="col-lg-7">
          {% if settings.messages_enabled|default('1') == '1' %}
            <form class="contact-form-card message-form" method="post" action="{{ url_for('public.submit_message', username=owner.username) }}">
              {{ form.hidden_tag() }}
              <div class="row g-3">
                <div class="col-md-6">
                  {{ form.name.label(class="form-label") }}
                  {{ form.name(class="form-control", autocomplete="name") }}
                </div>
                <div class="col-md-6">
                  {{ form.email.label(class="form-label") }}
                  {{ form.email(class="form-control", autocomplete="email") }}
                </div>
                <div class="col-12">
                  {{ form.phone.label(class="form-label") }}
                  {{ form.phone(class="form-control", autocomplete="tel") }}
                </div>
                <div class="col-12">
                  {{ form.content.label(class="form-label") }}
                  {{ form.content(class="form-control", rows="5") }}
                </div>
              </div>
              <button class="btn btn-primary" type="submit"><i class="bi bi-send"></i> {{ form.submit.label.text }}</button>
            </form>
          {% else %}
            <div class="module-empty-state">留言功能暂未开放。</div>
          {% endif %}
        </div>
      </div>
    </div>
  </div>
</section>
```

表单字段仍按当前模板逐项渲染：

```html
{{ form.name.label(class="form-label") }}
{{ form.name(class="form-control", autocomplete="name") }}
{{ form.email.label(class="form-label") }}
{{ form.email(class="form-control", autocomplete="email") }}
{{ form.phone.label(class="form-label") }}
{{ form.phone(class="form-control", autocomplete="tel") }}
{{ form.content.label(class="form-label") }}
{{ form.content(class="form-control", rows="5") }}
```

- [ ] **Step 7: 补充详情页 CSS**

在 `app/static/css/main.css` 中补充：

```css
.resume-hero-layout {
  position: relative;
}

.resume-actions .btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.profile-panel-sticky {
  position: sticky;
  top: 88px;
}

.profile-panel.contact-panel {
  border-radius: var(--radius);
  box-shadow: var(--shadow-md);
}

.module-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.module-title {
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.module-title i {
  color: var(--brand);
}

.resume-module {
  height: 100%;
}

.module-empty-state {
  display: grid;
  min-height: 120px;
  place-items: center;
  color: var(--muted);
  text-align: center;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
}

.contact-card {
  border-radius: var(--radius);
}

.contact-list {
  display: grid;
  gap: 12px;
}

.contact-list div {
  display: grid;
  grid-template-columns: 64px minmax(0, 1fr);
  gap: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--line);
}

.contact-list span {
  color: var(--muted);
  font-weight: 600;
}

.contact-list a,
.contact-list strong {
  min-width: 0;
  overflow-wrap: anywhere;
}

.contact-form-card {
  padding: 0;
}
```

- [ ] **Step 8: 运行详情页测试确认通过**

Run:

```powershell
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_frontend_polish.py tests/test_public.py -v
```

Expected: PASS。

- [ ] **Step 9: 提交详情页精修**

```bash
git add app/templates/public/resume.html app/static/css/main.css tests/test_frontend_polish.py
git commit -m "style: 精修公开简历详情页"
```

## Task 3: 响应式验证、线上部署和合并推送

**Files:**
- Modify: `app/static/css/main.css`
- Verify: all files

- [ ] **Step 1: 补充小屏响应式规则**

检查 `app/static/css/main.css` 中已有媒体查询，并补充以下规则：

```css
@media (max-width: 991.98px) {
  .profile-panel-sticky {
    position: static;
  }

  .public-navbar .navbar-nav {
    align-items: stretch !important;
    padding-top: 12px;
  }

  .public-navbar .navbar-nav .btn,
  .public-nav-link {
    justify-content: center;
    width: 100%;
  }
}

@media (max-width: 767.98px) {
  .public-nav-actions {
    width: 100%;
  }

  .search-control {
    display: grid;
    gap: 10px;
  }

  .search-control .form-control,
  .search-control .btn {
    width: 100%;
    border-radius: 8px !important;
  }

  .hero-feature-list {
    display: grid;
    grid-template-columns: 1fr;
  }

  .resume-card {
    min-height: auto;
  }

  .resume-card-header {
    grid-template-columns: 64px minmax(0, 1fr);
  }

  .resume-avatar {
    width: 64px;
    height: 64px;
  }

  .contact-list div,
  .profile-meta div {
    grid-template-columns: 1fr;
    gap: 4px;
  }
}
```

- [ ] **Step 2: 运行完整本地验证**

Run:

```powershell
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest -v
D:\Github\resume-site\.venv\Scripts\python.exe -m compileall app
git diff --check
git status --short --branch
```

Expected: 测试全部通过，编译通过，`git diff --check` 无输出，工作区没有未提交代码。

- [ ] **Step 3: 本地浏览器视觉验证**

启动一个本地 Flask 检查服务，可以使用线上 `.env` 或测试假数据脚本，但不得修改项目代码。浏览器检查：

- `http://127.0.0.1:5010/`
- `http://127.0.0.1:5010/u/demo`
- 桌面宽度 `1440x900`
- 平板宽度 `768x1024`
- 手机宽度 `390x844`

检查项：

- 首页公开简历桌面三列、平板两列、手机一列。
- 详情页桌面左右布局，手机上下排列。
- 搜索框、按钮、头像、卡片不溢出。
- 页面没有整体横向滚动条。
- 控制台没有明显 JavaScript 报错。

- [ ] **Step 4: 修复视觉问题后提交响应式收尾**

如果 Step 3 发现问题，修改 `app/static/css/main.css` 或对应模板，然后运行：

```powershell
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest tests/test_frontend_polish.py tests/test_public.py -v
D:\Github\resume-site\.venv\Scripts\python.exe -m compileall app
git diff --check
```

Expected: PASS。

提交：

```bash
git add app/static/css/main.css app/templates/public tests/test_frontend_polish.py
git commit -m "style: 完善前台响应式细节"
```

如果 Step 3 没有发现需要修改的问题，不创建空提交。

- [ ] **Step 5: 部署到线上**

打包当前分支并部署到 `/opt/resume-site`，保留线上 `.env`、`.venv` 和 `app/static/uploads`：

```powershell
git archive --format=tar -o $env:TEMP\resume-site-public-refinement.tar HEAD
scp -i "C:\Users\xiao\.ssh\id_ed25519" $env:TEMP\resume-site-public-refinement.tar root@120.79.146.35:/tmp/resume-site-public-refinement.tar
ssh -i "C:\Users\xiao\.ssh\id_ed25519" root@120.79.146.35 'set -e; DEPLOY=/opt/resume-site; test -d "$DEPLOY"; test -f "$DEPLOY/.env"; test -d "$DEPLOY/.venv"; mkdir -p "$DEPLOY/app/static/uploads"; tar -xf /tmp/resume-site-public-refinement.tar -C "$DEPLOY"; systemctl restart resume-site; systemctl restart nginx; systemctl is-active resume-site; systemctl is-active nginx'
```

Expected: `resume-site` 和 `nginx` 都输出 `active`。

- [ ] **Step 6: 服务器验证**

Run:

```bash
cd /opt/resume-site
./.venv/bin/python -m pytest -v
./.venv/bin/python -m compileall app
systemctl is-active resume-site
systemctl is-active nginx
```

Expected: 服务器测试全部通过，编译通过，服务均为 `active`。

- [ ] **Step 7: 线上页面验证**

验证线上页面：

- `/` 返回 200，包含 `public-hero`、`hero-feature-list`、`resume-grid`。
- `/auth/login` 返回 200。
- `/u/<public_username>` 返回 200，包含 `resume-hero-layout`、`profile-panel-sticky`、`contact-card`。
- 线上浏览器手机宽度没有整体横向滚动条。

- [ ] **Step 8: 合并并推送**

如果线上验证通过：

```powershell
cd D:\Github\resume-site
git fetch origin master
git merge --ff-only codex/public-frontend-refinement
D:\Github\resume-site\.venv\Scripts\python.exe -m pytest -v
D:\Github\resume-site\.venv\Scripts\python.exe -m compileall app
git diff --check
git push origin master
git worktree remove D:\Github\resume-site\.worktrees\public-frontend-refinement
git branch -d codex/public-frontend-refinement
```

Expected: `master` 推送成功，前台精修分支和 worktree 清理完成。

## 自查结果

- 规格中的首页导航、Banner、搜索卡片、平台特性、公开简历卡片、首页空状态均由 Task 1 覆盖。
- 规格中的详情页导航、首屏布局、右侧信息卡、内容模块、空模块状态和联系我卡片均由 Task 2 覆盖。
- 规格中的电脑、平板、手机响应式、浏览器控制台和线上部署验证均由 Task 3 覆盖。
- 本计划不要求修改 Python 后端代码，不修改数据库字段，不改变搜索、跳转和留言提交业务逻辑。
