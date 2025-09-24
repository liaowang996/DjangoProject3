from django.test import RequestFactory
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_platform.settings')

import django
django.setup()

from api_platform.api_auto.views import run_single_case
from django.test import RequestFactory

# 创建模拟请求
request = RequestFactory().get('/')

# 示例执行（替换为实际获取的case_step_info_id）
case_step_id = "step_01"  # 这里替换为实际ID
response = run_single_case(request, case_step_id)
print(response.json())