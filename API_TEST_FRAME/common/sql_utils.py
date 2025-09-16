import pymysql


from common import config


class SqlUtils():

    def __init__(self):
        self.connect = pymysql.connect(
            host=config.MYSQL_DB_HOST,
            port=int(config.MYSQL_DB_PORT),
            user=config.MYSQL_DB_USER,
            password=config.MYSQL_DB_PASSWORD,
            db=config.MYSQL_DB_DATABASE,
            charset=config.MYSQL_DB_CHARSET
        )
        self.cursor = self.connect.cursor(cursor=pymysql.cursors.DictCursor)

    def get_mysql_test_case_info(self):
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
        self.cursor.execute(sql_str)
        return self.cursor.fetchall()

if __name__ == '__main__':
    sql_utils = SqlUtils()
    for s in sql_utils.get_mysql_test_case_info():
        print(s)