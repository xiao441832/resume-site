from collections.abc import Iterable
from typing import Any

import pymysql
from flask import current_app, g
from pymysql.cursors import DictCursor


def build_connection_kwargs(config: dict[str, Any]) -> dict[str, Any]:
    return {
        "host": config["MYSQL_HOST"],
        "port": config["MYSQL_PORT"],
        "user": config["MYSQL_USER"],
        "password": config["MYSQL_PASSWORD"],
        "database": config["MYSQL_DATABASE"],
        "charset": config["MYSQL_CHARSET"],
        "cursorclass": DictCursor,
        "autocommit": False,
    }


def get_db():
    if "db" not in g:
        g.db = pymysql.connect(**build_connection_kwargs(current_app.config))
    return g.db


def close_db(error: BaseException | None = None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query_all(
    sql: str, params: Iterable[Any] | dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    with get_db().cursor() as cursor:
        cursor.execute(sql, params)
        return list(cursor.fetchall())


def query_one(
    sql: str, params: Iterable[Any] | dict[str, Any] | None = None
) -> dict[str, Any] | None:
    with get_db().cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.fetchone()


def execute(sql: str, params: Iterable[Any] | dict[str, Any] | None = None) -> int:
    db = get_db()
    with db.cursor() as cursor:
        affected = cursor.execute(sql, params)
    db.commit()
    return affected


def execute_many(sql: str, params: Iterable[Iterable[Any] | dict[str, Any]]) -> int:
    db = get_db()
    with db.cursor() as cursor:
        affected = cursor.executemany(sql, params)
    db.commit()
    return affected


def split_sql_script(script: str) -> list[str]:
    lines: list[str] = []
    for raw_line in script.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("--"):
            continue
        lines.append(raw_line)

    joined = "\n".join(lines)
    return [
        statement.strip().rstrip(";")
        for statement in joined.split(";")
        if statement.strip()
    ]


def execute_script(script: str) -> int:
    db = get_db()
    statements = split_sql_script(script)
    with db.cursor() as cursor:
        for statement in statements:
            cursor.execute(statement)
    db.commit()
    return len(statements)
