import pymysql
from contextlib import contextmanager
from common import config
from common.log_utils import logger


class SqlUtils():
    def __init__(self):
        self._validate_config()
        self.connection_params = {
            'host': config.MYSQL_DB_HOST,
            'port': int(config.MYSQL_DB_PORT),
            'user': config.MYSQL_DB_USER,
            'password': config.MYSQL_DB_PASSWORD,
            'db': config.MYSQL_DB_DATABASE,
            'charset': config.MYSQL_DB_CHARSET or 'utf8mb4'
        }
        self.connect = None
        self.cursor = None

    def _validate_config(self):
        required_configs = [
            'MYSQL_DB_HOST', 'MYSQL_DB_PORT',
            'MYSQL_DB_USER', 'MYSQL_DB_PASSWORD',
            'MYSQL_DB_DATABASE'
        ]
        for config_name in required_configs:
            if not hasattr(config, config_name) or not getattr(config, config_name):
                error_msg = f"数据库配置缺失: {config_name}"
                logger.error(error_msg)
                raise AttributeError(error_msg)

    def _get_connection(self):
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
        """修复游标关闭逻辑：移除closed属性判断，直接尝试关闭"""
        try:
            # 游标关闭：直接调用close()，无需判断closed属性（不存在该属性）
            if self.cursor:
                self.cursor.close()
                logger.debug("数据库游标已关闭")
            # 连接关闭：判断连接是否已关闭
            if self.connect and not self.connect._closed:
                self.connect.close()
                logger.debug("数据库连接已关闭")
        except pymysql.MySQLError as e:
            logger.warning(f"关闭数据库连接时出错: {str(e)}")
        except Exception as e:
            # 捕获其他异常（如游标已关闭时重复调用close()）
            logger.warning(f"关闭数据库资源时出现非预期错误: {str(e)}")

    @contextmanager
    def transaction(self):
        conn, _ = self._get_connection()
        try:
            yield
            conn.commit()
            logger.debug("事务已提交")
        except Exception as e:
            conn.rollback()
            logger.error(f"事务执行失败，已回滚: {str(e)}")
            raise

    def execute_query(self, sql, params=None):
        try:
            _, cursor = self._get_connection()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            result = cursor.fetchall()
            logger.debug(f"查询返回 {len(result)} 条记录")
            if not self.connect or self.connect._closed:
                self.close()
            return result
        except pymysql.MySQLError as e:
            logger.error(f"SQL查询执行失败: {str(e)}", exc_info=True)
            self.close()
            raise

    def execute_update(self, sql, params=None):
        try:
            with self.transaction():
                _, cursor = self._get_connection()
                logger.debug(f"执行SQL更新: {sql} 参数: {params}")
                affected_rows = cursor.execute(sql, params) if params else cursor.execute(sql)
                logger.debug(f"SQL更新影响 {affected_rows} 行")
            return affected_rows
        except pymysql.MySQLError as e:
            logger.error(f"SQL更新执行失败: {str(e)}", exc_info=True)
            raise
    def execute_update(self, sql, params=None):
        """执行更新（INSERT/UPDATE/DELETE，仅在事务内调用）"""
        try:
            with self.transaction():  # 依赖事务上下文管理连接
                _, cursor = self._get_connection()
                logger.debug(f"执行SQL更新: {sql} 参数: {params}")
                affected_rows = cursor.execute(sql, params) if params else cursor.execute(sql)
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
        	a.part_name AS '模块名称',
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
        	a.excepted_result AS '期望结果',
        	a.is_pass   AS '是否通过'
        FROM
        	case_step_info a
        	LEFT JOIN case_info b ON a.id = b.id
        	LEFT JOIN api_info c ON a.api_id = c.api_id
        WHERE
        	b.is_run = '是'
        ORDER BY
					a.part_name,
        	b.case_id,
        	a.case_step_name;
        '''
        return self.execute_query(sql_str)


if __name__ == '__main__':
    try:
        sql_utils = SqlUtils()
        test_cases = sql_utils.get_mysql_test_case_info()
        print(test_cases)
        logger.info(f"从数据库获取到 {len(test_cases)} 条测试用例")

        for case in test_cases:
            logger.info(f"测试用例编号: {case['测试用例编号']} 测试用例名称: {case['测试用例名称']}")
    except Exception as e:
        logger.error(f"测试用例获取失败: {str(e)}")