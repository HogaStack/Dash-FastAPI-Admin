import time
from dash import ctx, dcc, no_update
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
from typing import Dict
from api.monitor.logininfor import LogininforApi
from server import app
from utils.dict_util import DictManager
from utils.feedback_util import MessageManager
from utils.time_format_util import TimeFormatUtil


def generate_logininfor_table(query_params: Dict):
    """
    根据查询参数获取登录日志表格数据及分页信息

    :param query_params: 查询参数
    :return: 登录日志表格数据及分页信息
    """
    table_info = LogininforApi.list_logininfor(query_params)
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
        item['login_time'] = TimeFormatUtil.format_time(item.get('login_time'))
        item['key'] = str(item['info_id'])

    return [table_data, table_pagination]


@app.callback(
    output=dict(
        login_log_table_data=Output(
            'login_log-list-table', 'data', allow_duplicate=True
        ),
        login_log_table_pagination=Output(
            'login_log-list-table', 'pagination', allow_duplicate=True
        ),
        login_log_table_selectedrowkeys=Output(
            'login_log-list-table', 'selectedRowKeys'
        ),
    ),
    inputs=dict(
        search_click=Input('login_log-search', 'nClicks'),
        refresh_click=Input('login_log-refresh', 'nClicks'),
        sorter=Input('login_log-list-table', 'sorter'),
        pagination=Input('login_log-list-table', 'pagination'),
        operations=Input('login_log-operations-store', 'data'),
    ),
    state=dict(
        ipaddr=State('login_log-ipaddr-input', 'value'),
        user_name=State('login_log-user_name-input', 'value'),
        status_select=State('login_log-status-select', 'value'),
        login_time_range=State('login_log-login_time-range', 'value'),
    ),
    prevent_initial_call=True,
)
def get_login_log_table_data(
    search_click,
    refresh_click,
    sorter,
    pagination,
    operations,
    ipaddr,
    user_name,
    status_select,
    login_time_range,
):
    """
    获取登录日志表格数据回调（进行表格相关增删查改操作后均会触发此回调）
    """

    begin_time = None
    end_time = None
    if login_time_range:
        begin_time = login_time_range[0]
        end_time = login_time_range[1]
    query_params = dict(
        ipaddr=ipaddr,
        user_name=user_name,
        status=status_select,
        begin_time=begin_time,
        end_time=end_time,
        order_by_column=sorter.get('columns')[0] if sorter else None,
        is_asc=f'{sorter.get("orders")[0]}ing' if sorter else None,
        page_num=1,
        page_size=10,
    )
    triggered_prop = ctx.triggered[0].get('prop_id')
    if triggered_prop == 'login_log-list-table.pagination':
        query_params.update(
            {
                'page_num': pagination['current'],
                'page_size': pagination['pageSize'],
            }
        )
    if search_click or refresh_click or pagination or operations:
        table_data, table_pagination = generate_logininfor_table(query_params)
        return dict(
            login_log_table_data=table_data,
            login_log_table_pagination=table_pagination,
            login_log_table_selectedrowkeys=None,
        )

    raise PreventUpdate


# 重置登录日志搜索表单数据回调
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
        Output('login_log-ipaddr-input', 'value'),
        Output('login_log-user_name-input', 'value'),
        Output('login_log-status-select', 'value'),
        Output('login_log-login_time-range', 'value'),
        Output('login_log-operations-store', 'data'),
    ],
    Input('login_log-reset', 'nClicks'),
    prevent_initial_call=True,
)


# 隐藏/显示登录日志搜索表单回调
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
        Output('login_log-search-form-container', 'hidden'),
        Output('login_log-hidden-tooltip', 'title'),
    ],
    Input('login_log-hidden', 'nClicks'),
    State('login_log-search-form-container', 'hidden'),
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
    Output(
        {'type': 'login_log-operation-button', 'index': 'delete'}, 'disabled'
    ),
    Input('login_log-list-table', 'selectedRowKeys'),
    prevent_initial_call=True,
)


# 根据选择的表格数据行数控制解锁按钮状态回调
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
    Output('login_log-unlock', 'disabled'),
    Input('login_log-list-table', 'selectedRowKeys'),
    prevent_initial_call=True,
)


@app.callback(
    [
        Output('login_log-delete-text', 'children'),
        Output('login_log-delete-confirm-modal', 'visible'),
        Output('login_log-delete-ids-store', 'data'),
    ],
    Input({'type': 'login_log-operation-button', 'index': ALL}, 'nClicks'),
    State('login_log-list-table', 'selectedRowKeys'),
    prevent_initial_call=True,
)
def login_log_delete_modal(operation_click, selected_row_keys):
    """
    显示删除或清空登录日志二次确认弹窗回调
    """
    trigger_id = ctx.triggered_id
    if trigger_id.index in ['delete', 'clear']:
        if trigger_id.index == 'delete':
            info_ids = ','.join(selected_row_keys)

            return [
                f'是否确认删除访问编号为{info_ids}的登录日志？',
                True,
                {'oper_type': 'delete', 'info_ids': info_ids},
            ]

        elif trigger_id.index == 'clear':
            return [
                '是否确认清除所有的登录日志？',
                True,
                {'oper_type': 'clear'},
            ]

    raise PreventUpdate


@app.callback(
    Output('login_log-operations-store', 'data', allow_duplicate=True),
    Input('login_log-delete-confirm-modal', 'okCounts'),
    State('login_log-delete-ids-store', 'data'),
    prevent_initial_call=True,
)
def login_log_delete_confirm(delete_confirm, info_ids_data):
    """
    删除或清空登录日志弹窗确认回调，实现删除或清空操作
    """
    if delete_confirm:
        oper_type = info_ids_data.get('oper_type')
        if oper_type == 'clear':
            LogininforApi.clean_logininfor()
            MessageManager.success(content='清除成功')

            return {'type': 'clear'}
        else:
            params = info_ids_data.get('info_ids')
            LogininforApi.del_logininfor(params)
            MessageManager.success(content='删除成功')

            return {'type': 'delete'}

    raise PreventUpdate


@app.callback(
    [
        Output('login_log-export-container', 'data', allow_duplicate=True),
        Output('login_log-export-complete-judge-container', 'data'),
    ],
    Input('login_log-export', 'nClicks'),
    [
        State('login_log-list-table', 'sorter'),
        State('login_log-ipaddr-input', 'value'),
        State('login_log-user_name-input', 'value'),
        State('login_log-status-select', 'value'),
        State('login_log-login_time-range', 'value'),
    ],
    running=[[Output('login_log-export', 'loading'), True, False]],
    prevent_initial_call=True,
)
def export_login_log_list(
    export_click, sorter, ipaddr, user_name, status_select, login_time_range
):
    """
    导出登录日志信息回调
    """
    if export_click:
        begin_time = None
        end_time = None
        if login_time_range:
            begin_time = login_time_range[0]
            end_time = login_time_range[1]
        export_params = dict(
            ipaddr=ipaddr,
            user_name=user_name,
            status=status_select,
            begin_time=begin_time,
            end_time=end_time,
            order_by_column=sorter.get('columns')[0] if sorter else None,
            is_asc=f'{sorter.get("orders")[0]}ing' if sorter else None,
        )
        export_login_log_res = LogininforApi.export_logininfor(export_params)
        export_login_log = export_login_log_res.content
        MessageManager.success(content='导出成功')

        return [
            dcc.send_bytes(
                export_login_log,
                f'登录日志信息_{time.strftime("%Y%m%d%H%M%S", time.localtime())}.xlsx',
            ),
            {'timestamp': time.time()},
        ]

    raise PreventUpdate


@app.callback(
    Output('login_log-export-container', 'data', allow_duplicate=True),
    Input('login_log-export-complete-judge-container', 'data'),
    prevent_initial_call=True,
)
def reset_login_log_export_status(data):
    """
    导出完成后重置下载组件数据回调，防止重复下载文件
    """
    time.sleep(0.5)
    if data:
        return None

    raise PreventUpdate


@app.callback(
    Output('login_log-unlock', 'nClicks'),
    Input('login_log-unlock', 'nClicks'),
    State('login_log-list-table', 'selectedRows'),
    prevent_initial_call=True,
)
def unlock_user(unlock_click, selected_rows):
    """
    解锁用户回调
    """
    if unlock_click:
        user_name = selected_rows[0].get('user_name')
        LogininforApi.unlock_logininfor(user_name=user_name)
        MessageManager.success(content='解锁成功')

        return no_update

    raise PreventUpdate
