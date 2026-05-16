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
    assert "search-control" in html
    assert "resume-grid" in html
    assert "resume-card" in html
    assert "resume-card-header" in html
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


def test_admin_pages_load_bootstrap_icons(client, monkeypatch):
    login_admin(client)
    monkeypatch.setattr("app.admin.routes.query_one", lambda sql, params=None: {"total": 0})
    monkeypatch.setattr("app.admin.routes.query_all", lambda sql, params=None: [])

    response = client.get("/admin")

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "bootstrap-icons" in html


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


def test_main_css_contains_blue_theme_tokens():
    css = open("app/static/css/main.css", encoding="utf-8").read()

    assert "--brand: #2563eb" in css
    assert "--ink: #152238" in css
    assert "--soft: #f6f8fb" in css
    assert "--line: #dce3ed" in css
