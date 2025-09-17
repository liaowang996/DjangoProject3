import pymysql
from contextlib import contextmanager
from common import config
from common.log_utils import logger


class SqlUtils():
    def __init__(self):
        """初始化数据库连接配置"""
        self._validate_config()
        self.connection_params = {
            'host': config.MYSQL_DB_HOST,
            'port': int(config.MYSQL_DB_PORT),
            'user': config.MYSQL_DB_USER,
            'password': config.MYSQL_DB_PASSWORD,
            'db': config.MYSQL_DB_DATABASE,
            'charset': config.MYSQL_DB_CHARSET or 'utf8mb4'  # 提供默认字符集
        }
        self.connect = None
        self.cursor = None

    def _validate_config(self):
        """验证数据库配置是否完整"""
        required_configs = [
            'MYSQL_DB_HOST', 'MYSQL_DB_PORT',
            'MYSQL_DB_USER', 'MYSQL_DB_PASSWORD',
            'MYSQL_DB_DATABASE'
        ]

        for config_name in required_configs:
            if not hasattr(config, config_name) or not getattr(config, config_name):
                error_msg = f"数据库配置缺失: {config_name} 未在config中定义或值为空"
                logger.error(error_msg)
                raise AttributeError(error_msg)

    def _get_connection(self):
        """获取数据库连接（如果连接不存在或已关闭则重新创建）"""
        try:
            if not self.connect or self.connect._closed:
                logger.info(f"连接数据库: {self.connection_params['host']}:{self.connection_params['port']}")
                self.connect = pymysql.connect(**self.connection_params)
                self.cursor = self.connect.cursor(cursor=pymysql.cursors.DictCursor)
                logger.debug("数据库连接成功")
            return self.connect, self.cursor
        except pymysql.MySQLError as e:
            logger.error(f"数据库连接失败: {str(e)}", exc_info=True)
            raise

    def close(self):
        """关闭数据库连接"""
        try:
            if self.cursor:
                self.cursor.close()
                logger.debug("数据库游标已关闭")
            if self.connect and not self.connect._closed:
                self.connect.close()
                logger.debug("数据库连接已关闭")
        except pymysql.MySQLError as e:
            logger.warning(f"关闭数据库连接时出错: {str(e)}")

    @contextmanager
    def transaction(self):
        """事务上下文管理器，自动处理提交和回滚"""
        conn, _ = self._get_connection()
        try:
            yield
            conn.commit()
            logger.debug("事务已提交")
        except Exception as e:
            conn.rollback()
            logger.error(f"事务执行失败，已回滚: {str(e)}")
            raise
        finally:
            self.close()

    def execute_query(self, sql, params=None):
        """
        执行查询语句
        :param sql: SQL查询语句
        :param params: SQL参数，用于参数化查询
        :return: 查询结果列表
        """
        try:
            _, cursor = self._get_connection()
            # logger.debug(f"执行SQL查询: {sql} 参数: {params}")

            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            result = cursor.fetchall()
            logger.debug(f"查询返回 {len(result)} 条记录")
            return result
        except pymysql.MySQLError as e:
            logger.error(f"SQL查询执行失败: {str(e)}", exc_info=True)
            raise
        finally:
            self.close()

    def execute_update(self, sql, params=None):
        """
        执行更新语句（INSERT/UPDATE/DELETE）
        :param sql: SQL语句
        :param params: SQL参数，用于参数化查询
        :return: 受影响的行数
        """
        try:
            with self.transaction():
                _, cursor = self._get_connection()
                logger.debug(f"执行SQL更新: {sql} 参数: {params}")

                if params:
                    affected_rows = cursor.execute(sql, params)
                else:
                    affected_rows = cursor.execute(sql)

                logger.debug(f"SQL更新影响 {affected_rows} 行")
                return affected_rows
        except pymysql.MySQLError as e:
            logger.error(f"SQL更新执行失败: {str(e)}", exc_info=True)
            raise

    def get_mysql_test_case_info(self):
        """获取MySQL中的测试用例信息"""
        sql_str = '''
        SELECT
        	b.case_id AS '测试用例编号',
        	b.case_name AS '测试用例名称',
        	b.is_run AS '用例执行',
        	a.case_step_name AS '测试用例步骤',
        	c.api_name AS '接口名称',
        	c.api_request_type AS '请求方式',
        	c.api_request_url AS '请求地址',
        	c.api_url_params AS '请求参数(get)',
        	c.api_post_data AS '提交数据(post)',
        	a.get_value_type AS '取值方式',
        	a.variable_name AS '传值变量',
        	a.get_value_code AS '取值代码',
        	a.excepted_result_type AS '期望结果类型',
        	a.excepted_result AS '期望结果'
        FROM
        	case_step_info a
        	LEFT JOIN case_info b ON a.case_id = b.case_id
        	LEFT JOIN api_info c ON a.api_id = c.api_id
        WHERE
        	b.is_run = '是'
        ORDER BY
        	b.case_id,
        	a.case_step_name;
        '''
        return self.execute_query(sql_str)


if __name__ == '__main__':
    try:
        sql_utils = SqlUtils()
        test_cases = sql_utils.get_mysql_test_case_info()
        logger.info(f"从数据库获取到 {len(test_cases)} 条测试用例")

        for case in test_cases:
            logger.info(f"测试用例编号: {case['测试用例编号']} 测试用例名称: {case['测试用例名称']}")
    except Exception as e:
        logger.error(f"测试用例获取失败: {str(e)}")
