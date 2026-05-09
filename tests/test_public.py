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
    assert "张三" in html
    assert "Flask" in html
    assert "简历网站" in html


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
