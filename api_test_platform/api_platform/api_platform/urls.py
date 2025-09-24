"""
URL configuration for api_platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
# 仅导入首页视图（index在api_auto/views.py中）
from api_auto.views import index

urlpatterns = [
    path('admin/', admin.site.urls),  # Django后台路由
    path('', index, name='index'),    # 首页路由（映射到api_auto的index视图）
    # 接口自动化路由：分发到api_auto应用的urls.py（具体路由在api_auto/urls.py中）
    path('api-auto/', include('api_auto.urls')),
    # UI自动化路由：分发到ui_auto应用（待开发，已创建空urls.py）
    path('ui-auto/', include('ui_auto.urls')),
    # 平台造数路由：分发到data_maker应用（待开发，已创建空urls.py）
    path('data-maker/', include('data_maker.urls')),
]