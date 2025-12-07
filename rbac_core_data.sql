-- MySQL dump 10.13  Distrib 8.0.35, for Win64 (x86_64)
--
-- Host: localhost    Database: mainmgmt_vue_new_db
-- ------------------------------------------------------
-- Server version	8.0.35

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Dumping data for table `sys_menu`
--

LOCK TABLES `sys_menu` WRITE;
/*!40000 ALTER TABLE `sys_menu` DISABLE KEYS */;
INSERT INTO `sys_menu` (`id`, `name`, `text`, `icon`, `parent_id`, `order_num`, `path`, `component`, `menu_type`, `perms`, `create_time`, `update_time`, `remark`) VALUES (1,'home','主页','home',0,10,'/',NULL,'C',NULL,'2025-11-08','2025-11-08 03:40:29.804293',NULL),(2,'sys','系统管理','system',0,9999,'/sys',NULL,'M',NULL,'2025-11-08','2025-11-08 03:40:29.806326',NULL),(3,'user','用户管理','user',2,1,'/sys/user',NULL,'C',NULL,'2025-11-08','2025-11-08 03:40:29.809312',NULL),(4,'role','角色管理','role',2,2,'/sys/role',NULL,'C',NULL,'2025-11-08','2025-11-08 03:40:29.811275',NULL),(5,'menu','菜单管理','menu',2,3,'/sys/menu',NULL,'C',NULL,'2025-11-08','2025-11-08 03:40:29.813269',NULL),(6,'devicemgmt','设备管理','port',0,20,'/mainmgmt/list',NULL,'M',NULL,'2025-11-08','2025-11-16 05:49:58.607304','设备管理'),(7,'devicelist','设备列表','servers',6,20,'/devicemgmt/list',NULL,'C',NULL,'2025-11-08','2025-11-08 13:49:17.560506',NULL),(8,'tollsys','收费系统','Records',0,30,'/checklanesoft/list',NULL,'M',NULL,'2025-11-16','2025-11-18 11:31:29.798811','收费 系统'),(12,'tollsys:lanesoft','车道软件信息','totp',8,1,'/checklanesoft/list','','C','','2025-11-16','2025-11-16 07:58:16.679701',''),(13,'tollsys:vehlossrate','车牌识别率','flow',8,2,'/vehlossrate/list',NULL,'C',NULL,'2025-11-18','2025-11-20 05:48:29.430646',NULL),(14,'tollsys:holidayfree','节假日免费参数','ubuntu',8,3,'/holidayfree/list','','C','','2025-11-20','2025-11-22 02:22:38.368835',''),(15,'tollsys:lanepsam','车道psam卡信息','log',8,4,'/lanepsaminfo/list','','C','','2025-11-22','2025-11-22 02:28:01.348929',''),(16,'tollsys:gantrypsam','门架PSAM卡信息','server-info',8,5,'/gantrypsaminfo/list','','C','','2025-11-22','2025-11-22 13:12:14.788687',''),(17,'pingdevices:list','设备连通性检查','datasync',8,6,'/pingdevices/list',NULL,'C',NULL,'2025-11-29','2025-11-29 17:00:51.608902',NULL);
/*!40000 ALTER TABLE `sys_menu` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `sys_permission`
--

LOCK TABLES `sys_permission` WRITE;
/*!40000 ALTER TABLE `sys_permission` DISABLE KEYS */;
INSERT INTO `sys_permission` (`id`, `name`, `code`, `request_method`, `url_path`, `remark`, `menu_id`) VALUES (1,'查询用户列表','user:list','GET','/api/auth/users',NULL,3),(2,'添加用户','user:add','POST','/api/auth/users',NULL,3),(3,'修改用户','user:edit','PUT','/api/auth/users/{userId}',NULL,3),(4,'删除用户','user:delete','DELETE','/api/auth/users/{userId}',NULL,3),(5,'超级用户重置密码','user:resetpwd','POST','/api/auth/changePassword',NULL,3),(6,'查询角色列表','role:list','GET','/api/role/roles',NULL,4),(7,'添加角色','role:add','POST','/api/role/roles',NULL,4),(8,'修改角色','role:edit','PUT','/api/role/roles/{roleid}',NULL,4),(9,'删除角色','role:delete','DELETE','/api/role/roles/{roleid}',NULL,4),(10,'分配角色权限','role:permission','POST','/api/role/assign_menu',NULL,4),(11,'查询角色菜单列表','role:menuList','GET','/api/role/role_menus/{roleId}',NULL,4),(12,'查看菜单列表','menu:list','GET','/api/menu/menus',NULL,5),(13,'添加菜单','menu:add','POST','/api/menu/menus',NULL,5),(14,'修改菜单','menu:edit','PUT','/api/menu/menus/{menuId}',NULL,5),(15,'删除菜单','menu:delete','DELETE','/api/menu/menus/{menuId}',NULL,5),(16,'查询权限列表','permission:list','GET','/api/permission/permissions',NULL,5),(17,'添加权限','permission:add','POST','/api/permission/permissions',NULL,5),(18,'修改权限','permission:edit','PUT','/api/permission/permissions/{permissionId}',NULL,5),(19,'删除权限','permission:delete','DELETE','/api/permission/permissions/{permissionId}',NULL,5),(20,'设备列表','devices:view','GET','/devicemgmt/devices/','',7),(21,'添加设备','devices:add','POST','/devicemgmt/add',NULL,7),(22,'编辑设备','devices:edit','POST','/devicemgmt/devices/{id}','',7),(23,'删除设备','devices:delete','DELETE','/devicemgmt/devices','',7),(24,'获取设备类型','devices:device-types','GET','/api/devicemgmt/device-types','',7),(25,'获取子网类型','devices:subnet-types','GET','/api/devicemgmt/subnet-types','',7),(26,'批量上传','devices:upload','POST','api/devicemgmt/upload','',7),(27,'导出设备信息','devices:download','GET','api/devicemgmt/download','',7),(30,'车道软件信息','checklanesoft:view','GET','/api/checklanesoft/checklanesoft',NULL,12),(31,'车牌识别率','vehlossrate:view','GET','/api/vehlossrate/vehlossrate',NULL,13),(32,'车牌图像','vehlossrate:getimageurl','GET','/api/vehlossrate/getimageurl',NULL,13),(33,'免费参数列表','holidayfree:view','GET','/api/holidayfree/vholidayfree','',14),(34,'车道psam卡信息列表','lanepsaminfo:view','GET','/api/lanepsaminfo/lanepsaminfo',NULL,15),(35,'获取车道PSAM卡信息','lanepsaminfo:getpsam','GET','/api/lanepsaminfo/getlanepsaminfo','',15),(36,'编辑坏卡信息','lanepsaminfo:edit','POST','/api/lanepsaminfo/lanepsaminfo/{psamno}',NULL,15),(37,'下载车道PSAM卡信息','lanepsaminfo:download','GET','/api/lanepsaminfo/download',NULL,15),(38,'门架PSAM卡信息列表','gantrypsaminfo:view','GET','/ap/gantrypsaminfo/gantrypasminfo',NULL,16),(39,'获取门架PSAM卡信息','gantrypsaminfo:getpsam','GET','/api/gantrypsaminfo/gantrypsaminfo',NULL,16),(40,'编辑门架坏卡信息','gantrypsaminfo:edit','POST','/api/gantrypsaminfo/gantrypsaminfo/{psamno}',NULL,16),(41,'下载门架PSAM卡信息','gantrypsaminfo:download','GET','/api/gantrypsaminfo/download',NULL,16),(42,'编辑故障原因','checklanesoft:edit','POST','/api/checklanesoft/checklanesoft/:id',NULL,12),(43,'新增编辑设备','devices:manage','POST','/device/form/:mode(add|edit)/:id?',NULL,7),(44,'ping结果列表','pingdevices:view','GET','/api/pingdevices/list',NULL,17),(45,'批量ping','devices:batch-ping','POST','/api/pingdevices/ping/batch',NULL,17);
/*!40000 ALTER TABLE `sys_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `sys_role`
--

LOCK TABLES `sys_role` WRITE;
/*!40000 ALTER TABLE `sys_role` DISABLE KEYS */;
INSERT INTO `sys_role` (`id`, `name`, `code`, `create_time`, `update_time`, `remark`) VALUES (1,'超级用户','super_admin','2025-11-08','2025-11-08 06:05:51.236398',NULL),(2,'普通管理员','ordinary_admin','2025-11-08','2025-11-08 06:06:16.257597',NULL),(3,'普通用户','domestic-consumer','2025-11-14','2025-11-14 02:00:48.200865',NULL);
/*!40000 ALTER TABLE `sys_role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `sys_role_menu`
--

LOCK TABLES `sys_role_menu` WRITE;
/*!40000 ALTER TABLE `sys_role_menu` DISABLE KEYS */;
INSERT INTO `sys_role_menu` (`id`, `menu_id`, `role_id`) VALUES (49,1,2),(50,2,2),(51,3,2),(52,4,2),(53,6,2),(54,7,2),(286,1,3),(287,6,3),(288,7,3),(289,8,3),(290,12,3),(291,13,3),(292,14,3),(293,15,3),(294,16,3),(336,1,1),(337,2,1),(338,3,1),(339,4,1),(340,5,1),(341,6,1),(342,7,1),(343,8,1),(344,12,1),(345,13,1),(346,14,1),(347,15,1),(348,16,1),(349,17,1);
/*!40000 ALTER TABLE `sys_role_menu` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `sys_role_permission`
--

LOCK TABLES `sys_role_permission` WRITE;
/*!40000 ALTER TABLE `sys_role_permission` DISABLE KEYS */;
INSERT INTO `sys_role_permission` (`id`, `permission_id`, `role_id`) VALUES (24,1,2),(25,1,1),(26,2,1),(27,3,1),(28,4,1),(29,5,1),(30,6,1),(31,7,1),(32,8,1),(33,9,1),(34,10,1),(35,11,1),(36,12,1),(37,13,1),(38,14,1),(39,15,1),(40,16,1),(41,17,1),(42,18,1),(43,19,1),(44,20,2),(45,20,1),(46,21,1),(47,22,1),(48,23,1),(49,24,1),(50,25,1),(51,12,2),(52,6,2),(53,16,2),(54,20,3),(55,26,1),(56,27,1),(58,30,1),(59,31,1),(60,32,1),(61,33,1),(62,34,1),(63,35,1),(64,36,1),(65,37,1),(66,40,1),(67,41,1),(68,38,1),(69,39,1),(70,32,3),(71,33,3),(72,34,3),(73,35,3),(74,38,3),(75,39,3),(76,30,3),(77,31,3),(79,42,1),(80,43,1),(81,44,1),(82,45,1);
/*!40000 ALTER TABLE `sys_role_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `sys_user`
--

LOCK TABLES `sys_user` WRITE;
/*!40000 ALTER TABLE `sys_user` DISABLE KEYS */;
INSERT INTO `sys_user` (`password`, `last_login`, `is_superuser`, `id`, `username`, `realname`, `email`, `telephone`, `is_active`, `status`, `avatar`, `create_time`, `update_time`, `latest_token`) VALUES ('pbkdf2_sha256$720000$ptB9H4fMAX9hAKtf1oFbyc$BEirY61vUPZa54sR4DqhNIKx86mVVZ63DQIAk6bZNmI=','2025-12-06 13:20:54.258577',0,1,'admin','超级管理员','admin@example.com','',1,1,'111.jpg','2025-11-08','2025-12-06 13:20:54.266520','eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyaWQiOjEsImV4cCI6MTc2NTAyNzI1NH0.q4csexRgwIY4oMS_IRfRINyoHPjYlPuMhXJXk0A2M24'),('pbkdf2_sha256$720000$7VBKfiTdqzrgzyvN2DATPG$H43TUSAbnqK60WgOcQnv7ZNNF/eh6ueXLLAiZFOE970=','2025-11-27 05:29:32.338498',0,2,'www','www','www@123.com','13345676567',1,1,'111.jpg','2025-11-13','2025-11-27 05:29:32.344483','eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyaWQiOjIsImV4cCI6MTc2NDI1MDE3Mn0.OAfBd50bvUCFE-xXJ0kcZrbqNcqcZ22UEwYI3TvEbVM'),('pbkdf2_sha256$720000$ogdlIfqOuYatcPp6txcrBz$QhT9soQNe+EfRfBVKbRDiAvIstflmELGTazVEmxI2QY=','2025-11-23 08:00:38.631465',0,3,'wxh','weixiaoheng','wei@123.com','13345654456',1,1,'111.jpg','2025-11-14','2025-11-23 08:00:38.638447','eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyaWQiOjMsImV4cCI6MTc2MzkxMzYzOH0.XAC32e1wA6_uOivt4pfgSKQWHo9HJYHFfySjTOOZ47E'),('pbkdf2_sha256$720000$nlxbVn4A2DNqnkeZ8N8x7R$xrVkzD0nGldu4bx8VRHQ1BxfkctEw5oIW9SYfLiifQo=',NULL,0,4,'111','111','111@123.com','13322222222',1,1,'111.jpg','2025-11-16','2025-11-23 07:59:59.187390',NULL),('pbkdf2_sha256$720000$EmJHkrQpiJmP3vP0mpZhOy$sd6klxhHKXWGdksk5DbAwFJM3nN8o1AsqSe+PuGIJIg=',NULL,0,5,'aaa','aaa','aaa@163.com','13345676543',1,1,'111.jpg','2025-11-27','2025-11-27 02:30:23.422231',NULL);
/*!40000 ALTER TABLE `sys_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `sys_user_role`
--

LOCK TABLES `sys_user_role` WRITE;
/*!40000 ALTER TABLE `sys_user_role` DISABLE KEYS */;
INSERT INTO `sys_user_role` (`id`, `role_id`, `user_id`) VALUES (1,1,1),(4,3,3),(5,3,4),(6,3,2),(7,3,5);
/*!40000 ALTER TABLE `sys_user_role` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-07  9:32:00
