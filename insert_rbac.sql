删除顺序
truncate table  sys_user_role
truncate table sys_role_permission
truncate table sys_role_menu
truncate table sys_user_user_permissions
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE sys_user;
truncate table sys_role
truncate table sys_permission
truncate table sys_menu
SET FOREIGN_KEY_CHECKS = 1;

-- ----------------------------
-- Records of sys_menu
-- ----------------------------
INSERT INTO `sys_menu` VALUES (1, 'home', '主页', 'home', 0, 10, '/', NULL, 'C', NULL, '2025-11-08', '2025-11-08 03:40:29.804293', NULL);
INSERT INTO `sys_menu` VALUES (2, 'sys', '系统管理', 'system', 0, 9999, '/sys', NULL, 'M', NULL, '2025-11-08', '2025-11-08 03:40:29.806326', NULL);
INSERT INTO `sys_menu` VALUES (3, 'user', '用户管理', 'user', 2, 1, '/sys/user', NULL, 'C', NULL, '2025-11-08', '2025-11-08 03:40:29.809312', NULL);
INSERT INTO `sys_menu` VALUES (4, 'role', '角色管理', 'role', 2, 2, '/sys/role', NULL, 'C', NULL, '2025-11-08', '2025-11-08 03:40:29.811275', NULL);
INSERT INTO `sys_menu` VALUES (5, 'menu', '菜单管理', 'menu', 2, 3, '/sys/menu', NULL, 'C', NULL, '2025-11-08', '2025-11-08 03:40:29.813269', NULL);
INSERT INTO `sys_menu` VALUES (6, 'devicemgmt', '设备管理', 'port', 0, 20, '/mainmgmt/list', NULL, 'M', NULL, '2025-11-08', '2025-11-16 05:49:58.607304', '设备管理');
INSERT INTO `sys_menu` VALUES (7, 'devicelist', '设备列表', 'servers', 6, 20, '/devicemgmt/list', NULL, 'C', NULL, '2025-11-08', '2025-11-08 13:49:17.560506', NULL);
INSERT INTO `sys_menu` VALUES (8, 'tollsys', '收费系统', 'Records', 0, 30, '/checklanesoft/list', NULL, 'M', NULL, '2025-11-16', '2025-11-18 11:31:29.798811', '收费 系统');
INSERT INTO `sys_menu` VALUES (12, 'tollsys:lanesoft', '车道软件信息', 'totp', 8, 1, '/checklanesoft/list', '', 'C', '', '2025-11-16', '2025-11-16 07:58:16.679701', '');
INSERT INTO `sys_menu` VALUES (13, 'tollsys:vehlossrate', '车牌识别率', 'flow', 8, 2, '/vehlossrate/list', NULL, 'C', NULL, '2025-11-18', '2025-11-20 05:48:29.430646', NULL);
INSERT INTO `sys_menu` VALUES (14, 'tollsys:holidayfree', '节假日免费参数', 'ubuntu', 8, 3, '/holidayfree/list', '', 'C', '', '2025-11-20', '2025-11-22 02:22:38.368835', '');
INSERT INTO `sys_menu` VALUES (15, 'tollsys:lanepsam', '车道psam卡信息', 'log', 8, 4, '/lanepsaminfo/list', '', 'C', '', '2025-11-22', '2025-11-22 02:28:01.348929', '');
INSERT INTO `sys_menu` VALUES (16, 'tollsys:gantrypsam', '门架PSAM卡信息', 'server-info', 8, 5, '/gantrypsaminfo/list', '', 'C', '', '2025-11-22', '2025-11-22 13:12:14.788687', '');
INSERT INTO `sys_menu` VALUES (17, 'pingdevices:list', '设备连通性检查', 'datasync', 8, 6, '/pingdevices/list', NULL, 'C', NULL, '2025-11-29', '2025-11-29 17:00:51.608902', NULL);

-- ----------------------------
-- Records of sys_permission
-- ----------------------------
INSERT INTO `sys_permission` VALUES (1, '查询用户列表', 'user:list', 'GET', '/api/auth/users', NULL, 3);
INSERT INTO `sys_permission` VALUES (2, '添加用户', 'user:add', 'POST', '/api/auth/users', NULL, 3);
INSERT INTO `sys_permission` VALUES (3, '修改用户', 'user:edit', 'PUT', '/api/auth/users/{userId}', NULL, 3);
INSERT INTO `sys_permission` VALUES (4, '删除用户', 'user:delete', 'DELETE', '/api/auth/users/{userId}', NULL, 3);
INSERT INTO `sys_permission` VALUES (5, '超级用户重置密码', 'user:resetpwd', 'POST', '/api/auth/changePassword', NULL, 3);
INSERT INTO `sys_permission` VALUES (6, '查询角色列表', 'role:list', 'GET', '/api/role/roles', NULL, 4);
INSERT INTO `sys_permission` VALUES (7, '添加角色', 'role:add', 'POST', '/api/role/roles', NULL, 4);
INSERT INTO `sys_permission` VALUES (8, '修改角色', 'role:edit', 'PUT', '/api/role/roles/{roleid}', NULL, 4);
INSERT INTO `sys_permission` VALUES (9, '删除角色', 'role:delete', 'DELETE', '/api/role/roles/{roleid}', NULL, 4);
INSERT INTO `sys_permission` VALUES (10, '分配角色权限', 'role:permission', 'POST', '/api/role/assign_menu', NULL, 4);
INSERT INTO `sys_permission` VALUES (11, '查询角色菜单列表', 'role:menuList', 'GET', '/api/role/role_menus/{roleId}', NULL, 4);
INSERT INTO `sys_permission` VALUES (12, '查看菜单列表', 'menu:list', 'GET', '/api/menu/menus', NULL, 5);
INSERT INTO `sys_permission` VALUES (13, '添加菜单', 'menu:add', 'POST', '/api/menu/menus', NULL, 5);
INSERT INTO `sys_permission` VALUES (14, '修改菜单', 'menu:edit', 'PUT', '/api/menu/menus/{menuId}', NULL, 5);
INSERT INTO `sys_permission` VALUES (15, '删除菜单', 'menu:delete', 'DELETE', '/api/menu/menus/{menuId}', NULL, 5);
INSERT INTO `sys_permission` VALUES (16, '查询权限列表', 'permission:list', 'GET', '/api/permission/permissions', NULL, 5);
INSERT INTO `sys_permission` VALUES (17, '添加权限', 'permission:add', 'POST', '/api/permission/permissions', NULL, 5);
INSERT INTO `sys_permission` VALUES (18, '修改权限', 'permission:edit', 'PUT', '/api/permission/permissions/{permissionId}', NULL, 5);
INSERT INTO `sys_permission` VALUES (19, '删除权限', 'permission:delete', 'DELETE', '/api/permission/permissions/{permissionId}', NULL, 5);
INSERT INTO `sys_permission` VALUES (20, '设备列表', 'devices:view', 'GET', '/devicemgmt/devices/', '', 7);
INSERT INTO `sys_permission` VALUES (21, '添加设备', 'devices:add', 'POST', '/devicemgmt/add', NULL, 7);
INSERT INTO `sys_permission` VALUES (22, '编辑设备', 'devices:edit', 'POST', '/devicemgmt/devices/{id}', '', 7);
INSERT INTO `sys_permission` VALUES (23, '删除设备', 'devices:delete', 'DELETE', '/devicemgmt/devices', '', 7);
INSERT INTO `sys_permission` VALUES (24, '获取设备类型', 'devices:device-types', 'GET', '/api/devicemgmt/device-types', '', 7);
INSERT INTO `sys_permission` VALUES (25, '获取子网类型', 'devices:subnet-types', 'GET', '/api/devicemgmt/subnet-types', '', 7);
INSERT INTO `sys_permission` VALUES (26, '批量上传', 'devices:upload', 'POST', 'api/devicemgmt/upload', '', 7);
INSERT INTO `sys_permission` VALUES (27, '导出设备信息', 'devices:download', 'GET', 'api/devicemgmt/download', '', 7);
INSERT INTO `sys_permission` VALUES (30, '车道软件信息', 'checklanesoft:view', 'GET', '/api/checklanesoft/checklanesoft', NULL, 12);
INSERT INTO `sys_permission` VALUES (31, '车牌识别率', 'vehlossrate:view', 'GET', '/api/vehlossrate/vehlossrate', NULL, 13);
INSERT INTO `sys_permission` VALUES (32, '车牌图像', 'vehlossrate:getimageurl', 'GET', '/api/vehlossrate/getimageurl', NULL, 13);
INSERT INTO `sys_permission` VALUES (33, '免费参数列表', 'holidayfree:view', 'GET', '/api/holidayfree/vholidayfree', '', 14);
INSERT INTO `sys_permission` VALUES (34, '车道psam卡信息列表', 'lanepsaminfo:view', 'GET', '/api/lanepsaminfo/lanepsaminfo', NULL, 15);
INSERT INTO `sys_permission` VALUES (35, '获取车道PSAM卡信息', 'lanepsaminfo:getpsam', 'GET', '/api/lanepsaminfo/getlanepsaminfo', '', 15);
INSERT INTO `sys_permission` VALUES (36, '编辑坏卡信息', 'lanepsaminfo:edit', 'POST', '/api/lanepsaminfo/lanepsaminfo/{psamno}', NULL, 15);
INSERT INTO `sys_permission` VALUES (37, '下载车道PSAM卡信息', 'lanepsaminfo:download', 'GET', '/api/lanepsaminfo/download', NULL, 15);
INSERT INTO `sys_permission` VALUES (38, '门架PSAM卡信息列表', 'gantrypsaminfo:view', 'GET', '/ap/gantrypsaminfo/gantrypasminfo', NULL, 16);
INSERT INTO `sys_permission` VALUES (39, '获取门架PSAM卡信息', 'gantrypsaminfo:getpsam', 'GET', '/api/gantrypsaminfo/gantrypsaminfo', NULL, 16);
INSERT INTO `sys_permission` VALUES (40, '编辑门架坏卡信息', 'gantrypsaminfo:edit', 'POST', '/api/gantrypsaminfo/gantrypsaminfo/{psamno}', NULL, 16);
INSERT INTO `sys_permission` VALUES (41, '下载门架PSAM卡信息', 'gantrypsaminfo:download', 'GET', '/api/gantrypsaminfo/download', NULL, 16);
INSERT INTO `sys_permission` VALUES (42, '编辑故障原因', 'checklanesoft:edit', 'POST', '/api/checklanesoft/checklanesoft/:id', NULL, 12);
INSERT INTO `sys_permission` VALUES (43, '新增编辑设备', 'devices:manage', 'POST', '/device/form/:mode(add|edit)/:id?', NULL, 7);
INSERT INTO `sys_permission` VALUES (44, 'ping结果列表', 'pingdevices:view', 'GET', '/api/pingdevices/list', NULL, 17);
INSERT INTO `sys_permission` VALUES (45, '批量ping', 'devices:batch-ping', 'POST', '/api/pingdevices/ping/batch', NULL, 17);

-- ----------------------------
-- Records of sys_role
-- ----------------------------
INSERT INTO `sys_role` VALUES (1, '超级用户', 'super_admin', '2025-11-08', '2025-11-08 06:05:51.236398', NULL);
INSERT INTO `sys_role` VALUES (2, '普通管理员', 'ordinary_admin', '2025-11-08', '2025-11-08 06:06:16.257597', NULL);
INSERT INTO `sys_role` VALUES (3, '普通用户', 'domestic-consumer', '2025-11-14', '2025-11-14 02:00:48.200865', NULL);

-- ----------------------------
-- Records of sys_role_menu
-- ----------------------------
INSERT INTO `sys_role_menu` VALUES (49, 1, 2);
INSERT INTO `sys_role_menu` VALUES (50, 2, 2);
INSERT INTO `sys_role_menu` VALUES (51, 3, 2);
INSERT INTO `sys_role_menu` VALUES (52, 4, 2);
INSERT INTO `sys_role_menu` VALUES (53, 6, 2);
INSERT INTO `sys_role_menu` VALUES (54, 7, 2);
INSERT INTO `sys_role_menu` VALUES (286, 1, 3);
INSERT INTO `sys_role_menu` VALUES (287, 6, 3);
INSERT INTO `sys_role_menu` VALUES (288, 7, 3);
INSERT INTO `sys_role_menu` VALUES (289, 8, 3);
INSERT INTO `sys_role_menu` VALUES (290, 12, 3);
INSERT INTO `sys_role_menu` VALUES (291, 13, 3);
INSERT INTO `sys_role_menu` VALUES (292, 14, 3);
INSERT INTO `sys_role_menu` VALUES (293, 15, 3);
INSERT INTO `sys_role_menu` VALUES (294, 16, 3);
INSERT INTO `sys_role_menu` VALUES (336, 1, 1);
INSERT INTO `sys_role_menu` VALUES (337, 2, 1);
INSERT INTO `sys_role_menu` VALUES (338, 3, 1);
INSERT INTO `sys_role_menu` VALUES (339, 4, 1);
INSERT INTO `sys_role_menu` VALUES (340, 5, 1);
INSERT INTO `sys_role_menu` VALUES (341, 6, 1);
INSERT INTO `sys_role_menu` VALUES (342, 7, 1);
INSERT INTO `sys_role_menu` VALUES (343, 8, 1);
INSERT INTO `sys_role_menu` VALUES (344, 12, 1);
INSERT INTO `sys_role_menu` VALUES (345, 13, 1);
INSERT INTO `sys_role_menu` VALUES (346, 14, 1);
INSERT INTO `sys_role_menu` VALUES (347, 15, 1);
INSERT INTO `sys_role_menu` VALUES (348, 16, 1);
INSERT INTO `sys_role_menu` VALUES (349, 17, 1);

-- ----------------------------
-- Records of sys_user_role
-- ----------------------------
INSERT INTO `sys_user_role` VALUES (1, 1, 1);
INSERT INTO `sys_user_role` VALUES (4, 3, 3);
INSERT INTO `sys_user_role` VALUES (5, 3, 4);
INSERT INTO `sys_user_role` VALUES (6, 3, 2);
INSERT INTO `sys_user_role` VALUES (7, 3, 5);

-- ----------------------------
-- Records of sys_user
-- ----------------------------
INSERT INTO `sys_user` VALUES ('pbkdf2_sha256$720000$ptB9H4fMAX9hAKtf1oFbyc$BEirY61vUPZa54sR4DqhNIKx86mVVZ63DQIAk6bZNmI=', '2025-12-04 16:09:35.336166', 0, 1, 'admin', '超级管理员', 'admin@example.com', '', 1, 1, '111.jpg', '2025-11-08', '2025-12-04 16:09:35.344695', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyaWQiOjEsImV4cCI6MTc2NDg2NDU3NX0.5yHdxZQjMJKkl7FNkRsL_2kKn_XeCAk-rFB5Zrve33E');
INSERT INTO `sys_user` VALUES ('pbkdf2_sha256$720000$7VBKfiTdqzrgzyvN2DATPG$H43TUSAbnqK60WgOcQnv7ZNNF/eh6ueXLLAiZFOE970=', '2025-11-27 05:29:32.338498', 0, 2, 'www', 'www', 'www@123.com', '13345676567', 1, 1, '111.jpg', '2025-11-13', '2025-11-27 05:29:32.344483', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyaWQiOjIsImV4cCI6MTc2NDI1MDE3Mn0.OAfBd50bvUCFE-xXJ0kcZrbqNcqcZ22UEwYI3TvEbVM');
INSERT INTO `sys_user` VALUES ('pbkdf2_sha256$720000$ogdlIfqOuYatcPp6txcrBz$QhT9soQNe+EfRfBVKbRDiAvIstflmELGTazVEmxI2QY=', '2025-11-23 08:00:38.631465', 0, 3, 'wxh', 'weixiaoheng', 'wei@123.com', '13345654456', 1, 1, '111.jpg', '2025-11-14', '2025-11-23 08:00:38.638447', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyaWQiOjMsImV4cCI6MTc2MzkxMzYzOH0.XAC32e1wA6_uOivt4pfgSKQWHo9HJYHFfySjTOOZ47E');
INSERT INTO `sys_user` VALUES ('pbkdf2_sha256$720000$nlxbVn4A2DNqnkeZ8N8x7R$xrVkzD0nGldu4bx8VRHQ1BxfkctEw5oIW9SYfLiifQo=', NULL, 0, 4, '111', '111', '111@123.com', '13322222222', 1, 1, '111.jpg', '2025-11-16', '2025-11-23 07:59:59.187390', NULL);
INSERT INTO `sys_user` VALUES ('pbkdf2_sha256$720000$EmJHkrQpiJmP3vP0mpZhOy$sd6klxhHKXWGdksk5DbAwFJM3nN8o1AsqSe+PuGIJIg=', NULL, 0, 5, 'aaa', 'aaa', 'aaa@163.com', '13345676543', 1, 1, '111.jpg', '2025-11-27', '2025-11-27 02:30:23.422231', NULL);


-- 查看某个用户能看到的所有菜单
SELECT DISTINCT m.* 
FROM sys_user u
JOIN sys_user_role ur ON u.id = ur.user_id
JOIN sys_role_menu rm ON ur.role_id = rm.role_id
JOIN sys_menu m ON rm.menu_id = m.id
WHERE u.id = '1' 
ORDER BY m.parent_id;

