from werkzeug.security import generate_password_hash


def test_login_page_renders(client):
    response = client.get("/auth/login")

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "用户登录" in html
    assert 'rel="icon"' in html


def test_admin_login_redirects_to_unified_login(client):
    response = client.get("/admin/login", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/auth/login")


def test_register_creates_normal_user(client, monkeypatch):
    executed = {}

    monkeypatch.setattr("app.auth.routes.find_user_by_username", lambda username: None)
    monkeypatch.setattr("app.auth.routes.find_user_by_email", lambda email: None)

    def fake_execute(sql, params):
        executed["sql"] = sql
        executed["params"] = params
        return 1

    monkeypatch.setattr("app.auth.routes.execute", fake_execute)

    response = client.post(
        "/auth/register",
        data={
            "username": "student",
            "email": "student@example.com",
            "display_name": "学生用户",
            "password": "secret123",
            "confirm_password": "secret123",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/auth/login")
    assert "INSERT INTO users" in executed["sql"]
    assert executed["params"][0] == "student"
    assert executed["params"][4] == "user"


def test_register_rejects_duplicate_username(client, monkeypatch):
    monkeypatch.setattr(
        "app.auth.routes.find_user_by_username",
        lambda username: {"id": 1, "username": username},
    )
    monkeypatch.setattr("app.auth.routes.find_user_by_email", lambda email: None)

    response = client.post(
        "/auth/register",
        data={
            "username": "student",
            "email": "student@example.com",
            "display_name": "学生用户",
            "password": "secret123",
            "confirm_password": "secret123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "用户名已存在" in response.get_data(as_text=True)


def test_login_success_sets_unified_session(client, monkeypatch):
    monkeypatch.setattr(
        "app.auth.routes.find_user_by_login",
        lambda login_name: {
            "id": 7,
            "username": "student",
            "password_hash": generate_password_hash("secret123"),
            "display_name": "学生用户",
            "role": "user",
            "is_active": 1,
        },
    )
    monkeypatch.setattr("app.auth.routes.mark_last_login", lambda user_id: None)

    response = client.post(
        "/auth/login",
        data={"username": "student", "password": "secret123"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")
    with client.session_transaction() as session:
        assert session["user_id"] == 7
        assert session["username"] == "student"
        assert session["display_name"] == "学生用户"
        assert session["role"] == "user"


def test_super_admin_login_redirects_to_admin_dashboard(client, monkeypatch):
    monkeypatch.setattr(
        "app.auth.routes.find_user_by_login",
        lambda login_name: {
            "id": 8,
            "username": "admin",
            "password_hash": generate_password_hash("secret123"),
            "display_name": "管理员",
            "role": "super_admin",
            "is_active": 1,
        },
    )
    monkeypatch.setattr("app.auth.routes.mark_last_login", lambda user_id: None)

    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "secret123"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin")


def test_legacy_admin_role_does_not_enter_admin_dashboard(client, monkeypatch):
    monkeypatch.setattr(
        "app.auth.routes.find_user_by_login",
        lambda login_name: {
            "id": 8,
            "username": "admin",
            "password_hash": generate_password_hash("secret123"),
            "display_name": "旧管理员",
            "role": "admin",
            "is_active": 1,
        },
    )
    monkeypatch.setattr("app.auth.routes.mark_last_login", lambda user_id: None)

    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "secret123"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")


def test_login_rejects_wrong_password(client, monkeypatch):
    monkeypatch.setattr(
        "app.auth.routes.find_user_by_login",
        lambda login_name: {
            "id": 7,
            "username": "student",
            "password_hash": generate_password_hash("secret123"),
            "display_name": "学生用户",
            "role": "user",
            "is_active": 1,
        },
    )

    response = client.post(
        "/auth/login",
        data={"username": "student", "password": "bad-password"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "用户名或密码错误" in response.get_data(as_text=True)


def test_login_rejects_disabled_user(client, monkeypatch):
    monkeypatch.setattr(
        "app.auth.routes.find_user_by_login",
        lambda login_name: {
            "id": 7,
            "username": "student",
            "password_hash": generate_password_hash("secret123"),
            "display_name": "学生用户",
            "role": "user",
            "is_active": 0,
        },
    )

    response = client.post(
        "/auth/login",
        data={"username": "student", "password": "secret123"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "账号已被禁用" in response.get_data(as_text=True)
