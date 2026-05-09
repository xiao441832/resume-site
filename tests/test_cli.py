from pathlib import Path

from app.cli import load_sql_file


def test_load_sql_file_reads_utf8_text(tmp_path):
    sql_file = tmp_path / "sample.sql"
    sql_file.write_text("SELECT '中文';", encoding="utf-8")

    assert load_sql_file(sql_file) == "SELECT '中文';"
