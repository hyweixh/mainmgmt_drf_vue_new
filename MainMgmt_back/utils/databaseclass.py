import pyodbc
import firebirdsql


class Mssql_class(object):
    def __init__(self, db_ip, db_name, db_user, db_pw):
        self.db_ip = db_ip
        self.db_name = db_name
        self.db_user = db_user
        self.db_pw = db_pw
        self.conn = None
        self.cursor = None
        self.in_transaction = False  # 用于跟踪是否在事务中

    def connect(self):
        try:
            conn_str = (
                f'DRIVER=ODBC Driver 18 for SQL Server;'
                f'SERVER={self.db_ip};'
                f'DATABASE={self.db_name};'
                f'UID={self.db_user};'
                f'PWD={self.db_pw};'
                f'TrustServerCertificate=yes;'
            )
            self.conn = pyodbc.connect(conn_str)
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(f"连接数据库失败: {e}")
            raise

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            if self.in_transaction:  # 如果在事务中，则回滚
                self.rollback()
            self.conn.close()

    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params)  # 使用参数化查询
            if query.strip().upper().startswith("INSERT") or \
                    query.strip().upper().startswith("UPDATE") or \
                    query.strip().upper().startswith("DELETE"):
                self.in_transaction = True  # 标记为在事务中
            rows = self.cursor.fetchall()
            # print("rows:",rows)
            return rows
        except pyodbc.Error as e:
            print(f"查询数据库时发生错误: {e}")
            if self.in_transaction:  # 如果在事务中，则回滚
                self.rollback()
            return None

    # 定义执行SQL命令但不尝试获取结果集
    def execute_non_query(self, query, params=None):
        try:
            self.cursor.execute(query, params)  # 使用参数化查询执行非查询操作
            if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
                self.in_transaction = True  # 标记为在事务中

        except pyodbc.Error as e:
            print(f"执行非查询操作时发生错误: {e}")
            if self.in_transaction:  # 如果在事务中，则回滚
                self.rollback()
            raise

    def commit(self):
        try:
            self.conn.commit()
            self.in_transaction = False  # 重置事务状态
        except pyodbc.Error as e:
            print(f"提交事务时发生错误: {e}")
            self.rollback()  # 如果提交失败，则回滚
            raise

    def rollback(self):
        try:
            self.conn.rollback()
            self.in_transaction = False  # 重置事务状态
        except pyodbc.Error as e:
            print(f"回滚事务时发生错误: {e}")
            raise
class Firebird_class(object):
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = firebirdsql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
            )
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(f"连接Firebird数据库失败: {e}")
            raise

    def execute_query(self, sqlstr, params=None):
        try:
            if params:
                for k, v in params.items():
                    sqlstr = sqlstr.replace(f":{k}", str(v))
            self.cursor.execute(sqlstr)
            rows = self.cursor.fetchall()
            return rows
        except firebirdsql.Error as e:
            print(f"查询Firebird数据库时发生错误: {e}")
            return None

    def close_connection(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()




# if __name__ == "__main__":
#     # 创建MSSQL数据库连接实例并连接
#     mssql_instance = Mssql_class('your_mssql_server_ip', 'your_mssql_database', 'your_username', 'your_password')
#     mssql_instance.connect()
#
#     # 执行查询（注意：这里应该使用参数化查询来避免SQL注入）
#     query = "SELECT * FROM your_table WHERE column_name = ?"
#     params = ('your_value',)
#     results = mssql_instance.execute_query(query, params)
#     for row in results:
#         print(row)
#
#         # 断开连接
#     mssql_instance.disconnect()
#
#     # 创建Firebird数据库连接实例并连接
#     firebird_instance = Firebird_class('your_firebird_server_ip', 3050, 'your_username', 'your_password',
#                                        'your_database_alias_or_path')
#     firebird_instance.connect()
#
#     # 执行查询（注意：这里假设使用:param形式作为参数占位符）
#     # 请注意，上面的execute_query方法中的参数替换是不安全的，仅用于演示
#     # 在实际生产环境中，您应该寻找支持安全参数化查询的Firebird驱动
#     firebird_query = "SELECT * FROM your_table WHERE column_name = :value"
#     firebird_params = {'value': 'your_value'}
#     firebird_results = firebird_instance.execute_query(firebird_query, firebird_params)
#     for row in firebird_results:
#         print(row)
#
#         # 断开连接
#     firebird_instance.close_connection()