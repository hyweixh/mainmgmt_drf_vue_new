// mysqlConfig.js
export const mysqlConfig = `
[mysqld]
datadir                        = /data/mysql                          # mysql路径
socket                         = /var/lib/mysql/mysql.sock            # 默认sock，不要改
log-error                      = /logs/mysqld.log                     # mysql日志路径
pid-file                       = /var/run/mysqld/mysqld.pid            # mysql进程
log-bin                        = mysql-bin                            # 二进制日志
binlog_format                  = ROW                                   # Row模式
server-id                      = 1                                     # Mysql唯一标识，用于主从同步
slow_query_log                 = on                                    # 开启慢查询日志
long_query_time                = 3                                     # 记录超过3秒的SQL
slow_query_log_file            = /logs/slow.log                        # 慢日志日志
log-output                     = TABLE                                 # 日志输出到表格
innodb_print_all_deadlocks     = ON                                    # 输出死锁信息
`;
