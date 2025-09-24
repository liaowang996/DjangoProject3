import uuid
from common.sql_utils import SqlUtils
from common.config import CONFIG
from common.log_utils import logger


class ExcelToMysqlImporter:
    def __init__(self):
        self.sql_utils = SqlUtils()
        self.target_db = "api_test"
        self.field_mapping = {
            "测试用例编号": [("case_info", "case_id"), ("case_step_info", "case_id")],
            "模块名称": [("case_step_info", "part_name")],
            "测试用例名称": [("case_info", "case_name")],
            "用例执行": [("case_info", "is_run")],
            "测试用例步骤": [("case_step_info", "case_step_name")],
            "接口名称": [("api_info", "api_name")],
            "请求方式": [("api_info", "api_request_type")],
            "请求地址": [("api_info", "api_request_url")],
            "请求参数(get)": [("api_info", "api_url_params")],
            "提交数据(post)": [("api_info", "api_post_data")],
            "取值方式": [("case_step_info", "get_value_type")],
            "传值变量": [("case_step_info", "variable_name")],
            "取值代码": [("case_step_info", "get_value_code")],
            "期望结果类型": [("case_step_info", "excepted_result_type")],
            "期望结果": [("case_step_info", "excepted_result")],
            "是否通过": [("case_step_info", "is_pass")]
        }
        logger.info("ExcelToMysqlImporter初始化完成，目标数据库：%s", self.target_db)

    def _generate_short_uuid(self, length=10):
        return str(uuid.uuid4()).replace("-", "")[:length]

    def _convert_is_run(self, is_run_str):
        if str(is_run_str).strip().lower() in ("是", "1", "yes", "true"):
            return "是"
        else:
            return "否"

    def _get_api_id_by_name(self, api_name):
        sql = """SELECT api_id FROM api_info WHERE api_name = %s LIMIT 1"""
        result = self.sql_utils.execute_query(sql, (api_name,))
        return result[0]["api_id"] if result else None

    def _get_case_info_id(self, case_id, case_name):
        sql = """SELECT CaseInfo_id FROM case_info WHERE case_id = %s AND case_name = %s LIMIT 1"""
        result = self.sql_utils.execute_query(sql, (case_id, case_name))
        return result[0]["CaseInfo_id"] if result else None

    def _get_case_step_id(self, case_id, part_name):
        sql = """SELECT CaseStepInfo_id FROM case_step_info WHERE case_id = %s AND part_name = %s LIMIT 1"""
        result = self.sql_utils.execute_query(sql, (case_id, part_name))
        return result[0]["CaseStepInfo_id"] if result else None

    def _handle_api_info(self, excel_row):
        api_name = excel_row.get("接口名称", "").strip()
        if not api_name:
            logger.warning("接口名称为空，跳过api_info处理")
            return None

        api_request_type = excel_row.get("请求方式", "").strip().upper()
        api_request_url = excel_row.get("请求地址", "").strip()
        api_url_params = excel_row.get("请求参数(get)", "").strip() or "{}"
        api_post_data = excel_row.get("提交数据(post)", "").strip() or "{}"

        exist_api_id = self._get_api_id_by_name(api_name)
        if exist_api_id:
            update_sql = """
                UPDATE api_info 
                SET api_request_type = %s, 
                    api_request_url = %s, 
                    api_url_params = %s, 
                    api_post_data = %s 
                WHERE api_name = %s
            """
            self.sql_utils.execute_update(
                update_sql,
                (api_request_type, api_request_url, api_url_params, api_post_data, api_name)
            )
            logger.debug("【更新api_info】api_name=%s，api_id=%s", api_name, exist_api_id)
            return exist_api_id
        else:
            new_api_id = self._generate_short_uuid(length=10)
            insert_sql = """
                INSERT INTO api_info (
                    api_id, api_name, api_request_type, 
                    api_request_url, api_url_params, api_post_data
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """
            self.sql_utils.execute_update(
                insert_sql,
                (new_api_id, api_name, api_request_type, api_request_url, api_url_params, api_post_data)
            )
            logger.debug("【插入api_info】api_name=%s，新api_id=%s", api_name, new_api_id)
            return new_api_id

    def _handle_case_info(self, excel_row):
        case_id = excel_row.get("测试用例编号", "").strip()
        case_name = excel_row.get("测试用例名称", "").strip()
        if not (case_id and case_name):
            logger.warning(f"用例编号/名称为空（case_id={case_id}），跳过case_info处理")
            return None

        is_run = self._convert_is_run(excel_row.get("用例执行", "是"))

        exist_case_id = self._get_case_info_id(case_id, case_name)
        if exist_case_id:
            update_sql = """
                UPDATE case_info 
                SET is_run = %s 
                WHERE case_id = %s AND case_name = %s
            """
            self.sql_utils.execute_update(update_sql, (is_run, case_id, case_name))
            logger.debug("【更新case_info】case_id=%s，case_name=%s，is_run=%s", case_id, case_name, is_run)
            return exist_case_id
        else:
            new_case_id = self._generate_short_uuid(length=10)
            insert_sql = """
                INSERT INTO case_info (CaseInfo_id, case_id, case_name, is_run)
                VALUES (%s, %s, %s, %s)
            """
            self.sql_utils.execute_update(insert_sql, (new_case_id, case_id, case_name, is_run))
            logger.debug("【插入case_info】case_id=%s，case_name=%s，新CaseInfo_id=%s", case_id, case_name, new_case_id)
            return new_case_id

    def _handle_case_step_info(self, excel_row, case_info_id, api_id):
        case_id = excel_row.get("测试用例编号", "").strip()
        part_name = excel_row.get("模块名称", "").strip() or "未分类"
        case_step_name = excel_row.get("测试用例步骤", "").strip() or "默认步骤"
        get_value_type = excel_row.get("取值方式", "").strip() or "无"
        variable_name = excel_row.get("传值变量", "").strip()
        get_value_code = excel_row.get("取值代码", "").strip()
        excepted_result_type = excel_row.get("期望结果类型", "").strip() or "无"
        excepted_result = excel_row.get("期望结果", "").strip()
        is_pass = excel_row.get("是否通过", "").strip() or "未执行"

        if not (case_id and case_info_id and api_id):
            logger.warning(f"必要参数缺失（case_id={case_id}，case_info_id={case_info_id}），跳过case_step_info处理")
            return

        exist_step_id = self._get_case_step_id(case_id, part_name)
        if exist_step_id:
            update_sql = """
                UPDATE case_step_info 
                SET case_step_name = %s, 
                    get_value_type = %s, 
                    variable_name = %s, 
                    get_value_code = %s, 
                    excepted_result_type = %s, 
                    excepted_result = %s, 
                    is_pass = %s,
                    api_id = %s 
                WHERE CaseStepInfo_id = %s
            """
            self.sql_utils.execute_update(
                update_sql,
                (case_step_name, get_value_type, variable_name, get_value_code,
                 excepted_result_type, excepted_result, is_pass, api_id, exist_step_id)
            )
            logger.debug("【更新case_step_info】case_id=%s，part_name=%s，step_id=%s", case_id, part_name, exist_step_id)
        else:
            insert_sql = """
                INSERT INTO case_step_info (
                    CaseStepInfo_id, case_id, case_step_name, part_name, api_id,
                    get_value_type, variable_name, excepted_result_type,
                    excepted_result, get_value_code, is_pass
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.sql_utils.execute_update(
                insert_sql,
                (case_info_id, case_id, case_step_name, part_name, api_id,
                 get_value_type, variable_name, excepted_result_type,
                 excepted_result, get_value_code, is_pass)
            )
            logger.debug("【插入case_step_info】case_id=%s，part_name=%s，step_id=%s（复用case_info.CaseInfo_id）",
                         case_id, part_name, case_info_id)

    def import_case_info(self, case_info_list):
        result = {"total": len(case_info_list), "success": 0, "fail": 0, "fail_details": []}
        logger.info("开始导入case_info数据，总条数：%d", result["total"])

        for idx, case_item in enumerate(case_info_list, 1):
            try:
                case_id = case_item.get("case_id", f"unknown_{idx}")
                case_info_rows = case_item.get("case_info", [])
                if not case_info_rows:
                    err_msg = f"第{idx}条无case_info数据"
                    logger.warning(err_msg)
                    result["fail"] += 1
                    result["fail_details"].append(err_msg)
                    continue

                for excel_row in case_info_rows:
                    with self.sql_utils.transaction():
                        api_id = self._handle_api_info(excel_row)
                        if not api_id:
                            raise Exception("api_info处理失败，未获取到api_id")

                        case_info_id = self._handle_case_info(excel_row)
                        if not case_info_id:
                            raise Exception("case_info处理失败，未获取到case_info.CaseInfo_id")

                        self._handle_case_step_info(excel_row, case_info_id, api_id)

                result["success"] += 1
                logger.info("第%d条数据导入成功：case_id=%s", idx, case_id)
            except Exception as e:
                err_msg = f"第{idx}条数据导入失败：{str(e)}"
                logger.error(err_msg, exc_info=True)
                result["fail"] += 1
                result["fail_details"].append(err_msg)

        logger.info("=" * 50)
        logger.info("case_info数据导入完成：")
        logger.info(f"总条数：{result['total']} | 成功：{result['success']} | 失败：{result['fail']}")
        if result["fail_details"]:
            logger.info("失败详情：")
            for detail in result["fail_details"]:
                logger.info(f"  - {detail}")
        logger.info("=" * 50)
        return result

    def close(self):
        self.sql_utils.close()
        logger.info("ExcelToMysqlImporter资源已释放")


# 测试代码
if __name__ == "__main__":
    case_info_name = [
        {'case_id': 'part_1_case_01', 'case_info': [
            {'测试用例编号': 'case_01', '模块名称': 'part_1', '测试用例名称': '注册接口_part_1', '用例执行': '是',
             '测试用例步骤': 'step_01', '接口名称': '注册接口_part_1', '请求方式': 'POST', '请求地址': '/api/register',
             '请求参数(get)': '', '提交数据(post)': '{"email": "sydney@fife","password": "pistol"}',
             '取值方式': '正则匹配', '传值变量': 'total_pages', '取值代码': '"total_pages":(.+?)',
             '期望结果类型': 'json键是否存在', '期望结果': 'error', '是否通过': '通过', '来源文件': 'test_demo.xls'}]},
        {'case_id': 'part_1_case_02', 'case_info': [
            {'测试用例编号': 'case_02', '模块名称': 'part_1', '测试用例名称': '登录失败接口1_part_1', '用例执行': '是',
             '测试用例步骤': 'step_01', '接口名称': '登录失败接口1_part_1', '请求方式': 'POST',
             '请求地址': '/api/login', '请求参数(get)': '', '提交数据(post)': '{"email": "123123"}', '取值方式': '无',
             '传值变量': '', '取值代码': '', '期望结果类型': 'json键是否存在', '期望结果': 'error', '是否通过': '通过',
             '来源文件': 'test_demo.xls'}]},
        {'case_id': 'part_1_case_03', 'case_info': [
            {'测试用例编号': 'case_03', '模块名称': 'part_1', '测试用例名称': '登录失败接口2_part_1', '用例执行': '是',
             '测试用例步骤': 'step_01', '接口名称': '登录失败接口2_part_1', '请求方式': 'POST',
             '请求地址': '/api/login', '请求参数(get)': '', '提交数据(post)': '{"email": "12323"}', '取值方式': '无',
             '传值变量': '', '取值代码': '', '期望结果类型': 'json键是否存在', '期望结果': 'error', '是否通过': '通过',
             '来源文件': 'test_demo.xls'}]},
        {'case_id': 'part_2_case_01', 'case_info': [
            {'测试用例编号': 'case_01', '模块名称': 'part_2', '测试用例名称': '注册接口part_2', '用例执行': '是',
             '测试用例步骤': 'step_01', '接口名称': '注册接口part_2', '请求方式': 'POST', '请求地址': '/api/register',
             '请求参数(get)': '', '提交数据(post)': '{"email": "sydney@fife","password": "pistol"}',
             '取值方式': '正则匹配', '传值变量': 'total_pages', '取值代码': '"total_pages":(.+?)',
             '期望结果类型': 'json键是否存在', '期望结果': 'total_pages', '是否通过': '通过',
             '来源文件': 'test_demo2.xls'}]},
        {'case_id': 'part_2_case_02', 'case_info': [
            {'测试用例编号': 'case_02', '模块名称': 'part_2', '测试用例名称': '登录失败接口1_part_2', '用例执行': '是',
             '测试用例步骤': 'step_01', '接口名称': '登录失败接口1_part_2', '请求方式': 'POST',
             '请求地址': '/api/login', '请求参数(get)': '', '提交数据(post)': '{"email": "123123"}', '取值方式': '无',
             '传值变量': '', '取值代码': '', '期望结果类型': 'json键是否存在', '期望结果': 'total_pages',
             '是否通过': '通过', '来源文件': 'test_demo2.xls'}]},
        {'case_id': 'part_2_case_03', 'case_info': [
            {'测试用例编号': 'case_03', '模块名称': 'part_2', '测试用例名称': '登录失败接口2_part_2', '用例执行': '是',
             '测试用例步骤': 'step_01', '接口名称': '登录失败接口2_part_2', '请求方式': 'POST',
             '请求地址': '/api/login', '请求参数(get)': '', '提交数据(post)': '{"email": "12323"}', '取值方式': '无',
             '传值变量': '', '取值代码': '', '期望结果类型': 'json键是否存在', '期望结果': 'total_pages',
             '是否通过': '通过', '来源文件': 'test_demo2.xls'}]}
    ]

    try:
        importer = ExcelToMysqlImporter()
        import_result = importer.import_case_info(case_info_name)
        print("\n" + "=" * 50)
        print("导入结果汇总：")
        print(f"总数据条数：{import_result['total']}")
        print(f"成功条数：{import_result['success']}")
        print(f"失败条数：{import_result['fail']}")
        if import_result['fail_details']:
            print("\n失败详情：")
            for detail in import_result['fail_details']:
                print(f"  - {detail}")
        print("=" * 50)
    except Exception as e:
        logger.critical("导入工具初始化失败：%s", str(e), exc_info=True)
    finally:
        if 'importer' in locals():
            importer.close()