from django.test import RequestFactory
import os
import sys
from pathlib import Path

# 设置项目根路径
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))  # 添加项目根目录到Python路径

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_platform.api_platform.settings')

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