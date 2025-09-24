class TestResultCollector:
    """测试结果收集器，用于收集和格式化测试结果数据"""

    def __init__(self):
        self.results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "start_time": None,
            "end_time": None,
            "duration": 0,
            "test_cases": [],
            "failed_cases": [],
            "environment": {
                "api_url": "",
                "test_env": "",
                "tool_version": ""
            },
            "module_stats": {}  # 按模块统计结果
        }

    def add_test_case(self, case_info, result, duration=0, error_msg=""):
        """添加测试用例结果"""
        self.results["total"] += 1

        # 更新状态统计
        if result == "passed":
            self.results["passed"] += 1
        elif result == "failed":
            self.results["failed"] += 1
        elif result == "skipped":
            self.results["skipped"] += 1

        # 更新模块统计
        module_name = case_info.get("模块名称", "未知模块")
        if module_name not in self.results["module_stats"]:
            self.results["module_stats"][module_name] = {"passed": 0, "failed": 0, "skipped": 0}
        self.results["module_stats"][module_name][result] += 1

        # 记录详细用例信息
        test_case = {
            "case_id": case_info.get("测试用例编号", ""),
            "case_name": case_info.get("测试用例名称", ""),
            "module": module_name,
            "api_name": case_info[0].get("接口名称", ""),
            "method": case_info[0].get("请求方式", ""),
            "result": result,
            "duration": duration,
            "error_msg": error_msg
        }

        self.results["test_cases"].append(test_case)

        # 如果是失败用例，单独记录
        if result == "failed":
            self.results["failed_cases"].append(test_case)

    def set_environment(self, api_url, test_env, tool_version):
        """设置测试环境信息"""
        self.results["environment"] = {
            "api_url": api_url,
            "test_env": test_env,
            "tool_version": tool_version
        }

    def set_time_info(self, start_time, end_time, duration):
        """设置时间信息"""
        self.results["start_time"] = start_time
        self.results["end_time"] = end_time
        self.results["duration"] = duration

    def get_results(self):
        """获取整理后的结果数据"""
        return self.results
