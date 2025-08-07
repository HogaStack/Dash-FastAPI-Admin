import time
from dash import ctx, dcc, no_update
from dash.dependencies import ALL, Input, Output, State
from dash.exceptions import PreventUpdate
from typing import Dict
from api.monitor.job import JobApi
from config.constant import SysJobStatusConstant
from server import app
from utils.common_util import ValidateUtil
from utils.dict_util import DictManager
from utils.feedback_util import MessageManager
from utils.permission_util import PermissionManager
from utils.time_format_util import TimeFormatUtil


def generate_job_table(query_params: Dict):
    """
    根据查询参数获取定时任务表格数据及分页信息

    :param query_params: 查询参数
    :return: 定时任务表格数据及分页信息
    """
    table_info = JobApi.list_job(query_params)
    table_data = table_info['rows']
    table_pagination = dict(
        pageSize=table_info['page_size'],
        current=table_info['page_num'],
        showSizeChanger=True,
        pageSizeOptions=[10, 30, 50, 100],
        showQuickJumper=True,
        total=table_info['total'],
    )
    for item in table_data:
        if item['status'] == SysJobStatusConstant.NORMAL:
            item['status_checked'] = dict(checked=True)
        else:
            item['status_checked'] = dict(checked=False)
        item['job_group_tag'] = DictManager.get_dict_tag(
            dict_type='sys_job_group', dict_value=item.get('job_group')
        )
        item['key'] = str(item['job_id'])
        item['operation'] = [
            {'title': '修改', 'icon': 'antd-edit'}
            if PermissionManager.check_perms('monitor:job:edit')
            else None,
            {'title': '删除', 'icon': 'antd-delete'}
            if PermissionManager.check_perms('monitor:job:remove')
            else None,
            {'title': '执行一次', 'icon': 'antd-rocket'}
            if PermissionManager.check_perms('monitor:job:changeStatus')
            else None,
            {'title': '任务详细', 'icon': 'antd-eye'}
            if PermissionManager.check_perms('monitor:job:query')
            else None,
            {'title': '调度日志', 'icon': 'antd-history'}
            if PermissionManager.check_perms('monitor:job:query')
            else None,
        ]

    return [table_data, table_pagination]


@app.callback(
    output=dict(
        job_table_data=Output('job-list-table', 'data', allow_duplicate=True),
        job_table_pagination=Output(
            'job-list-table', 'pagination', allow_duplicate=True
        ),
        job_table_selectedrowkeys=Output('job-list-table', 'selectedRowKeys'),
    ),
    inputs=dict(
        search_click=Input('job-search', 'nClicks'),
        refresh_click=Input('job-refresh', 'nClicks'),
        pagination=Input('job-list-table', 'pagination'),
        operations=Input('job-operations-store', 'data'),
    ),
    state=dict(
        job_name=State('job-job_name-input', 'value'),
        job_group=State('job-job_group-select', 'value'),
        status_select=State('job-status-select', 'value'),
    ),
    prevent_initial_call=True,
)
def get_job_table_data(
    search_click,
    refresh_click,
    pagination,
    operations,
    job_name,
    job_group,
    status_select,
):
    """
    获取定时任务表格数据回调（进行表格相关增删查改操作后均会触发此回调）
    """
    query_params = dict(
        job_name=job_name,
        job_group=job_group,
        status=status_select,
        page_num=1,
        page_size=10,
    )
    triggered_id = ctx.triggered_id
    if triggered_id == 'job-list-table':
        query_params.update(
            {
                'page_num': pagination['current'],
                'page_size': pagination['pageSize'],
            }
        )
    if search_click or refresh_click or pagination or operations:
        table_data, table_pagination = generate_job_table(query_params)
        return dict(
            job_table_data=table_data,
            job_table_pagination=table_pagination,
            job_table_selectedrowkeys=None,
        )

    raise PreventUpdate


# 重置定时任务搜索表单数据回调
app.clientside_callback(
    """
    (reset_click) => {
        if (reset_click) {
            return [null, null, null, {'type': 'reset'}]
        }
        throw window.dash_clientside.PreventUpdate;
    }
    """,
    [
        Output('job-job_name-input', 'value'),
        Output('job-job_group-select', 'value'),
        Output('job-status-select', 'value'),
        Output('job-operations-store', 'data'),
    ],
    Input('job-reset', 'nClicks'),
    prevent_initial_call=True,
)


# 隐藏/显示定时任务搜索表单回调
app.clientside_callback(
    """
    (hidden_click, hidden_status) => {
        if (hidden_click) {
            return [
                !hidden_status,
                hidden_status ? '隐藏搜索' : '显示搜索'
            ]
        }
        throw window.dash_clientside.PreventUpdate;
    }
    """,
    [
        Output('job-search-form-container', 'hidden'),
        Output('job-hidden-tooltip', 'title'),
    ],
    Input('job-hidden', 'nClicks'),
    State('job-search-form-container', 'hidden'),
    prevent_initial_call=True,
)


# 根据选择的表格数据行数控制修改按钮状态回调
app.clientside_callback(
    """
    (table_rows_selected) => {
        outputs_list = window.dash_clientside.callback_context.outputs_list;
        if (outputs_list) {
            if (table_rows_selected?.length === 1) {
                return false;
            }
            return true;
        }
        throw window.dash_clientside.PreventUpdate;
    }
    """,
    Output({'type': 'job-operation-button', 'index': 'edit'}, 'disabled'),
    Input('job-list-table', 'selectedRowKeys'),
    prevent_initial_call=True,
)


# 根据选择的表格数据行数控制删除按钮状态回调
app.clientside_callback(
    """
    (table_rows_selected) => {
        outputs_list = window.dash_clientside.callback_context.outputs_list;
        if (outputs_list) {
            if (table_rows_selected?.length > 0) {
                return false;
            }
            return true;
        }
        throw window.dash_clientside.PreventUpdate;
    }
    """,
    Output({'type': 'job-operation-button', 'index': 'delete'}, 'disabled'),
    Input('job-list-table', 'selectedRowKeys'),
    prevent_initial_call=True,
)


# 定时任务表单数据双向绑定回调
app.clientside_callback(
    """
    (row_data, form_value) => {
        trigger_id = window.dash_clientside.callback_context.triggered_id;
        if (trigger_id === 'job-form-store') {
            return [window.dash_clientside.no_update, row_data];
        }
        if (trigger_id === 'job-form') {
            Object.assign(row_data, form_value);
            return [row_data, window.dash_clientside.no_update];
        }
        throw window.dash_clientside.PreventUpdate;
    }
    """,
    [
        Output('job-form-store', 'data', allow_duplicate=True),
        Output('job-form', 'values'),
    ],
    [
        Input('job-form-store', 'data'),
        Input('job-form', 'values'),
    ],
    prevent_initial_call=True,
)


@app.callback(
    output=dict(
        modal_visible=Output('job-modal', 'visible', allow_duplicate=True),
        modal_title=Output('job-modal', 'title'),
        form_value=Output('job-form-store', 'data', allow_duplicate=True),
        form_label_validate_status=Output(
            'job-form', 'validateStatuses', allow_duplicate=True
        ),
        form_label_validate_info=Output(
            'job-form', 'helps', allow_duplicate=True
        ),
        modal_type=Output('job-modal_type-store', 'data'),
    ),
    inputs=dict(
        operation_click=Input(
            {'type': 'job-operation-button', 'index': ALL}, 'nClicks'
        ),
        dropdown_click=Input('job-list-table', 'nClicksDropdownItem'),
    ),
    state=dict(
        selected_row_keys=State('job-list-table', 'selectedRowKeys'),
        recently_clicked_dropdown_item_title=State(
            'job-list-table', 'recentlyClickedDropdownItemTitle'
        ),
        recently_dropdown_item_clicked_row=State(
            'job-list-table', 'recentlyDropdownItemClickedRow'
        ),
    ),
    prevent_initial_call=True,
)
def add_edit_job_modal(
    operation_click,
    dropdown_click,
    selected_row_keys,
    recently_clicked_dropdown_item_title,
    recently_dropdown_item_clicked_row,
):
    """
    显示新增或编辑定时任务弹窗回调
    """
    trigger_id = ctx.triggered_id
    if (
        trigger_id == {'index': 'add', 'type': 'job-operation-button'}
        or trigger_id == {'index': 'edit', 'type': 'job-operation-button'}
        or (
            trigger_id == 'job-list-table'
            and recently_clicked_dropdown_item_title == '修改'
        )
    ):
        if trigger_id == {'index': 'add', 'type': 'job-operation-button'}:
            job_info = dict(
                job_name=None,
                job_group=None,
                invoke_target=None,
                cron_expression=None,
                job_args=None,
                job_kwargs=None,
                misfire_policy='1',
                concurrent='1',
                status=SysJobStatusConstant.NORMAL,
            )
            return dict(
                modal_visible=True,
                modal_title='新增任务',
                form_value=job_info,
                form_label_validate_status=None,
                form_label_validate_info=None,
                modal_type={'type': 'add'},
            )
        elif trigger_id == {
            'index': 'edit',
            'type': 'job-operation-button',
        } or (
            trigger_id == 'job-list-table'
            and recently_clicked_dropdown_item_title == '修改'
        ):
            if trigger_id == {'index': 'edit', 'type': 'job-operation-button'}:
                job_id = int(','.join(selected_row_keys))
            else:
                job_id = int(recently_dropdown_item_clicked_row['key'])
            job_info_res = JobApi.get_job(job_id=job_id)
            job_info = job_info_res['data']
            return dict(
                modal_visible=True,
                modal_title='编辑任务',
                form_value=job_info,
                form_label_validate_status=None,
                form_label_validate_info=None,
                modal_type={'type': 'edit'},
            )

    raise PreventUpdate


@app.callback(
    output=dict(
        form_label_validate_status=Output(
            'job-form', 'validateStatuses', allow_duplicate=True
        ),
        form_label_validate_info=Output(
            'job-form', 'helps', allow_duplicate=True
        ),
        modal_visible=Output('job-modal', 'visible'),
        operations=Output('job-operations-store', 'data', allow_duplicate=True),
    ),
    inputs=dict(confirm_trigger=Input('job-modal', 'okCounts')),
    state=dict(
        modal_type=State('job-modal_type-store', 'data'),
        form_value=State('job-form-store', 'data'),
        form_label=State(
            {'type': 'job-form-label', 'index': ALL, 'required': True}, 'label'
        ),
    ),
    running=[[Output('job-modal', 'confirmLoading'), True, False]],
    prevent_initial_call=True,
)
def job_confirm(confirm_trigger, modal_type, form_value, form_label):
    """
    新增或编定时任务弹窗确认回调，实现新增或编辑操作
    """
    if confirm_trigger:
        # 获取所有必填表单项对应label的index
        form_label_list = [x['id']['index'] for x in ctx.states_list[-1]]
        # 获取所有输入必填表单项对应的label
        form_label_state = {
            x['id']['index']: x.get('value') for x in ctx.states_list[-1]
        }
        if all(
            ValidateUtil.not_empty(item)
            for item in [form_value.get(k) for k in form_label_list]
        ):
            params_add = form_value
            params_edit = params_add.copy()
            modal_type = modal_type.get('type')
            if modal_type == 'add':
                JobApi.add_job(params_add)
            if modal_type == 'edit':
                JobApi.update_job(params_edit)
            if modal_type == 'add':
                MessageManager.success(content='新增成功')

                return dict(
                    form_label_validate_status=None,
                    form_label_validate_info=None,
                    modal_visible=False,
                    operations={'type': 'add'},
                )
            if modal_type == 'edit':
                MessageManager.success(content='编辑成功')

                return dict(
                    form_label_validate_status=None,
                    form_label_validate_info=None,
                    modal_visible=False,
                    operations={'type': 'edit'},
                )

            return dict(
                form_label_validate_status=None,
                form_label_validate_info=None,
                modal_visible=no_update,
                operations=no_update,
            )

        return dict(
            form_label_validate_status={
                form_label_state.get(k): None
                if ValidateUtil.not_empty(form_value.get(k))
                else 'error'
                for k in form_label_list
            },
            form_label_validate_info={
                form_label_state.get(k): None
                if ValidateUtil.not_empty(form_value.get(k))
                else f'{form_label_state.get(k)}不能为空!'
                for k in form_label_list
            },
            modal_visible=no_update,
            operations=no_update,
        )

    raise PreventUpdate


@app.callback(
    Output('job-operations-store', 'data', allow_duplicate=True),
    [
        Input('job-list-table', 'recentlySwitchDataIndex'),
        Input('job-list-table', 'recentlySwitchStatus'),
        Input('job-list-table', 'recentlySwitchRow'),
    ],
    prevent_initial_call=True,
)
def table_switch_job_status(
    recently_switch_data_index, recently_switch_status, recently_switch_row
):
    """
    表格内切换定时任务状态回调
    """
    if recently_switch_data_index:
        JobApi.change_job_status(
            job_id=int(recently_switch_row['key']),
            status='0' if recently_switch_status else '1',
        )
        MessageManager.success(content='修改成功')

        return {'type': 'switch-status'}

    raise PreventUpdate


@app.callback(
    output=dict(
        modal_visible=Output(
            'job_detail-modal', 'visible', allow_duplicate=True
        ),
        modal_title=Output('job_detail-modal', 'title'),
        form_value=Output(
            {'type': 'job_detail-form-value', 'index': ALL}, 'children'
        ),
    ),
    inputs=dict(dropdown_click=Input('job-list-table', 'nClicksDropdownItem')),
    state=dict(
        recently_clicked_dropdown_item_title=State(
            'job-list-table', 'recentlyClickedDropdownItemTitle'
        ),
        recently_dropdown_item_clicked_row=State(
            'job-list-table', 'recentlyDropdownItemClickedRow'
        ),
    ),
    prevent_initial_call=True,
)
def get_job_detail_modal(
    dropdown_click,
    recently_clicked_dropdown_item_title,
    recently_dropdown_item_clicked_row,
):
    """
    显示定时任务详情弹窗回调及执行一次定时任务回调
    """
    # 获取所有输出表单项对应value的index
    form_value_list = [x['id']['index'] for x in ctx.outputs_list[-1]]
    # 显示定时任务详情弹窗
    if dropdown_click and recently_clicked_dropdown_item_title == '任务详细':
        job_id = int(recently_dropdown_item_clicked_row['key'])
        job_info_res = JobApi.get_job(job_id=job_id)
        job_info = job_info_res['data']
        if job_info.get('misfire_policy') == '1':
            job_info['misfire_policy'] = '立即执行'
        elif job_info.get('misfire_policy') == '2':
            job_info['misfire_policy'] = '执行一次'
        else:
            job_info['misfire_policy'] = '放弃执行'
        job_info['concurrent'] = (
            '是' if job_info.get('concurrent') == '0' else '否'
        )
        job_info['job_group'] = DictManager.get_dict_label(
            dict_type='sys_job_group',
            dict_value=job_info.get('job_group'),
        )
        job_info['job_executor'] = DictManager.get_dict_label(
            dict_type='sys_job_executor',
            dict_value=job_info.get('job_executor'),
        )
        job_info['status'] = DictManager.get_dict_label(
            dict_type='sys_job_status',
            dict_value=job_info.get('status'),
        )
        job_info['create_time'] = TimeFormatUtil.format_time(
            job_info.get('create_time')
        )
        return dict(
            modal_visible=True,
            modal_title='任务详情',
            form_value=[job_info.get(k) for k in form_value_list],
        )

    # 执行一次定时任务
    if dropdown_click and recently_clicked_dropdown_item_title == '执行一次':
        job_info_res = JobApi.run_job(
            job_id=int(recently_dropdown_item_clicked_row['key']),
            job_group=recently_dropdown_item_clicked_row['job_group'],
        )
        MessageManager.success(content='执行成功')

        return dict(
            modal_visible=False,
            modal_title=None,
            form_value=[None] * len(form_value_list),
        )

    raise PreventUpdate


@app.callback(
    [
        Output('job-delete-text', 'children'),
        Output('job-delete-confirm-modal', 'visible'),
        Output('job-delete-ids-store', 'data'),
    ],
    [
        Input({'type': 'job-operation-button', 'index': ALL}, 'nClicks'),
        Input('job-list-table', 'nClicksDropdownItem'),
    ],
    [
        State('job-list-table', 'selectedRowKeys'),
        State('job-list-table', 'recentlyClickedDropdownItemTitle'),
        State('job-list-table', 'recentlyDropdownItemClickedRow'),
    ],
    prevent_initial_call=True,
)
def job_delete_modal(
    operation_click,
    dropdown_click,
    selected_row_keys,
    recently_clicked_dropdown_item_title,
    recently_dropdown_item_clicked_row,
):
    """
    显示删除定时任务二次确认弹窗回调
    """
    trigger_id = ctx.triggered_id
    if trigger_id == {'index': 'delete', 'type': 'job-operation-button'} or (
        trigger_id == 'job-list-table'
        and recently_clicked_dropdown_item_title == '删除'
    ):
        if trigger_id == {'index': 'delete', 'type': 'job-operation-button'}:
            job_ids = ','.join(selected_row_keys)
        else:
            if recently_clicked_dropdown_item_title == '删除':
                job_ids = recently_dropdown_item_clicked_row['key']
            else:
                return [no_update] * 3

        return [
            f'是否确认删除任务编号为{job_ids}的任务？',
            True,
            job_ids,
        ]

    raise PreventUpdate


@app.callback(
    Output('job-operations-store', 'data', allow_duplicate=True),
    Input('job-delete-confirm-modal', 'okCounts'),
    State('job-delete-ids-store', 'data'),
    prevent_initial_call=True,
)
def job_delete_confirm(delete_confirm, job_ids_data):
    """
    删除定时任务弹窗确认回调，实现删除操作
    """
    if delete_confirm:
        params = job_ids_data
        JobApi.del_job(params)
        MessageManager.success(content='删除成功')

        return {'type': 'delete'}

    raise PreventUpdate


@app.callback(
    output=dict(
        job_log_modal_visible=Output('job_to_job_log-modal', 'visible'),
        job_log_modal_title=Output('job_to_job_log-modal', 'title'),
        job_log_job_name=Output(
            'job_log-job_name-input', 'value', allow_duplicate=True
        ),
        job_log_search_nclick=Output('job_log-search', 'nClicks'),
    ),
    inputs=dict(
        operation_click=Input(
            {'type': 'job-operation-log', 'index': ALL}, 'nClicks'
        ),
        dropdown_click=Input('job-list-table', 'nClicksDropdownItem'),
    ),
    state=dict(
        recently_clicked_dropdown_item_title=State(
            'job-list-table', 'recentlyClickedDropdownItemTitle'
        ),
        recently_dropdown_item_clicked_row=State(
            'job-list-table', 'recentlyDropdownItemClickedRow'
        ),
        job_log_search_nclick=State('job_log-search', 'nClicks'),
    ),
    prevent_initial_call=True,
)
def job_to_job_log_modal(
    operation_click,
    dropdown_click,
    recently_clicked_dropdown_item_title,
    recently_dropdown_item_clicked_row,
    job_log_search_nclick,
):
    """
    显示定时任务对应调度日志表格弹窗回调
    """

    trigger_id = ctx.triggered_id
    if trigger_id == {'index': 'log', 'type': 'job-operation-log'} or (
        trigger_id == 'job-list-table'
        and recently_clicked_dropdown_item_title == '调度日志'
    ):
        if (
            trigger_id == 'job-list-table'
            and recently_clicked_dropdown_item_title == '调度日志'
        ):
            return dict(
                job_log_modal_visible=True,
                job_log_modal_title='任务调度日志',
                job_log_job_name=recently_dropdown_item_clicked_row.get(
                    'job_name'
                ),
                job_log_search_nclick=job_log_search_nclick + 1
                if job_log_search_nclick
                else 1,
            )

        return dict(
            job_log_modal_visible=True,
            job_log_modal_title='任务调度日志',
            job_log_job_name=None,
            job_log_search_nclick=job_log_search_nclick + 1
            if job_log_search_nclick
            else 1,
        )

    raise PreventUpdate


@app.callback(
    [
        Output('job-export-container', 'data', allow_duplicate=True),
        Output('job-export-complete-judge-container', 'data'),
    ],
    Input('job-export', 'nClicks'),
    [
        State('job-job_name-input', 'value'),
        State('job-job_group-select', 'value'),
        State('job-status-select', 'value'),
    ],
    running=[[Output('job-export', 'loading'), True, False]],
    prevent_initial_call=True,
)
def export_job_list(export_click, job_name, job_group, status_select):
    """
    导出定时任务信息回调
    """
    if export_click:
        export_params = dict(
            job_name=job_name,
            job_group=job_group,
            status=status_select,
        )
        export_job_res = JobApi.export_job(export_params)
        export_job = export_job_res.content
        MessageManager.success(content='导出成功')

        return [
            dcc.send_bytes(
                export_job,
                f'定时任务信息_{time.strftime("%Y%m%d%H%M%S", time.localtime())}.xlsx',
            ),
            {'timestamp': time.time()},
        ]

    raise PreventUpdate


@app.callback(
    Output('job-export-container', 'data', allow_duplicate=True),
    Input('job-export-complete-judge-container', 'data'),
    prevent_initial_call=True,
)
def reset_job_export_status(data):
    """
    导出完成后重置下载组件数据回调，防止重复下载文件
    """
    time.sleep(0.5)
    if data:
        return None

    raise PreventUpdate
