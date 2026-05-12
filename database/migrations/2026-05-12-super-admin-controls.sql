-- 超级管理员用户管控增量迁移。
-- 线上数据无保留价值时，可以直接重建数据库并执行 database/schema.sql。

ALTER TABLE users MODIFY role ENUM('super_admin','user','admin') NOT NULL DEFAULT 'user';

ALTER TABLE users
    ADD COLUMN can_publish TINYINT(1) NOT NULL DEFAULT 1 AFTER is_active,
    ADD COLUMN ban_reason VARCHAR(255) NULL AFTER can_publish,
    ADD COLUMN publish_ban_reason VARCHAR(255) NULL AFTER ban_reason;

UPDATE users SET role = 'super_admin' WHERE role = 'admin';

ALTER TABLE users MODIFY role ENUM('super_admin','user') NOT NULL DEFAULT 'user';

ALTER TABLE users
    ADD KEY idx_users_publish_active (role, is_active, can_publish);

ALTER TABLE profile
    ADD COLUMN is_public_blocked TINYINT(1) NOT NULL DEFAULT 0 AFTER is_active,
    ADD COLUMN public_block_reason VARCHAR(255) NULL AFTER is_public_blocked;

ALTER TABLE profile
    DROP KEY idx_profile_public,
    ADD KEY idx_profile_public (is_active, is_public_blocked);
