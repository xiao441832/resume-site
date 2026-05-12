from pathlib import Path

from app.cli import load_sql_file

BASE_DIR = Path(__file__).resolve().parent.parent


def table_block(schema: str, table_name: str) -> str:
    start = schema.index(f"CREATE TABLE IF NOT EXISTS {table_name} (")
    end = schema.index(") ENGINE=InnoDB", start)
    return schema[start:end]


def test_load_sql_file_reads_utf8_text(tmp_path):
    sql_file = tmp_path / "sample.sql"
    sql_file.write_text("SELECT '中文';", encoding="utf-8")

    assert load_sql_file(sql_file) == "SELECT '中文';"


def test_schema_sql_matches_task_contract_fragments():
    schema = load_sql_file(BASE_DIR / "database" / "schema.sql")
    users = table_block(schema, "users")
    profile = table_block(schema, "profile")
    skills = table_block(schema, "skills")
    experiences = table_block(schema, "experiences")
    messages = table_block(schema, "messages")
    uploads = table_block(schema, "uploads")
    site_settings = table_block(schema, "site_settings")

    assert "role ENUM('user','admin') NOT NULL DEFAULT 'user'" in users
    assert "email VARCHAR(255) NOT NULL" in users
    assert "UNIQUE KEY uq_users_username (username)" in users
    assert "UNIQUE KEY uq_users_email (email)" in users
    assert "user_id BIGINT UNSIGNED NOT NULL" in profile
    assert "phone VARCHAR(80) NULL" in profile
    assert "job_status VARCHAR(160) NULL" in profile
    assert "UNIQUE KEY uq_profile_user (user_id)" in profile
    assert "CONSTRAINT fk_profile_user" in profile
    assert "user_id BIGINT UNSIGNED NOT NULL" in skills
    assert "proficiency TINYINT UNSIGNED NOT NULL DEFAULT 80" in skills
    assert "KEY idx_skills_user_public_order" in skills
    assert "user_id BIGINT UNSIGNED NOT NULL" in experiences
    assert "start_date DATE NULL" in experiences
    assert "target_user_id BIGINT UNSIGNED NOT NULL" in messages
    assert "KEY idx_messages_target_status_created" in messages
    assert "user_id BIGINT UNSIGNED NULL" in uploads
    assert "CONSTRAINT fk_uploads_user" in uploads
    assert "KEY idx_uploads_purpose_created (upload_purpose, created_at)" in uploads
    assert "UNIQUE KEY uq_site_settings_key (setting_key)" in site_settings


def test_seed_sql_uses_expected_site_setting_keys_only():
    seed = load_sql_file(BASE_DIR / "database" / "seed.sql")

    for key in ("site_title", "seo_description", "icp_text", "messages_enabled"):
        assert f"'{key}'" in seed

    for old_key in ("site_name", "site_description", "allow_messages", "contact_email"):
        assert f"'{old_key}'" not in seed
