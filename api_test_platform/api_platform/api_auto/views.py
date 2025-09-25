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
from .models import CaseStepInfo, ApiInfo, CaseInfo, ConfigUrl
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


def case_list(request):
    """用例列表：按模块分组、批量执行、删除"""
    # 1. 获取所有用例数据并按模块分组
    modules = CaseStepInfo.objects.values('part_name').distinct().order_by('part_name')
    module_cases = {}

    for module in modules:
        module_cases[module['part_name']] = CaseStepInfo.objects.filter(
            part_name=module['part_name']
        ).select_related('api').order_by('case_id', 'case_step_name')

    # 2. 处理删除请求
    if request.method == 'POST' and 'delete_case' in request.POST:
        case_step_id = request.POST.get('case_step_id')
        try:
            case = CaseStepInfo.objects.get(case_step_info_id=case_step_id)
            case.delete()
            messages.success(request, "用例删除成功！")
            return redirect(reverse('api_auto:case_list'))
        except CaseStepInfo.DoesNotExist:
            messages.error(request, "用例不存在！")
        except Exception as e:
            messages.error(request, f"删除失败：{str(e)}")
        return redirect(reverse('api_auto:case_list'))

    # 3. 执行所有用例逻辑
    if request.method == 'POST' and 'run_all' in request.POST:
        try:
            run_case_path = os.path.join(settings.FRAMEWORK_DIR, 'test_runner', 'run_case.py')
            result = subprocess.run(
                [settings.PYTHON_EXECUTABLE, run_case_path],
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                messages.success(request, f"所有用例执行完成！结果：{result.stdout}")
            else:
                messages.error(request, f"用例执行失败！错误：{result.stderr}")
        except Exception as e:
            messages.error(request, f"执行异常：{str(e)}")
        return redirect(reverse('api_auto:case_list'))

    return render(request, 'api_auto/case_list.html', {
        'module_cases': module_cases,  # 按模块分组的用例数据
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
        # 获取用例记录
        case_step = CaseStepInfo.objects.get(case_step_info_id=case_step_id)

        logger.debug("初始化RunSingleCase执行器")
        runner = RunSingleCase(case_step_id)

        logger.info("启动用例执行流程")
        result = runner.run()

        # 根据执行结果更新数据库
        if result['status'] == 'success':
            case_step.is_pass = "通过"
            logger.info(f"用例执行成功, 更新数据库状态为通过: {case_step_id}")
        else:
            case_step.is_pass = "失败"
            logger.warning(f"用例执行失败, 更新数据库状态为失败: {case_step_id}")

        # 保存执行结果到数据库
        case_step.save()

        # 记录详细执行结果
        logger.debug(f"用例执行结果: {result}")
        return JsonResponse(result)

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


@csrf_exempt
def run_all_cases(request):
    """执行全量用例并保存结果到数据库"""
    if request.method == 'GET':
        # 返回当前执行进度
        progress = cache.get('test_progress', {
            'total': 0,
            'current': 0,
            'status': 'idle'
        })
        return JsonResponse(progress)

    try:
        logger.info("开始执行全量用例")
        # 1. 初始化执行状态
        total_cases = CaseStepInfo.objects.count()
        cache.set('test_progress', {
            'total': total_cases,
            'current': 0,
            'status': 'running'
        }, 3600)

        # 2. 获取所有用例并执行
        case_steps = CaseStepInfo.objects.all()
        success_count = 0
        failure_count = 0

        for index, case_step in enumerate(case_steps):
            # 执行单条用例
            from test_runner.run_single_case import RunSingleCase
            runner = RunSingleCase(case_step.case_step_info_id)
            result = runner.run()

            # 更新用例状态
            case_step.is_pass = "通过" if result['passed'] else "失败"
            case_step.save()

            # 更新执行进度
            if result['passed']:
                success_count += 1
            else:
                failure_count += 1

            cache.set('test_progress', {
                'total': total_cases,
                'current': index + 1,
                'status': 'running',
                'success': success_count,
                'failure': failure_count
            }, 3600)

        # 3. 返回执行结果
        cache.set('test_progress', {
            'total': total_cases,
            'current': total_cases,
            'status': 'completed',
            'success': success_count,
            'failure': failure_count
        }, 60)

        return JsonResponse({
            'status': 'completed',
            'total': total_cases,
            'success': success_count,
            'failure': failure_count
        })

    except Exception as e:
        logger.error(f"全量执行失败: {str(e)}", exc_info=True)
        cache.set('test_progress', {
            'status': 'failed',
            'message': str(e)
        }, 60)
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

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
    failed_cases = CaseStepInfo.objects.filter(is_pass="失败").select_related('api')

    return render(request, 'api_auto/dashboard.html', {
        'pass_rate': round(pass_rate, 2),
        'stats': stats,
        'failed_cases': failed_cases
    })


def config_list(request):
    """环境配置列表"""
    configs = ConfigUrl.objects.all().order_by('section', 'key_name')
    return render(request, 'api_auto/config_list.html', {
        'configs': configs
    })


def config_edit(request, config_id=None):
    """编辑或新增环境配置"""
    if request.method == 'POST':
        section = request.POST.get('section')
        key_name = request.POST.get('key_name')

        # 检查是否已存在相同section和key_name的记录
        existing_config = ConfigUrl.objects.filter(
            section=section,
            key_name=key_name
        ).exclude(id=config_id).first()

        if existing_config:
            # 更新已有记录
            config = existing_config
            messages.info(request, "配置已存在，已更新原有记录")
        elif config_id:
            config = get_object_or_404(ConfigUrl, id=config_id)
        else:
            config = ConfigUrl()

        # 获取表单数据
        config.url_chin_name = request.POST.get('url_chin_name')
        config.section = section
        config.key_name = key_name
        config.urls_addr = request.POST.get('urls_addr')
        config.note = request.POST.get('note')

        try:
            config.save()
            messages.success(request, "配置保存成功！")
            return redirect('api_auto:config_list')
        except Exception as e:
            messages.error(request, f"保存失败：{str(e)}")
            return render(request, 'api_auto/config_edit.html', {
                'config': config,
                'error': str(e)
            })

    else:
        if config_id:
            config = get_object_or_404(ConfigUrl, id=config_id)
        else:
            config = ConfigUrl()

        return render(request, 'api_auto/config_edit.html', {
            'config': config
        })


def config_delete(request, config_id):
    """删除环境配置"""
    config = get_object_or_404(ConfigUrl, id=config_id)
    config.delete()
    messages.success(request, "配置删除成功！")
    return redirect('api_auto:config_list')


def api_management(request):
    """接口管理页面"""
    # 获取所有用例数据（关联接口信息）
    cases = CaseStepInfo.objects.select_related('api').all()

    # 获取所有关联的用例信息
    case_ids = [case.case_id for case in cases]
    case_infos = CaseInfo.objects.filter(case_id__in=case_ids)
    case_info_map = {info.case_id: info for info in case_infos}

    # 将用例信息附加到对应的CaseStepInfo对象
    for case in cases:
        case.case_info = case_info_map.get(case.case_id)

    return render(request, 'api_auto/api_management.html', {
        'cases': cases
    })


def api_management_add(request):
    """新增接口管理记录"""
    from .forms import ApiManagementForm

    if request.method == 'POST':
        form = ApiManagementForm(request.POST)
        if form.is_valid():
            try:
                # 保存API信息
                api = ApiInfo(
                    api_id=f"api_{form.cleaned_data['case_id']}_{form.cleaned_data['case_step_name']}",
                    api_name=form.cleaned_data['api_name'],
                    api_request_type=form.cleaned_data['api_request_type'],
                    api_request_url=form.cleaned_data['api_request_url'],
                    api_url_params=form.cleaned_data['api_url_params'],
                    api_post_data=form.cleaned_data['api_post_data']
                )
                api.save()

                # 保存用例信息
                case_info = CaseInfo(
                    case_info_id=f"case_{form.cleaned_data['case_id']}",
                    case_id=form.cleaned_data['case_id'],
                    case_name=form.cleaned_data['case_name'],
                    is_run=form.cleaned_data['is_run']
                )
                case_info.save()

                # 保存用例步骤信息
                case_step = CaseStepInfo(
                    case_step_info_id=f"step_{form.cleaned_data['case_id']}_{form.cleaned_data['case_step_name']}",
                    case_id=form.cleaned_data['case_id'],
                    case_step_name=form.cleaned_data['case_step_name'],
                    part_name=form.cleaned_data['part_name'],
                    api=api,
                    get_value_type=form.cleaned_data['get_value_type'],
                    variable_name=form.cleaned_data['variable_name'],
                    get_value_code=form.cleaned_data['get_value_code'],
                    excepted_result_type=form.cleaned_data['excepted_result_type'],
                    excepted_result=form.cleaned_data['excepted_result']
                )
                case_step.save()

                messages.success(request, "接口管理记录添加成功！")
                return redirect('api_auto:api_management')
            except Exception as e:
                messages.error(request, f"保存失败：{str(e)}")
                logger.error(f"新增接口管理记录失败: {str(e)}", exc_info=True)
        else:
            messages.error(request, "表单数据无效，请检查输入！")
    else:
        form = ApiManagementForm()

    return render(request, 'api_auto/api_management_form.html', {
        'form': form,
        'title': '新增接口管理记录'
    })


def api_management_edit(request, case_step_id):
    """编辑接口管理记录"""
    from .forms import ApiManagementForm
    case_step = get_object_or_404(CaseStepInfo, case_step_info_id=case_step_id)

    if request.method == 'POST':
        form = ApiManagementForm(request.POST, instance=case_step)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "接口管理记录更新成功！")
                return redirect('api_auto:api_management')
            except Exception as e:
                messages.error(request, f"更新失败：{str(e)}")
        else:
            messages.error(request, "表单数据无效，请检查输入！")
    else:
        # 获取关联的CaseInfo
        case_info = CaseInfo.objects.filter(case_id=case_step.case_id).first()

        initial_data = {
            'case_id': case_step.case_id,
            'case_name': case_info.case_name if case_info else '',
            'is_run': case_info.is_run if case_info else '是',
            'api_name': case_step.api.api_name if case_step.api else '',
            'api_request_type': case_step.api.api_request_type if case_step.api else '',
            'api_request_url': case_step.api.api_request_url if case_step.api else '',
            'api_url_params': case_step.api.api_url_params if case_step.api else '',
            'api_post_data': case_step.api.api_post_data if case_step.api else '',
        }
        form = ApiManagementForm(initial=initial_data, instance=case_step)

    return render(request, 'api_auto/api_management_form.html', {
        'form': form,
        'title': '编辑接口管理记录',
        'case_step_id': case_step_id
    })


def api_management_delete(request, case_step_id):
    """删除接口管理记录"""
    case_step = get_object_or_404(CaseStepInfo, case_step_info_id=case_step_id)
    try:
        # 删除关联的API信息和用例信息
        if case_step.api:
            case_step.api.delete()
        if case_step.case_info:
            case_step.case_info.delete()
        case_step.delete()
        messages.success(request, "接口管理记录删除成功！")
    except Exception as e:
        messages.error(request, f"删除失败：{str(e)}")
    return redirect('api_auto:api_management')