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
