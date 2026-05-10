from dataclasses import dataclass
from typing import Type

from flask_wtf import FlaskForm

from app.admin.forms import (
    CertificateForm,
    EducationForm,
    ExperienceForm,
    ProjectForm,
    SkillForm,
)


@dataclass(frozen=True)
class ResourceConfig:
    key: str
    table: str
    title: str
    form_class: Type[FlaskForm]
    columns: tuple[str, ...]
    list_columns: tuple[str, ...]


RESOURCE_CONFIGS = {
    "skills": ResourceConfig(
        key="skills",
        table="skills",
        title="技能",
        form_class=SkillForm,
        columns=("name", "category", "proficiency", "icon", "color", "sort_order", "is_active"),
        list_columns=("name", "category", "proficiency", "sort_order", "is_active"),
    ),
    "experiences": ResourceConfig(
        key="experiences",
        table="experiences",
        title="工作 / 实习经历",
        form_class=ExperienceForm,
        columns=(
            "company",
            "position",
            "location",
            "start_date",
            "end_date",
            "is_current",
            "description",
            "sort_order",
            "is_active",
        ),
        list_columns=("company", "position", "location", "sort_order", "is_active"),
    ),
    "projects": ResourceConfig(
        key="projects",
        table="projects",
        title="项目经历",
        form_class=ProjectForm,
        columns=(
            "name",
            "role",
            "tech_stack",
            "project_url",
            "source_url",
            "cover_image_path",
            "start_date",
            "end_date",
            "summary",
            "highlights",
            "sort_order",
            "is_active",
        ),
        list_columns=("name", "role", "tech_stack", "sort_order", "is_active"),
    ),
    "education": ResourceConfig(
        key="education",
        table="education",
        title="教育经历",
        form_class=EducationForm,
        columns=(
            "school",
            "major",
            "degree",
            "location",
            "start_date",
            "end_date",
            "description",
            "sort_order",
            "is_active",
        ),
        list_columns=("school", "major", "degree", "sort_order", "is_active"),
    ),
    "certificates": ResourceConfig(
        key="certificates",
        table="certificates",
        title="证书",
        form_class=CertificateForm,
        columns=(
            "name",
            "issuer",
            "issue_date",
            "certificate_url",
            "image_path",
            "description",
            "sort_order",
            "is_active",
        ),
        list_columns=("name", "issuer", "issue_date", "sort_order", "is_active"),
    ),
}


def get_resource_config(key: str) -> ResourceConfig:
    if key not in RESOURCE_CONFIGS:
        raise KeyError(key)
    return RESOURCE_CONFIGS[key]


def build_insert_sql(config: ResourceConfig) -> str:
    columns = ", ".join(config.columns)
    placeholders = ", ".join(["%s"] * len(config.columns))
    return f"INSERT INTO {config.table} ({columns}) VALUES ({placeholders})"


def build_update_sql(config: ResourceConfig) -> str:
    assignments = ", ".join(f"{column} = %s" for column in config.columns)
    return f"UPDATE {config.table} SET {assignments} WHERE id = %s"
