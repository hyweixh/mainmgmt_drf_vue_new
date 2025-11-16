token
89b7c7af8a262018198d9d58c26043da7154ecbdb0d0d14c6a0363d8c4f9db1d

密钥
SECb58d1dc7e5c9aab94063584af51910e46e7ce4a2acc7b4ec20455b6db5e885fa


初始化管理员
```sql
INSERT INTO `OpsAdmin`.`opsauth_opsuser` (`password`, `last_login`, `is_superuser`, `uid`, `username`, `realname`, `email`, `telephone`, `is_active`, `status`, `date_joined`) VALUES ('pbkdf2_sha256$720000$4yQw602HHcGFTDjU4Soiz5$N/fmOrkzvl6MqkNoOSdb3Mxywe/lM7JzzSahl2LRwvo=', '2024-08-08 10:31:50.847792', 1, 'BWq9dYxGtid6MbHZ6aMNNj', 'chenzhuo', '陈卓', '844709972@qq.com', '', 1, 1, '2024-08-08 10:31:50.848099');
```
告警方式
```sql
INSERT INTO `OpsAdmin`.`alarm_alertmethod` (`id`, `method`) VALUES (1, '钉钉');
INSERT INTO `OpsAdmin`.`alarm_alertmethod` (`id`, `method`) VALUES (2, '邮件');
INSERT INTO `OpsAdmin`.`alarm_alertmethod` (`id`, `method`) VALUES (3, '飞书');
INSERT INTO `OpsAdmin`.`alarm_alertmethod` (`id`, `method`) VALUES (4, '企业微信');
```