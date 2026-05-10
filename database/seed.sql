INSERT INTO site_settings (setting_key, setting_value, setting_type, description)
VALUES
    ('site_title', '个人简历网站', 'string', '前台网站标题。'),
    ('seo_description', '个人简历、项目经历、技能与联系方式展示。', 'string', '页面 SEO 描述。'),
    ('icp_text', '', 'string', '页脚展示的备案信息。'),
    ('messages_enabled', '1', 'boolean', '是否开放前台留言表单。')
ON DUPLICATE KEY UPDATE
    setting_value = VALUES(setting_value),
    setting_type = VALUES(setting_type),
    description = VALUES(description),
    updated_at = CURRENT_TIMESTAMP;

INSERT INTO profile (
    id,
    name,
    title,
    city,
    email,
    summary,
    job_status,
    is_active
) VALUES (
    1,
    '你的姓名',
    '软件工程师',
    '上海',
    'admin@example.com',
    '这里填写一段适合展示在前台首页的个人简介。',
    '正在寻找合适的机会',
    1
)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    title = VALUES(title),
    city = VALUES(city),
    email = VALUES(email),
    summary = VALUES(summary),
    job_status = VALUES(job_status),
    is_active = VALUES(is_active),
    updated_at = CURRENT_TIMESTAMP;
