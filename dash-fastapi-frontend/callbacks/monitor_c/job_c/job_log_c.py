import time
from dash import ctx, dcc
from dash.dependencies import ALL, Input, Output, State
from dash.exceptions import PreventUpdate
from api.monitor.job_log import JobLogApi
from server import app
from utils.dict_util import DictManager
from utils.feedback_util import MessageManager
from utils.permission_util import PermissionManager
from utils.time_format_util import TimeFormatUtil


@app.callback(
    output=dict(
        job_log_table_data=Output(
            'job_log-list-table', 'data', allow_duplicate=True
        ),
        job_log_table_pagination=Output(
            'job_log-list-table', 'pagination', allow_duplicate=True
        ),
        job_log_table_selectedrowkeys=Output(
            'job_log-list-table', 'selectedRowKeys'
        ),
    ),
    inputs=dict(
        search_click=Input('job_log-search', 'nClicks'),
        refresh_click=Input('job_log-refresh', 'nClicks'),
        pagination=Input('job_log-list-table', 'pagination'),
        operations=Input('job_log-operations-store', 'data'),
    ),
    state=dict(
        job_name=State('job_log-job_name-input', 'value'),
        job_group=State('job_log-job_group-select', 'value'),
        status_select=State('job_log-status-select', 'value'),
        create_time_range=State('job_log-create_time-range', 'value'),
    ),
    prevent_initial_call=True,
)
def get_job_log_table_data(
    search_click,
    refresh_click,
    pagination,
    operations,
    job_name,
    job_group,
    status_select,
    create_time_range,
):
    """
    获取定时任务对应调度日志表格数据回调（进行表格相关增删查改操作后均会触发此回调）
    """

    begin_time = None
    end_time = None
    if create_time_range:
        begin_time = create_time_range[0]
        end_time = create_time_range[1]
    query_params = dict(
        job_name=job_name,
        job_group=job_group,
        status=status_select,
        begin_time=begin_time,
        end_time=end_time,
        page_num=1,
        page_size=10,
    )
    triggered_id = ctx.triggered_id
    if triggered_id == 'job_log-list-table':
        query_params.update(
            {
                'page_num': pagination['current'],
                'page_size': pagination['pageSize'],
            }
        )
    if search_click or refresh_click or pagination or operations:
        table_info = JobLogApi.list_job_log(query_params)
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
            item['status_tag'] = DictManager.get_dict_tag(
                dict_type='sys_job_status', dict_value=item.get('status')
            )
            item['job_group_tag'] = DictManager.get_dict_tag(
                dict_type='sys_job_group', dict_value=item.get('job_group')
            )
            item['create_time'] = TimeFormatUtil.format_time(
                item.get('create_time')
            )
            item['key'] = str(item['job_log_id'])
            item['operation'] = [
                {'content': '详情', 'type': 'link', 'icon': 'antd-eye'}
                if PermissionManager.check_perms('monitor:job:query')
                else {},
            ]

        return dict(
            job_log_table_data=table_data,
            job_log_table_pagination=table_pagination,
            job_log_table_selectedrowkeys=None,
        )

    raise PreventUpdate


# 重置定时任务调度日志搜索表单数据回调
app.clientside_callback(
    """
    (reset_click) => {
        if (reset_click) {
            return [null, null, null, null, {'type': 'reset'}]
        }
        throw window.dash_clientside.PreventUpdate;
    }
    """,
    [
        Output('job_log-job_name-input', 'value'),
        Output('job_log-job_group-select', 'value'),
        Output('job_log-status-select', 'value'),
        Output('job_log-create_time-range', 'value'),
        Output('job_log-operations-store', 'data'),
    ],
    Input('job_log-reset', 'nClicks'),
    prevent_initial_call=True,
)


# 隐藏/显示定时任务调度日志搜索表单回调
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
        Output('job_log-search-form-container', 'hidden'),
        Output('job_log-hidden-tooltip', 'title'),
    ],
    Input('job_log-hidden', 'nClicks'),
    State('job_log-search-form-container', 'hidden'),
    prevent_initial_call=True,
)


@app.callback(
    output=dict(
        modal_visible=Output('job_log-modal', 'visible', allow_duplicate=True),
        modal_title=Output('job_log-modal', 'title'),
        form_value=Output(
            {'type': 'job_log-form-value', 'index': ALL}, 'children'
        ),
    ),
    inputs=dict(button_click=Input('job_log-list-table', 'nClicksButton')),
    state=dict(
        clicked_content=State('job_log-list-table', 'clickedContent'),
        recently_button_clicked_row=State(
            'job_log-list-table', 'recentlyButtonClickedRow'
        ),
    ),
    prevent_initial_call=True,
)
def add_edit_job_log_modal(
    button_click, clicked_content, recently_button_clicked_row
):
    if button_click:
        # 获取所有输出表单项对应value的index
        form_value_list = [x['id']['index'] for x in ctx.outputs_list[-1]]
        job_log_info = recently_button_clicked_row
        job_log_info['job_group'] = DictManager.get_dict_label(
            dict_type='sys_job_group',
            dict_value=job_log_info.get('job_group'),
        )
        job_log_info['status'] = DictManager.get_dict_label(
            dict_type='sys_job_status',
            dict_value=job_log_info.get('status'),
        )
        return dict(
            modal_visible=True,
            modal_title='任务执行日志详情',
            form_value=[job_log_info.get(k) for k in form_value_list],
        )

    raise PreventUpdate


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
    Output({'type': 'job_log-operation-button', 'index': 'delete'}, 'disabled'),
    Input('job_log-list-table', 'selectedRowKeys'),
    prevent_initial_call=True,
)


@app.callback(
    [
        Output('job_log-delete-text', 'children'),
        Output('job_log-delete-confirm-modal', 'visible'),
        Output('job_log-delete-ids-store', 'data'),
    ],
    Input({'type': 'job_log-operation-button', 'index': ALL}, 'nClicks'),
    State('job_log-list-table', 'selectedRowKeys'),
    prevent_initial_call=True,
)
def job_log_delete_modal(operation_click, selected_row_keys):
    """
    显示删除或清空定时任务调度日志二次确认弹窗回调
    """
    trigger_id = ctx.triggered_id
    if trigger_id.index in ['delete', 'clear']:
        if trigger_id.index == 'delete':
            job_log_ids = ','.join(selected_row_keys)

            return [
                f'是否确认删除日志编号为{job_log_ids}的任务执行日志？',
                True,
                {'oper_type': 'delete', 'job_log_ids': job_log_ids},
            ]

        elif trigger_id.index == 'clear':
            return [
                '是否确认清除所有的任务执行日志？',
                True,
                {'oper_type': 'clear'},
            ]

    raise PreventUpdate


@app.callback(
    Output('job_log-operations-store', 'data', allow_duplicate=True),
    Input('job_log-delete-confirm-modal', 'okCounts'),
    State('job_log-delete-ids-store', 'data'),
    prevent_initial_call=True,
)
def job_log_delete_confirm(delete_confirm, job_log_ids_data):
    """
    删除或清空定时任务调度日志弹窗确认回调，实现删除或清空操作
    """
    if delete_confirm:
        oper_type = job_log_ids_data.get('oper_type')
        if oper_type == 'clear':
            JobLogApi.clean_job_log()
            MessageManager.success(content='清除成功')

            return {'type': 'clear'}

        else:
            params = job_log_ids_data.get('job_log_ids')
            JobLogApi.del_job_log(params)
            MessageManager.success(content='删除成功')

            return {'type': 'delete'}

    raise PreventUpdate


@app.callback(
    [
        Output('job_log-export-container', 'data', allow_duplicate=True),
        Output('job_log-export-complete-judge-container', 'data'),
    ],
    Input('job_log-export', 'nClicks'),
    [
        State('job_log-job_name-input', 'value'),
        State('job_log-job_group-select', 'value'),
        State('job_log-status-select', 'value'),
        State('job_log-create_time-range', 'value'),
    ],
    running=[[Output('job_log-export', 'loading'), True, False]],
    prevent_initial_call=True,
)
def export_job_log_list(
    export_click, job_name, job_group, status_select, create_time_range
):
    """
    导出定时任务调度日志信息回调
    """
    if export_click:
        begin_time = None
        end_time = None
        if create_time_range:
            begin_time = create_time_range[0]
            end_time = create_time_range[1]
        export_params = dict(
            job_name=job_name,
            job_group=job_group,
            status=status_select,
            begin_time=begin_time,
            end_time=end_time,
        )
        export_job_log_res = JobLogApi.export_job_log(export_params)
        export_job_log = export_job_log_res.content
        MessageManager.success(content='导出成功')

        return [
            dcc.send_bytes(
                export_job_log,
                f'任务执行日志信息_{time.strftime("%Y%m%d%H%M%S", time.localtime())}.xlsx',
            ),
            {'timestamp': time.time()},
        ]

    raise PreventUpdate


@app.callback(
    Output('job_log-export-container', 'data', allow_duplicate=True),
    Input('job_log-export-complete-judge-container', 'data'),
    prevent_initial_call=True,
)
def reset_job_log_export_status(data):
    """
    导出完成后重置下载组件数据回调，防止重复下载文件
    """
    time.sleep(0.5)
    if data:
        return None

    raise PreventUpdate
