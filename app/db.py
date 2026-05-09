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
    try:
        with db.cursor() as cursor:
            affected = cursor.execute(sql, params)
        db.commit()
        return affected
    except Exception:
        db.rollback()
        raise


def execute_many(sql: str, params: Iterable[Iterable[Any] | dict[str, Any]]) -> int:
    db = get_db()
    try:
        with db.cursor() as cursor:
            affected = cursor.executemany(sql, params)
        db.commit()
        return affected
    except Exception:
        db.rollback()
        raise


def split_sql_script(script: str) -> list[str]:
    statements: list[str] = []
    current: list[str] = []
    quote: str | None = None
    escape_next = False
    in_line_comment = False
    index = 0

    while index < len(script):
        char = script[index]
        next_char = script[index + 1] if index + 1 < len(script) else ""

        if in_line_comment:
            if char in "\r\n":
                in_line_comment = False
                current.append(char)
            index += 1
            continue

        if quote:
            current.append(char)
            if escape_next:
                escape_next = False
            elif char == "\\":
                escape_next = True
            elif char == quote:
                quote = None
            index += 1
            continue

        if char in {"'", '"'}:
            quote = char
            current.append(char)
        elif char == "-" and next_char == "-":
            in_line_comment = True
            index += 1
        elif char == ";":
            statement = "".join(current).strip()
            if statement:
                statements.append(statement)
            current = []
        else:
            current.append(char)

        index += 1

    statement = "".join(current).strip()
    if statement:
        statements.append(statement)
    return statements


def execute_script(script: str) -> int:
    db = get_db()
    statements = split_sql_script(script)
    try:
        with db.cursor() as cursor:
            for statement in statements:
                cursor.execute(statement)
        db.commit()
        return len(statements)
    except Exception:
        db.rollback()
        raise
