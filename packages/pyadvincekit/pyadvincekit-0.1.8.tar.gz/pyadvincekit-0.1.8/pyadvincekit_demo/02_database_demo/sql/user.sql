-- 创建表: user
-- 用户表
CREATE TABLE `user` (
  `id` VARCHAR(36) NOT NULL DEFAULT '(UUID())' COMMENT '主键ID',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `username` VARCHAR(50) COMMENT '用户名',
  `email` VARCHAR(320) COMMENT '电子邮件',
  `full_name` VARCHAR(100) COMMENT '全名',
  `age` INTEGER COMMENT '年龄',
  `is_active` BOOLEAN COMMENT '是否激活',
  `hashed_password` VARCHAR(225) COMMENT '密码',
  PRIMARY KEY (`id`, `username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE UNIQUE INDEX `UIDX1_user` ON `user` (`username`);
