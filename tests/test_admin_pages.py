def login_admin(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["username"] = "admin"
        session["display_name"] = "管理员"
        session["role"] = "super_admin"
        session["admin_user_id"] = 1
        session["admin_username"] = "admin"
        session["admin_display_name"] = "管理员"


def login_user(client, user_id=3):
    with client.session_transaction() as session:
        session["user_id"] = user_id
        session["username"] = "student"
        session["display_name"] = "学生用户"
        session["role"] = "user"


def test_super_admin_can_view_user_list(client, monkeypatch):
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
                "created_at": "2026-05-12",
                "last_login_at": None,
            }
        ],
    )

    response = client.get("/admin/users")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "演示用户" in html
    assert 'href="/admin/users/2"' in html


def test_super_admin_dashboard_shows_system_counts(client, monkeypatch):
    login_admin(client)

    def fake_query_one(sql, params=None):
        if "COUNT(*) AS total FROM users" in sql and "is_active = 1" in sql:
            return {"total": 10}
        if "COUNT(*) AS total FROM users" in sql and "is_active = 0" in sql:
            return {"total": 2}
        if "COUNT(*) AS total FROM users" in sql:
            return {"total": 12}
        if "p.is_public_blocked = 1" in sql:
            return {"total": 3}
        if "p.is_active = 1" in sql:
            return {"total": 8}
        if "status = 'unread'" in sql:
            return {"total": 4}
        return {"total": 20}

    monkeypatch.setattr("app.admin.routes.query_one", fake_query_one)
    monkeypatch.setattr("app.admin.routes.query_all", lambda sql, params=None: [])

    response = client.get("/admin")

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "用户总数" in html
    assert "正常用户" in html
    assert "已封号用户" in html
    assert "公开简历" in html
    assert "封禁简历" in html


def test_normal_user_cannot_view_user_list(client):
    login_user(client, user_id=3)

    response = client.get("/admin/users")

    assert response.status_code == 403


def test_normal_user_cannot_view_site_settings(client, monkeypatch):
    login_user(client, user_id=3)
    monkeypatch.setattr("app.admin.routes.query_all", lambda sql, params=None: [])

    response = client.get("/admin/settings")

    assert response.status_code == 403


def test_super_admin_updates_user_account_status(client, monkeypatch):
    login_admin(client)
    monkeypatch.setattr(
        "app.admin.routes.query_one",
        lambda sql, params=None: {"id": 2, "role": "user", "username": "demo"},
    )
    executed = []
    monkeypatch.setattr(
        "app.admin.routes.execute",
        lambda sql, params=None: executed.append((sql, params)) or 1,
    )

    response = client.post(
        "/admin/users/2/account-status",
        data={"ban_reason": "违规注册"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "UPDATE users" in executed[0][0]
    assert "is_active = %s" in executed[0][0]
    assert executed[0][1] == (0, "违规注册", 2)


def test_super_admin_updates_user_publish_status(client, monkeypatch):
    login_admin(client)
    monkeypatch.setattr(
        "app.admin.routes.query_one",
        lambda sql, params=None: {"id": 2, "role": "user", "username": "demo"},
    )
    executed = []
    monkeypatch.setattr(
        "app.admin.routes.execute",
        lambda sql, params=None: executed.append((sql, params)) or 1,
    )

    response = client.post(
        "/admin/users/2/publish-status",
        data={"publish_ban_reason": "资料不完整"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "can_publish = %s" in executed[0][0]
    assert executed[0][1] == (0, "资料不完整", 2)


def test_super_admin_updates_user_resume_status(client, monkeypatch):
    login_admin(client)
    monkeypatch.setattr(
        "app.admin.routes.query_one",
        lambda sql, params=None: {"id": 2, "role": "user", "username": "demo"},
    )
    executed = []
    monkeypatch.setattr(
        "app.admin.routes.execute",
        lambda sql, params=None: executed.append((sql, params)) or 1,
    )

    response = client.post(
        "/admin/users/2/resume-status",
        data={"is_public_blocked": "y", "public_block_reason": "内容违规"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "UPDATE profile" in executed[0][0]
    assert "is_public_blocked = %s" in executed[0][0]
    assert executed[0][1] == (1, "内容违规", 2)


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
    assert 'href="/dashboard/skills/new"' in html
    assert 'href="/admin/skills/new"' not in html
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


def test_profile_post_forces_hidden_when_publish_disabled(client, monkeypatch):
    login_user(client, user_id=3)

    def fake_query_one(sql, params=None):
        if "FROM users" in sql:
            return {"can_publish": 0, "publish_ban_reason": "资料违规"}
        return {
            "id": 1,
            "name": "旧名字",
            "title": "旧职位",
            "is_active": 1,
            "avatar_path": None,
            "resume_file_path": None,
        }

    monkeypatch.setattr("app.admin.routes.query_one", fake_query_one)
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
    assert executed[0][1][-3] == 0


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
