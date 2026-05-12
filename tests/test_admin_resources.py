from app.admin.resources import RESOURCE_CONFIGS, build_insert_sql, build_update_sql


def test_resource_registry_contains_resume_modules():
    assert set(RESOURCE_CONFIGS) == {
        "skills",
        "experiences",
        "projects",
        "education",
        "certificates",
    }


def test_build_insert_sql_uses_config_columns():
    config = RESOURCE_CONFIGS["skills"]

    sql = build_insert_sql(config)

    assert sql == (
        "INSERT INTO skills (user_id, name, category, proficiency, icon, color, sort_order, is_active) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    )


def test_build_update_sql_excludes_id_and_timestamps():
    config = RESOURCE_CONFIGS["skills"]

    sql = build_update_sql(config)

    assert sql == (
        "UPDATE skills SET name = %s, category = %s, proficiency = %s, icon = %s, "
        "color = %s, sort_order = %s, is_active = %s WHERE id = %s AND user_id = %s"
    )
