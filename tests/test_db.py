import pytest

from app import db
from app.db import build_connection_kwargs, execute, execute_many, execute_script, split_sql_script


def test_build_connection_kwargs_uses_app_config(app):
    kwargs = build_connection_kwargs(app.config)

    assert kwargs["host"] == "localhost"
    assert kwargs["port"] == 3306
    assert kwargs["charset"] == "utf8mb4"
    assert kwargs["cursorclass"].__name__ == "DictCursor"


def test_split_sql_script_ignores_empty_statements_and_line_comments():
    script = """
    -- first table
    CREATE TABLE one (id INT);

    -- second table
    CREATE TABLE two (id INT);
    """

    assert split_sql_script(script) == [
        "CREATE TABLE one (id INT)",
        "CREATE TABLE two (id INT)",
    ]


def test_split_sql_script_preserves_semicolon_inside_strings():
    script = """
    INSERT INTO profile (summary) VALUES ('Uses Flask; MySQL');
    SELECT "Bootstrap; Jinja2";
    """

    assert split_sql_script(script) == [
        "INSERT INTO profile (summary) VALUES ('Uses Flask; MySQL')",
        'SELECT "Bootstrap; Jinja2"',
    ]


class FakeCursor:
    def __init__(self, should_fail=False):
        self.should_fail = should_fail

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def execute(self, sql, params=None):
        if self.should_fail:
            raise RuntimeError("database write failed")
        return 1

    def executemany(self, sql, params):
        if self.should_fail:
            raise RuntimeError("database write failed")
        return 2


class FakeConnection:
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.committed = False
        self.rolled_back = False

    def cursor(self):
        return FakeCursor(self.should_fail)

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True


@pytest.mark.parametrize(
    "helper,args",
    [
        (execute, ("INSERT INTO skills (name) VALUES (%s)", ("Flask",))),
        (
            execute_many,
            ("INSERT INTO skills (name) VALUES (%s)", [("Flask",), ("MySQL",)]),
        ),
        (execute_script, ("INSERT INTO skills (name) VALUES ('Flask');",)),
    ],
)
def test_write_helpers_rollback_on_failure(monkeypatch, helper, args):
    fake_db = FakeConnection(should_fail=True)
    monkeypatch.setattr(db, "get_db", lambda: fake_db)

    with pytest.raises(RuntimeError, match="database write failed"):
        helper(*args)

    assert fake_db.rolled_back is True
    assert fake_db.committed is False
