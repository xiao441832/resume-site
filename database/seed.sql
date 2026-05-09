INSERT INTO site_settings (setting_key, setting_value, setting_type, description)
VALUES
    ('site_name', 'Resume Site', 'string', 'Public website name.'),
    ('site_description', 'Personal resume and portfolio site.', 'string', 'Short SEO description.'),
    ('contact_email', 'admin@example.com', 'string', 'Default public contact email.'),
    ('allow_messages', '1', 'boolean', 'Whether the public contact form accepts messages.')
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
    'Your Name',
    'Software Engineer',
    'Shanghai',
    'admin@example.com',
    'A concise personal summary for the public resume site.',
    'Open to opportunities',
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
