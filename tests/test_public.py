def resume_payload():
    return {
        "owner": {
            "id": 3,
            "username": "zhangsan",
            "display_name": "张三",
        },
        "profile": {
            "name": "张三",
            "title": "Python 工程师",
            "summary": "热爱后端开发",
            "avatar_path": "uploads/avatar.png",
            "resume_file_path": "uploads/resume.pdf",
            "github_url": "javascript:alert(1)",
            "website_url": "https://example.com",
            "email": "zhangsan@example.com",
            "phone": "13800138000",
        },
        "skills_by_category": {"后端": [{"name": "Flask", "proficiency": 90}]},
        "experiences": [],
        "projects": [
            {
                "name": "简历网站",
                "cover_image_path": "uploads/cover.png",
                "project_url": "javascript:alert(1)",
                "source_url": "https://github.com/example/repo",
                "tech_stack": "Flask, MySQL",
                "summary": "个人简历管理",
            }
        ],
        "education": [],
        "certificates": [],
        "settings": {"site_title": "多用户简历系统", "messages_enabled": "1", "icp_text": ""},
    }


def test_homepage_renders_public_resume_cards(client, monkeypatch):
    monkeypatch.setattr(
        "app.public.routes.load_public_resumes",
        lambda keyword="": [
            {
                "username": "zhangsan",
                "display_name": "张三",
                "name": "张三",
                "title": "Python 工程师",
                "city": "杭州",
                "summary": "热爱后端开发",
            }
        ],
    )
    monkeypatch.setattr(
        "app.public.routes.get_settings",
        lambda: {"site_title": "多用户简历系统", "seo_description": "", "icp_text": ""},
    )

    response = client.get("/")

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert 'rel="icon"' in html
    assert "多用户简历系统" in html
    assert "张三" in html
    assert "Python 工程师" in html
    assert 'href="/u/zhangsan"' in html


def test_user_resume_page_renders_scoped_resume_data(client, monkeypatch):
    monkeypatch.setattr(
        "app.public.routes.load_user_resume_data",
        lambda username: resume_payload(),
    )

    response = client.get("/u/zhangsan")

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "张三" in html
    assert "Flask" in html
    assert "简历网站" in html
    assert 'src="/static/uploads/avatar.png"' in html
    assert 'href="/static/uploads/resume.pdf"' in html
    assert 'src="/static/uploads/cover.png"' in html
    assert "javascript:alert" not in html
    assert 'href="https://example.com"' in html
    assert 'href="https://github.com/example/repo"' in html


def test_user_resume_page_returns_404_for_hidden_resume(client, monkeypatch):
    monkeypatch.setattr("app.public.routes.load_user_resume_data", lambda username: None)

    response = client.get("/u/hidden")

    assert response.status_code == 404


def test_message_submission_inserts_target_user_message(client, monkeypatch):
    monkeypatch.setattr("app.public.routes.messages_enabled", lambda: True)
    monkeypatch.setattr(
        "app.public.routes.find_public_user",
        lambda username: {"id": 3, "username": username},
    )
    inserted = {}

    def fake_execute(sql, params):
        inserted["sql"] = sql
        inserted["params"] = params
        return 1

    monkeypatch.setattr("app.public.routes.execute", fake_execute)

    response = client.post(
        "/u/zhangsan/messages",
        data={
            "name": "访客",
            "email": "visitor@example.com",
            "phone": "13800138000",
            "content": "你好，我想了解更多。",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/u/zhangsan#contact")
    assert "target_user_id" in inserted["sql"]
    assert inserted["params"][0] == 3
    assert inserted["params"][1] == "访客"
    assert inserted["params"][2] == "visitor@example.com"


def test_legacy_message_get_redirects_to_homepage(client):
    response = client.get("/messages", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/#public-resumes")


def test_csrf_error_redirects_to_contact_form(app):
    app.config["WTF_CSRF_ENABLED"] = True
    client = app.test_client()

    response = client.post(
        "/u/zhangsan/messages",
        data={
            "name": "访客",
            "email": "visitor@example.com",
            "phone": "13800138000",
            "content": "你好，我想了解更多。",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/#public-resumes")
