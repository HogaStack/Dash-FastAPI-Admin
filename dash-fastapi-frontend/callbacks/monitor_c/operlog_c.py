import time
from dash import ctx, dcc
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
from typing import Dict
from api.monitor.operlog import OperlogApi
from server import app
from utils.dict_util import DictManager
from utils.feedback_util import MessageManager
from utils.permission_util import PermissionManager
from utils.time_format_util import TimeFormatUtil


def generate_operlog_table(query_params: Dict):
    """
    根据查询参数获取操作日志表格数据及分页信息

    :param query_params: 查询参数
    :return: 操作日志表格数据及分页信息
    """
    table_info = OperlogApi.list_operlog(query_params)
    if table_info['code'] == 200:
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
                dict_type='sys_common_status', dict_value=item.get('status')
            )
            item['business_type_tag'] = DictManager.get_dict_tag(
                dict_type='sys_oper_type',
                dict_value=item.get('business_type'),
            )
            item['oper_time'] = TimeFormatUtil.format_time(
                item.get('oper_time')
            )
            item['key'] = str(item['oper_id'])
            item['cost_time'] = f'{item["cost_time"]}毫秒'
            item['operation'] = [
                {'content': '详情', 'type': 'link', 'icon': 'antd-eye'}
                if PermissionManager.check_perms('monitor:operlog:query')
                else {},
            ]

    return [table_data, table_pagination]


@app.callback(
    output=dict(
        operation_log_table_data=Output(
            'operation_log-list-table', 'data', allow_duplicate=True
        ),
        operation_log_table_pagination=Output(
            'operation_log-list-table', 'pagination', allow_duplicate=True
        ),
        operation_log_table_selectedrowkeys=Output(
            'operation_log-list-table', 'selectedRowKeys'
        ),
    ),
    inputs=dict(
        search_click=Input('operation_log-search', 'nClicks'),
        refresh_click=Input('operation_log-refresh', 'nClicks'),
        sorter=Input('operation_log-list-table', 'sorter'),
        pagination=Input('operation_log-list-table', 'pagination'),
        operations=Input('operation_log-operations-store', 'data'),
    ),
    state=dict(
        title=State('operation_log-title-input', 'value'),
        oper_name=State('operation_log-oper_name-input', 'value'),
        business_type=State('operation_log-business_type-select', 'value'),
        status_select=State('operation_log-status-select', 'value'),
        oper_time_range=State('operation_log-oper_time-range', 'value'),
    ),
    prevent_initial_call=True,
)
def get_operation_log_table_data(
    search_click,
    refresh_click,
    sorter,
    pagination,
    operations,
    title,
    oper_name,
    business_type,
    status_select,
    oper_time_range,
):
    """
    获取操作日志表格数据回调（进行表格相关增删查改操作后均会触发此回调）
    """

    begin_time = None
    end_time = None
    if oper_time_range:
        begin_time = oper_time_range[0]
        end_time = oper_time_range[1]
    query_params = dict(
        title=title,
        oper_name=oper_name,
        business_type=business_type,
        status=status_select,
        begin_time=begin_time,
        end_time=end_time,
        order_by_column=sorter.get('columns')[0] if sorter else None,
        is_asc=f'{sorter.get("orders")[0]}ing' if sorter else None,
        page_num=1,
        page_size=10,
    )
    triggered_prop = ctx.triggered[0].get('prop_id')
    if triggered_prop == 'operation_log-list-table.pagination':
        query_params.update(
            {
                'page_num': pagination['current'],
                'page_size': pagination['pageSize'],
            }
        )
    if search_click or refresh_click or pagination or operations:
        table_data, table_pagination = generate_operlog_table(query_params)
        return dict(
            operation_log_table_data=table_data,
            operation_log_table_pagination=table_pagination,
            operation_log_table_selectedrowkeys=None,
        )

    raise PreventUpdate


# 重置操作日志搜索表单数据回调
app.clientside_callback(
    """
    (reset_click) => {
        if (reset_click) {
            return [null, null, null, null, null, {'type': 'reset'}]
        }
        throw window.dash_clientside.PreventUpdate;
    }
    """,
    [
        Output('operation_log-title-input', 'value'),
        Output('operation_log-oper_name-input', 'value'),
        Output('operation_log-business_type-select', 'value'),
        Output('operation_log-status-select', 'value'),
        Output('operation_log-oper_time-range', 'value'),
        Output('operation_log-operations-store', 'data'),
    ],
    Input('operation_log-reset', 'nClicks'),
    prevent_initial_call=True,
)


# 隐藏/显示操作日志搜索表单回调
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
        Output('operation_log-search-form-container', 'hidden'),
        Output('operation_log-hidden-tooltip', 'title'),
    ],
    Input('operation_log-hidden', 'nClicks'),
    State('operation_log-search-form-container', 'hidden'),
    prevent_initial_call=True,
)


@app.callback(
    output=dict(
        modal_visible=Output(
            'operation_log-modal', 'visible', allow_duplicate=True
        ),
        modal_title=Output('operation_log-modal', 'title'),
        form_value=Output(
            {'type': 'operation_log-form-value', 'index': ALL}, 'children'
        ),
    ),
    inputs=dict(
        button_click=Input('operation_log-list-table', 'nClicksButton')
    ),
    state=dict(
        clicked_content=State('operation_log-list-table', 'clickedContent'),
        recently_button_clicked_row=State(
            'operation_log-list-table', 'recentlyButtonClickedRow'
        ),
    ),
    prevent_initial_call=True,
)
def add_edit_operation_log_modal(
    button_click, clicked_content, recently_button_clicked_row
):
    """
    显示操作日志详情弹窗回调
    """
    if button_click:
        # 获取所有输出表单项对应value的index
        form_value_list = [x['id']['index'] for x in ctx.outputs_list[-1]]
        operation_log_info = recently_button_clicked_row
        oper_name = (
            operation_log_info.get('oper_name')
            if operation_log_info.get('oper_name')
            else ''
        )
        oper_ip = (
            operation_log_info.get('oper_ip')
            if operation_log_info.get('oper_ip')
            else ''
        )
        oper_location = (
            operation_log_info.get('oper_location')
            if operation_log_info.get('oper_location')
            else ''
        )
        operation_log_info['login_info'] = (
            f'{oper_name} / {oper_ip} / {oper_location}'
        )
        operation_log_info['status'] = DictManager.get_dict_label(
            dict_type='sys_common_status',
            dict_value=operation_log_info.get('status'),
        )
        return dict(
            modal_visible=True,
            modal_title='操作日志详情',
            form_value=[operation_log_info.get(k) for k in form_value_list],
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
    Output(
        {'type': 'operation_log-operation-button', 'index': 'delete'},
        'disabled',
    ),
    Input('operation_log-list-table', 'selectedRowKeys'),
    prevent_initial_call=True,
)


@app.callback(
    [
        Output('operation_log-delete-text', 'children'),
        Output('operation_log-delete-confirm-modal', 'visible'),
        Output('operation_log-delete-ids-store', 'data'),
    ],
    Input({'type': 'operation_log-operation-button', 'index': ALL}, 'nClicks'),
    State('operation_log-list-table', 'selectedRowKeys'),
    prevent_initial_call=True,
)
def operation_log_delete_modal(operation_click, selected_row_keys):
    """
    显示删除或清空操作日志二次确认弹窗回调
    """
    trigger_id = ctx.triggered_id
    if trigger_id.index in ['delete', 'clear']:
        if trigger_id.index == 'delete':
            oper_ids = ','.join(selected_row_keys)

            return [
                f'是否确认删除日志编号为{oper_ids}的操作日志？',
                True,
                {'oper_type': 'delete', 'oper_ids': oper_ids},
            ]

        elif trigger_id.index == 'clear':
            return [
                '是否确认清除所有的操作日志？',
                True,
                {'oper_type': 'clear'},
            ]

    raise PreventUpdate


@app.callback(
    Output('operation_log-operations-store', 'data', allow_duplicate=True),
    Input('operation_log-delete-confirm-modal', 'okCounts'),
    State('operation_log-delete-ids-store', 'data'),
    prevent_initial_call=True,
)
def operation_log_delete_confirm(delete_confirm, oper_ids_data):
    """
    删除或清空操作日志弹窗确认回调，实现删除或清空操作
    """
    if delete_confirm:
        oper_type = oper_ids_data.get('oper_type')
        if oper_type == 'clear':
            OperlogApi.clean_operlog()
            MessageManager.success(content='清除成功')

            return {'type': 'clear'}
        else:
            params = oper_ids_data.get('oper_ids')
            OperlogApi.del_operlog(params)
            MessageManager.success(content='删除成功')

            return {'type': 'delete'}

    raise PreventUpdate


@app.callback(
    [
        Output('operation_log-export-container', 'data', allow_duplicate=True),
        Output('operation_log-export-complete-judge-container', 'data'),
    ],
    Input('operation_log-export', 'nClicks'),
    [
        State('operation_log-list-table', 'sorter'),
        State('operation_log-title-input', 'value'),
        State('operation_log-oper_name-input', 'value'),
        State('operation_log-business_type-select', 'value'),
        State('operation_log-status-select', 'value'),
        State('operation_log-oper_time-range', 'value'),
    ],
    running=[[Output('operation_log-export', 'loading'), True, False]],
    prevent_initial_call=True,
)
def export_operation_log_list(
    export_click,
    sorter,
    title,
    oper_name,
    business_type,
    status_select,
    oper_time_range,
):
    """
    导出操作日志信息回调
    """
    if export_click:
        begin_time = None
        end_time = None
        if oper_time_range:
            begin_time = oper_time_range[0]
            end_time = oper_time_range[1]
        export_params = dict(
            title=title,
            oper_name=oper_name,
            business_type=business_type,
            status=status_select,
            begin_time=begin_time,
            end_time=end_time,
            order_by_column=sorter.get('columns')[0] if sorter else None,
            is_asc=f'{sorter.get("orders")[0]}ing' if sorter else None,
        )
        export_operation_log_res = OperlogApi.export_operlog(export_params)
        export_operation_log = export_operation_log_res.content
        MessageManager.success(content='导出成功')

        return [
            dcc.send_bytes(
                export_operation_log,
                f'操作日志信息_{time.strftime("%Y%m%d%H%M%S", time.localtime())}.xlsx',
            ),
            {'timestamp': time.time()},
        ]

    raise PreventUpdate


@app.callback(
    Output('operation_log-export-container', 'data', allow_duplicate=True),
    Input('operation_log-export-complete-judge-container', 'data'),
    prevent_initial_call=True,
)
def reset_operation_log_export_status(data):
    """
    导出完成后重置下载组件数据回调，防止重复下载文件
    """
    time.sleep(0.5)
    if data:
        return None

    raise PreventUpdate
