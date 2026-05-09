from werkzeug.security import generate_password_hash


def test_login_page_renders(client):
    response = client.get("/admin/login")

    assert response.status_code == 200
    assert "管理员登录" in response.get_data(as_text=True)


def test_login_success_sets_session(client, monkeypatch):
    monkeypatch.setattr(
        "app.auth.routes.find_admin_by_username",
        lambda username: {
            "id": 7,
            "username": username,
            "password_hash": generate_password_hash("secret123"),
            "display_name": "Admin",
            "is_active": 1,
        },
    )
    monkeypatch.setattr("app.auth.routes.mark_last_login", lambda admin_id: None)

    response = client.post(
        "/admin/login",
        data={"username": "admin", "password": "secret123"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    with client.session_transaction() as session:
        assert session["admin_user_id"] == 7
        assert session["admin_username"] == "admin"


def test_login_rejects_wrong_password(client, monkeypatch):
    monkeypatch.setattr(
        "app.auth.routes.find_admin_by_username",
        lambda username: {
            "id": 7,
            "username": username,
            "password_hash": generate_password_hash("secret123"),
            "display_name": "Admin",
            "is_active": 1,
        },
    )

    response = client.post(
        "/admin/login",
        data={"username": "admin", "password": "bad-password"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "用户名或密码错误" in response.get_data(as_text=True)
