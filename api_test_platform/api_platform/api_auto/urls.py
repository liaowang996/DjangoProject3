from django.urls import path
from . import views

app_name = 'api_auto'  # 命名空间

urlpatterns = [
    path('', views.index, name='index'),  # 仪表盘首页
    path('import-excel/', views.import_excel, name='import_excel'),  # Excel导入
    path('case-list/', views.case_list, name='case_list'),  # 用例列表
    path('case-detail/<str:case_step_id>/', views.case_detail, name='case_detail'),  # 用例详情
    path('run-single-case/<str:case_step_id>/', views.run_single_case, name='run_single_case'),  # 单条执行
    path('run-all-cases/', views.run_all_cases, name='run_all_cases'),  # 全量执行
    path('dashboard/', views.dashboard, name='dashboard'),  # 仪表盘
    path('api-config/', views.api_config, name='api_config'),  # 接口配置
    # 环境配置相关路由
    path('config/', views.config_list, name='config_list'),
    path('config/edit/', views.config_edit, name='config_edit'),
    path('config/edit/<int:config_id>/', views.config_edit, name='config_edit'),
    path('config/delete/<int:config_id>/', views.config_delete, name='config_delete'),
    # 接口管理相关路由
    path('api-management/', views.api_management, name='api_management'),
    path('api-management/add/', views.api_management_add, name='api_management_add'),
    path('api-management/edit/<str:case_step_id>/', views.api_management_edit, name='api_management_edit'),
    path('api-management/delete/<str:case_step_id>/', views.api_management_delete, name='api_management_delete'),
]