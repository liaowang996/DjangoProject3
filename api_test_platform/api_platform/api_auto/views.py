import os
import shutil
import subprocess
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.contrib import messages
from django.db.models import F, Q, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger  # 内置分页
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from common.log_utils import logger
# 导入自定义模型和工具
from .models import CaseStepInfo, ApiInfo, CaseInfo
from .forms import ExcelUploadForm
from common.excel_to_mysql_importer import ExcelToMysqlImporter
from common.excel_utils import ExcelUtils
from test_runner.run_case import RunCase


def index(request):
    """首页：接口自动化、UI自动化、造数功能入口"""
    return render(request, 'api_auto/index.html')


# Excel导入视图
def import_excel(request):
    """Excel导入页面：上传Excel到test_data，再导入MySQL"""
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            # 1. 验证文件格式（仅支持xls/xlsx）
            if not excel_file.name.endswith(('.xls', '.xlsx')):
                messages.error(request, "仅支持xls/xlsx格式文件！")
                return redirect(reverse('api_auto:import_excel'))

            # 2. 保存文件到test_data目录
            test_data_dir = settings.FRAMEWORK_DIR / 'test_data'
            fs = FileSystemStorage(location=test_data_dir)
            import datetime
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"{timestamp}_{excel_file.name}"
            fs.save(filename, excel_file)
            file_path = os.path.join(test_data_dir, filename)
            messages.success(request, f"Excel文件上传成功：{filename}")

            # 3. 导入数据库
            try:
                importer = ExcelToMysqlImporter()
                excel_utils = ExcelUtils(file_path, sheet_name='Sheet1')
                case_info_list = excel_utils.get_sheet_data_by_dict()
                wrapped_case_info = [{'case_id': f"case_{i}", 'case_info': [case]} for i, case in
                                     enumerate(case_info_list)]
                import_result = importer.import_case_info(wrapped_case_info)
                importer.close()
                messages.success(request,
                                 f"数据导入完成！总条数：{import_result['total']}，成功：{import_result['success']}，失败：{import_result['fail']}")
            except Exception as e:
                messages.error(request, f"数据导入失败：{str(e)}")
                if os.path.exists(file_path):
                    os.remove(file_path)
                return redirect(reverse('api_auto:import_excel'))

            return redirect(reverse('api_auto:case_list'))
    else:
        form = ExcelUploadForm()

    return render(request, 'api_auto/import_excel.html', {'form': form})


# 用例列表视图（使用Django内置分页）
def case_list(request):
    """用例列表：分页（每页10条）、筛选、批量执行"""
    # 1. 获取所有用例数据（关联接口信息）
    case_queryset = CaseStepInfo.objects.select_related('api').all()

    # 2. 内置分页处理（每页10条）
    paginator = Paginator(case_queryset, 10)  # 核心：Django内置分页，无第三方依赖
    page = request.GET.get('page', 1)  # 从URL获取当前页码，默认第1页
    try:
        cases = paginator.page(page)  # 获取当前页数据
    except PageNotAnInteger:
        cases = paginator.page(1)  # 若页码不是整数，返回第1页
    except EmptyPage:
        cases = paginator.page(paginator.num_pages)  # 若页码超出范围，返回最后1页

    # 3. 批量执行逻辑
    if request.method == 'POST' and 'batch_run' in request.POST:
        selected_case_ids = request.POST.getlist('case_ids')
        if not selected_case_ids:
            messages.warning(request, "请选择至少一条用例执行！")
            return redirect(reverse('api_auto:case_list'))

        try:
            os.environ['SELECTED_CASE_IDS'] = ','.join(selected_case_ids)
            run_case_path = os.path.join(settings.FRAMEWORK_DIR, 'test_runner', 'run_case.py')
            result = subprocess.run(
                [settings.PYTHON_EXECUTABLE, run_case_path, '--selected-cases'],
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                messages.success(request, f"批量执行完成！结果：{result.stdout}")
            else:
                messages.error(request, f"批量执行失败！错误：{result.stderr}")
        except Exception as e:
            messages.error(request, f"批量执行异常：{str(e)}")
        return redirect(reverse('api_auto:case_list'))

    return render(request, 'api_auto/case_list.html', {
        'cases': cases,  # 当前页用例数据
        'paginator': paginator,  # 分页器对象（用于模板显示总页数）
        'current_page': page  # 当前页码
    })


# 接口配置视图
def api_config(request):
    """接口配置页面：管理API基础信息"""
    apis = ApiInfo.objects.all().order_by('api_name')
    return render(request, 'api_auto/api_config.html', {
        'apis': apis
    })

# 用例详情视图
def case_detail(request, case_step_id):
    """用例详情：展示完整用例信息"""
    case_step = get_object_or_404(CaseStepInfo, case_step_info_id=case_step_id)
    case_info = CaseInfo.objects.filter(case_info_id=case_step.case_step_info_id).first()
    return render(request, 'api_auto/case_detail.html', {
        'case_step': case_step,
        'case_info': case_info
    })


def run_single_case(request, case_step_id):
    """单条用例执行（AJAX请求）"""
    logger.info(f"开始执行单条用例, case_step_id={case_step_id}")
    from test_runner.run_single_case import RunSingleCase

    try:
        logger.debug("初始化RunSingleCase执行器")
        runner = RunSingleCase(case_step_id)

        logger.info("启动用例执行流程")
        result = runner.run()

        if result['status'] == 'success':
            logger.info(f"用例执行成功, 更新数据库状态: {case_step_id}")
            case_step = CaseStepInfo.objects.get(case_step_info_id=case_step_id)
            case_step.is_pass = "通过"
            case_step.save()
            logger.debug(f"返回成功结果: {result}")
            return JsonResponse(result)

        logger.warning(f"用例执行失败: {result.get('message')}")
        return JsonResponse(result, status=400)

    except CaseStepInfo.DoesNotExist:
        logger.error(f"用例记录不存在: {case_step_id}")
        return JsonResponse(
            {'status': 'error', 'message': '测试用例不存在'},
            status=404
        )
    except Exception as e:
        logger.error(f"单条用例执行异常: {str(e)}", exc_info=True)
        return JsonResponse(
            {'status': 'error', 'message': str(e)},
            status=500
        )

        if result.returncode == 0:
            case_step.is_pass = "通过"
            case_step.save()
            return JsonResponse({'status': 'success', 'message': result.stdout})
        else:
            case_step.is_pass = "失败"
            case_step.save()
            return JsonResponse({'status': 'error', 'message': result.stderr})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


# 全量用例执行视图
@csrf_exempt
def run_all_cases(request):
    """执行全量用例并生成报告"""
    from test_runner.run_case import RunCase
    from common.email_utils import EmailUtils

    if request.method == 'GET':
        # 返回当前执行进度
        progress = cache.get('test_progress', {'total': 0, 'current': 0, 'status': 'idle'})
        return JsonResponse(progress)

    try:
        logger.info("开始全量执行用例")
        # 1. 初始化执行状态
        cache.set('test_progress', {
            'total': 0,
            'current': 0,
            'status': 'preparing'
        }, 3600)

        # 2. 执行测试
        runner = RunCase()
        report_file = runner.run()

        if not report_file:
            raise ValueError("测试报告生成失败")


        # 3. 发送邮件
        logger.info("准备发送测试报告邮件")
        email_body = runner.generate_email_body(report_file)
        email_utils = EmailUtils(
            smtp_body=email_body,
            smtp_attch_path=report_file
        )

        # 4. 更新执行状态
        cache.set('test_progress', {
            'total': 1,
            'current': 1,
            'status': 'sending_email'
        }, 3600)

        if email_utils.send_email():
            messages.success(request,
                f"全量执行完成！报告已发送至邮箱。本地路径：{report_file}")
            cache.set('test_progress', {
                'total': 1,
                'current': 1,
                'status': 'success'
            }, 60)
        else:
            messages.warning(request,
                "全量执行完成但邮件发送失败！报告路径：" + report_file)
            cache.set('test_progress', {
                'total': 1,
                'current': 1,
                'status': 'email_failed'
            }, 60)

    except Exception as e:
        logger.error(f"全量执行异常: {str(e)}", exc_info=True)
        messages.error(request, f"全量执行失败：{str(e)}")
        cache.set('test_progress', {
            'total': 1,
            'current': 0,
            'status': 'failed'
        }, 60)

    return redirect(reverse('api_auto:case_list'))

def dashboard(request):
    """仪表盘视图，展示用例执行情况"""
    # 获取用例统计信息
    stats = CaseStepInfo.objects.aggregate(
        total=Count('case_step_info_id'),
        passed=Count('case_step_info_id', filter=Q(is_pass="通过")),
        failed=Count('case_step_info_id', filter=Q(is_pass="失败"))
    )

    # 计算通过率
    pass_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0

    # 获取失败用例列表
    failed_cases = CaseStepInfo.objects.filter(is_pass="失败").select_related('case_id')

    return render(request, 'api_auto/dashboard.html', {
        'pass_rate': round(pass_rate, 2),
        'stats': stats,
        'failed_cases': failed_cases
    })