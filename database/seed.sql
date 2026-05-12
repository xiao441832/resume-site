INSERT INTO site_settings (setting_key, setting_value, setting_type, description)
VALUES
    ('site_title', '多用户在线简历管理系统', 'string', '前台网站标题。'),
    ('seo_description', '多用户在线简历展示、项目经历、技能与留言管理。', 'string', '页面 SEO 描述。'),
    ('icp_text', '', 'string', '页脚展示的备案信息。'),
    ('messages_enabled', '1', 'boolean', '是否开放前台留言表单。')
ON DUPLICATE KEY UPDATE
    setting_value = VALUES(setting_value),
    setting_type = VALUES(setting_type),
    description = VALUES(description),
    updated_at = CURRENT_TIMESTAMP;
