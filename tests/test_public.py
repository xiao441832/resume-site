def test_homepage_renders_resume_data(client, monkeypatch):
    monkeypatch.setattr(
        "app.public.routes.load_homepage_data",
        lambda: {
            "profile": {"name": "张三", "title": "Python 工程师", "summary": "热爱后端开发"},
            "skills_by_category": {"后端": [{"name": "Flask", "proficiency": 90}]},
            "experiences": [],
            "projects": [{"name": "简历网站", "tech_stack": "Flask, MySQL", "summary": "个人简历管理"}],
            "education": [],
            "certificates": [],
            "settings": {"site_title": "张三的简历", "messages_enabled": "1", "icp_text": ""},
        },
    )

    response = client.get("/")

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert 'rel="icon"' in html
    assert "张三" in html
    assert "Flask" in html
    assert "简历网站" in html


def test_homepage_renders_upload_paths_through_static_url(client, monkeypatch):
    monkeypatch.setattr(
        "app.public.routes.load_homepage_data",
        lambda: {
            "profile": {
                "name": "张三",
                "title": "Python 工程师",
                "summary": "热爱后端开发",
                "avatar_path": "uploads/avatar.png",
                "resume_file_path": "uploads/resume.pdf",
            },
            "skills_by_category": {},
            "experiences": [],
            "projects": [
                {
                    "name": "简历网站",
                    "cover_image_path": "uploads/cover.png",
                    "summary": "个人简历管理",
                }
            ],
            "education": [],
            "certificates": [],
            "settings": {"site_title": "张三的简历", "messages_enabled": "1", "icp_text": ""},
        },
    )

    html = client.get("/").get_data(as_text=True)

    assert 'src="/static/uploads/avatar.png"' in html
    assert 'href="/static/uploads/resume.pdf"' in html
    assert 'src="/static/uploads/cover.png"' in html
    assert 'src="uploads/avatar.png"' not in html
    assert 'href="uploads/resume.pdf"' not in html


def test_homepage_blocks_unsafe_public_link_schemes(client, monkeypatch):
    monkeypatch.setattr(
        "app.public.routes.load_homepage_data",
        lambda: {
            "profile": {
                "name": "张三",
                "title": "Python 工程师",
                "summary": "热爱后端开发",
                "github_url": "javascript:alert(1)",
                "website_url": "https://example.com",
            },
            "skills_by_category": {},
            "experiences": [],
            "projects": [
                {
                    "name": "简历网站",
                    "project_url": "javascript:alert(1)",
                    "source_url": "https://github.com/example/repo",
                }
            ],
            "education": [],
            "certificates": [],
            "settings": {"site_title": "张三的简历", "messages_enabled": "1", "icp_text": ""},
        },
    )

    html = client.get("/").get_data(as_text=True)

    assert "javascript:alert" not in html
    assert 'href="https://example.com"' in html
    assert 'href="https://github.com/example/repo"' in html


def test_message_submission_inserts_message(client, monkeypatch):
    monkeypatch.setattr("app.public.routes.messages_enabled", lambda: True)
    inserted = {}

    def fake_execute(sql, params):
        inserted["params"] = params
        return 1

    monkeypatch.setattr("app.public.routes.execute", fake_execute)

    response = client.post(
        "/messages",
        data={
            "name": "访客",
            "email": "visitor@example.com",
            "phone": "13800138000",
            "content": "你好，我想了解更多。",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert inserted["params"][0] == "访客"
    assert inserted["params"][1] == "visitor@example.com"
