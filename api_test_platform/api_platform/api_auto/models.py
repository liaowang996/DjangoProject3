from django.db import models

class ApiInfo(models.Model):
    """接口信息表（对应api_info）"""
    api_id = models.CharField(max_length=100, primary_key=True, verbose_name="接口ID")
    api_name = models.CharField(max_length=100, verbose_name="接口名称")
    api_request_type = models.CharField(max_length=10, verbose_name="请求方式")
    api_request_url = models.CharField(max_length=300, verbose_name="请求地址")
    api_url_params = models.TextField(verbose_name="请求参数(get)")
    api_post_data = models.TextField(verbose_name="提交数据(post)")

    class Meta:
        db_table = 'api_info'  # 关联现有表
        verbose_name = "接口信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.api_name


class CaseInfo(models.Model):
    """用例信息表（对应case_info）"""
    case_info_id = models.CharField(max_length=10, primary_key=True, db_column='CaseInfo_id', verbose_name="用例信息ID")
    case_id = models.CharField(max_length=10, verbose_name="测试用例编号")
    case_name = models.CharField(max_length=100, verbose_name="测试用例名称")
    is_run = models.CharField(max_length=4, default="是", verbose_name="用例执行")

    class Meta:
        db_table = 'case_info'  # 关联现有表
        verbose_name = "用例信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.case_id}-{self.case_name}"


class CaseStepInfo(models.Model):
    """用例步骤表（对应case_step_info）"""
    case_step_info_id = models.CharField(max_length=10, primary_key=True, db_column='CaseStepInfo_id', verbose_name="步骤ID")
    case_id = models.CharField(max_length=10, verbose_name="测试用例编号")
    case_step_name = models.CharField(max_length=20, verbose_name="测试用例步骤")
    part_name = models.CharField(max_length=255, verbose_name="模块名称")
    api = models.ForeignKey(ApiInfo, on_delete=models.CASCADE, db_column='api_id', verbose_name="关联接口")
    get_value_type = models.CharField(max_length=20, verbose_name="取值方式")
    variable_name = models.CharField(max_length=20, verbose_name="传值变量")
    excepted_result_type = models.CharField(max_length=20, verbose_name="期望结果类型")
    excepted_result = models.TextField(verbose_name="期望结果")
    is_pass = models.CharField(max_length=255, null=True, blank=True, verbose_name="是否通过")
    get_value_code = models.TextField(null=True, blank=True, verbose_name="取值代码")

    class Meta:
        db_table = 'case_step_info'  # 关联现有表
        verbose_name = "用例步骤"
        verbose_name_plural = verbose_name
        ordering = ['part_name', 'case_id', 'case_step_name']  # 排序规则

    def __str__(self):
        return f"{self.part_name}-{self.case_id}-{self.case_step_name}"


class ConfigUrl(models.Model):
    """环境配置表"""
    url_chin_name = models.CharField(max_length=100, verbose_name="接口中文名称")
    section = models.CharField(max_length=100, verbose_name="配置节")
    key_name = models.CharField(max_length=100, verbose_name="键名")
    urls_addr = models.CharField(max_length=100, verbose_name="接口地址")
    note = models.CharField(max_length=100, verbose_name="备注", blank=True, null=True)

    class Meta:
        db_table = 'config_urls'
        verbose_name = "环境配置"
        verbose_name_plural = verbose_name
        unique_together = ('section', 'key_name')  # 确保section和key_name组合唯一

    def __str__(self):
        return f"{self.url_chin_name} ({self.urls_addr})"