def login_admin(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["username"] = "admin"
        session["display_name"] = "管理员"
        session["role"] = "admin"
        session["admin_user_id"] = 1
        session["admin_username"] = "admin"
        session["admin_display_name"] = "管理员"


def login_user(client, user_id=3):
    with client.session_transaction() as session:
        session["user_id"] = user_id
        session["username"] = "student"
        session["display_name"] = "学生用户"
        session["role"] = "user"


def test_resource_list_renders_rows(client, monkeypatch):
    login_user(client, user_id=3)
    captured = {}

    def fake_query_all(sql, params=None):
        captured["sql"] = sql
        captured["params"] = params
        return [
            {
                "id": 1,
                "name": "Flask",
                "category": "后端",
                "proficiency": 90,
                "sort_order": 1,
                "is_active": 1,
            }
        ]

    monkeypatch.setattr(
        "app.admin.routes.query_all",
        fake_query_all,
    )

    response = client.get("/dashboard/skills")

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "技能" in html
    assert "Flask" in html
    assert "新增" in html
    assert 'rel="icon"' in html
    assert "WHERE user_id = %s" in captured["sql"]
    assert captured["params"] == (3,)


def test_profile_post_updates_existing_profile(client, monkeypatch):
    login_user(client, user_id=3)
    monkeypatch.setattr(
        "app.admin.routes.query_one",
        lambda sql, params=None: {
            "id": 1,
            "name": "旧名字",
            "title": "旧职位",
            "is_active": 1,
            "avatar_path": None,
            "resume_file_path": None,
        },
    )
    executed = []
    monkeypatch.setattr(
        "app.admin.routes.execute",
        lambda sql, params=None: executed.append((sql, params)) or 1,
    )

    response = client.post(
        "/dashboard/profile",
        data={
            "name": "张三",
            "title": "Python 工程师",
            "city": "杭州",
            "email": "zhangsan@example.com",
            "phone": "13800138000",
            "wechat": "zhangsan",
            "github_url": "https://github.com/example",
            "website_url": "https://example.com",
            "summary": "热爱后端开发",
            "job_status": "正在寻找后端开发机会",
            "is_active": "y",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "UPDATE profile" in executed[0][0]
    assert "WHERE id = %s AND user_id = %s" in executed[0][0]
    assert executed[0][1][0] == "张三"
    assert executed[0][1][-1] == 3


def test_message_detail_updates_status(client, monkeypatch):
    login_user(client, user_id=3)
    monkeypatch.setattr(
        "app.admin.routes.query_one",
        lambda sql, params=None: {
            "id": 9,
            "name": "访客",
            "email": "visitor@example.com",
            "phone": "",
            "content": "想了解项目。",
            "status": "unread",
            "admin_note": "",
            "ip_address": "127.0.0.1",
            "user_agent": "pytest",
        },
    )
    executed = []
    monkeypatch.setattr(
        "app.admin.routes.execute",
        lambda sql, params=None: executed.append((sql, params)) or 1,
    )

    response = client.post(
        "/dashboard/messages/9",
        data={"status": "handled", "admin_note": "已回复"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "UPDATE messages" in executed[0][0]
    assert "target_user_id = %s" in executed[0][0]
    assert executed[0][1] == ("handled", "已回复", 9, 3)


def test_settings_post_upserts_site_settings(client, monkeypatch):
    login_admin(client)
    monkeypatch.setattr("app.admin.routes.query_all", lambda sql, params=None: [])
    executed = []
    monkeypatch.setattr(
        "app.admin.routes.execute",
        lambda sql, params=None: executed.append((sql, params)) or 1,
    )

    response = client.post(
        "/admin/settings",
        data={
            "site_title": "张三的简历",
            "seo_description": "Python 后端工程师",
            "icp_text": "浙ICP备00000000号",
            "messages_enabled": "y",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    keys = [params[0] for _, params in executed]
    assert keys == ["site_title", "seo_description", "icp_text", "messages_enabled"]
