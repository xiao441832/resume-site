from app.db import build_connection_kwargs, split_sql_script


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
