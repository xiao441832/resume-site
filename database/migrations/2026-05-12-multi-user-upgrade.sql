-- 多用户在线简历管理系统升级脚本
-- 执行前请先完整备份生产数据库。
-- 本脚本用于把旧版单用户简历库升级为多用户结构。

CREATE TABLE IF NOT EXISTS users (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    username VARCHAR(80) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(120) NOT NULL,
    role ENUM('user','admin') NOT NULL DEFAULT 'user',
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    last_login_at DATETIME NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_users_username (username),
    UNIQUE KEY uq_users_email (email),
    KEY idx_users_role_active (role, is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO users (username, email, password_hash, display_name, role, is_active, last_login_at)
SELECT username, COALESCE(email, 'admin@example.com'), password_hash, display_name, 'admin', is_active, last_login_at
FROM admin_users
WHERE NOT EXISTS (SELECT 1 FROM users WHERE users.username = admin_users.username)
LIMIT 1;

INSERT INTO users (username, email, password_hash, display_name, role, is_active)
SELECT 'demo', 'demo@example.com', password_hash, '演示用户', 'user', 1
FROM users
WHERE role = 'admin'
  AND NOT EXISTS (SELECT 1 FROM users AS existing_user WHERE existing_user.username = 'demo')
LIMIT 1;

SET @default_user_id := (SELECT id FROM users WHERE username = 'demo' LIMIT 1);

ALTER TABLE profile ADD COLUMN user_id BIGINT UNSIGNED NULL AFTER id;
ALTER TABLE skills ADD COLUMN user_id BIGINT UNSIGNED NULL AFTER id;
ALTER TABLE experiences ADD COLUMN user_id BIGINT UNSIGNED NULL AFTER id;
ALTER TABLE projects ADD COLUMN user_id BIGINT UNSIGNED NULL AFTER id;
ALTER TABLE education ADD COLUMN user_id BIGINT UNSIGNED NULL AFTER id;
ALTER TABLE certificates ADD COLUMN user_id BIGINT UNSIGNED NULL AFTER id;
ALTER TABLE messages ADD COLUMN target_user_id BIGINT UNSIGNED NULL AFTER id;
ALTER TABLE uploads ADD COLUMN user_id BIGINT UNSIGNED NULL AFTER id;

UPDATE profile SET user_id = @default_user_id WHERE user_id IS NULL;
UPDATE skills SET user_id = @default_user_id WHERE user_id IS NULL;
UPDATE experiences SET user_id = @default_user_id WHERE user_id IS NULL;
UPDATE projects SET user_id = @default_user_id WHERE user_id IS NULL;
UPDATE education SET user_id = @default_user_id WHERE user_id IS NULL;
UPDATE certificates SET user_id = @default_user_id WHERE user_id IS NULL;
UPDATE messages SET target_user_id = @default_user_id WHERE target_user_id IS NULL;
UPDATE uploads SET user_id = uploader_id WHERE user_id IS NULL AND uploader_id IS NOT NULL;

ALTER TABLE profile MODIFY user_id BIGINT UNSIGNED NOT NULL;
ALTER TABLE skills MODIFY user_id BIGINT UNSIGNED NOT NULL;
ALTER TABLE experiences MODIFY user_id BIGINT UNSIGNED NOT NULL;
ALTER TABLE projects MODIFY user_id BIGINT UNSIGNED NOT NULL;
ALTER TABLE education MODIFY user_id BIGINT UNSIGNED NOT NULL;
ALTER TABLE certificates MODIFY user_id BIGINT UNSIGNED NOT NULL;
ALTER TABLE messages MODIFY target_user_id BIGINT UNSIGNED NOT NULL;

ALTER TABLE profile ADD UNIQUE KEY uq_profile_user (user_id);
ALTER TABLE skills ADD KEY idx_skills_user_public_order (user_id, is_active, sort_order, id);
ALTER TABLE experiences ADD KEY idx_experiences_user_public_order (user_id, is_active, sort_order, start_date, id);
ALTER TABLE projects ADD KEY idx_projects_user_public_order (user_id, is_active, sort_order, start_date, id);
ALTER TABLE education ADD KEY idx_education_user_public_order (user_id, is_active, sort_order, start_date, id);
ALTER TABLE certificates ADD KEY idx_certificates_user_public_order (user_id, is_active, sort_order, issue_date, id);
ALTER TABLE messages ADD KEY idx_messages_target_status_created (target_user_id, status, created_at);
ALTER TABLE uploads ADD KEY idx_uploads_user_id (user_id);

ALTER TABLE profile
    ADD CONSTRAINT fk_profile_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE;
ALTER TABLE skills
    ADD CONSTRAINT fk_skills_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE;
ALTER TABLE experiences
    ADD CONSTRAINT fk_experiences_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE;
ALTER TABLE projects
    ADD CONSTRAINT fk_projects_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE;
ALTER TABLE education
    ADD CONSTRAINT fk_education_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE;
ALTER TABLE certificates
    ADD CONSTRAINT fk_certificates_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE;
ALTER TABLE messages
    ADD CONSTRAINT fk_messages_target_user FOREIGN KEY (target_user_id) REFERENCES users (id) ON DELETE CASCADE;
ALTER TABLE uploads
    ADD CONSTRAINT fk_uploads_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL;

UPDATE site_settings
SET setting_value = '多用户在线简历管理系统'
WHERE setting_key = 'site_title';

UPDATE site_settings
SET setting_value = '多用户在线简历展示、项目经历、技能与留言管理。'
WHERE setting_key = 'seo_description';
