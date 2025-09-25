from django import forms
from .models import CaseInfo, CaseStepInfo, ApiInfo

class ExcelUploadForm(forms.Form):
    """Excel上传表单"""
    excel_file = forms.FileField(
        label='选择Excel文件',
        help_text='仅支持xls/xlsx格式文件',
        widget=forms.FileInput(attrs={'accept': '.xls,.xlsx'})
    )

class ApiManagementForm(forms.ModelForm):
    IS_RUN_CHOICES = [('是', '是'), ('否', '否')]
    EXPECTED_RESULT_TYPE_CHOICES = [
        ('无', '无'),
        ('json键是否存在', 'json键是否存在'),
        ('json键值对', 'json键值对'),
        ('正则匹配', '正则匹配')
    ]

    # 基础信息
    case_id = forms.CharField(label='测试用例编号', max_length=10)
    case_name = forms.CharField(label='测试用例名称', max_length=100)
    is_run = forms.ChoiceField(choices=IS_RUN_CHOICES, label='是否执行')
    part_name = forms.CharField(label='模块名称', max_length=255)
    case_step_name = forms.CharField(label='测试用例步骤', max_length=20)

    # 接口信息
    api_name = forms.CharField(label='接口名称', max_length=100)
    api_request_type = forms.CharField(label='请求方式', max_length=10)
    api_request_url = forms.CharField(label='请求地址', max_length=300)
    api_url_params = forms.CharField(
        label='请求参数(get)',
        required=False,
        widget=forms.Textarea(attrs={'rows': 3})
    )
    api_post_data = forms.CharField(
        label='提交数据(post)',
        required=False,
        widget=forms.Textarea(attrs={'rows': 3})
    )

    # 测试步骤信息
    get_value_type = forms.CharField(label='取值方式', max_length=20)
    variable_name = forms.CharField(label='传值变量', max_length=20)
    excepted_result_type = forms.ChoiceField(
        choices=EXPECTED_RESULT_TYPE_CHOICES,
        label='期望结果类型'
    )
    excepted_result = forms.CharField(
        label='期望结果',
        widget=forms.Textarea(attrs={'rows': 3})
    )
    get_value_code = forms.CharField(
        label='取值代码',
        required=False,
        widget=forms.Textarea(attrs={'rows': 3})
    )

    class Meta:
        model = CaseStepInfo
        exclude = ['is_pass', 'case_step_info_id', 'api']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 设置字段样式
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
