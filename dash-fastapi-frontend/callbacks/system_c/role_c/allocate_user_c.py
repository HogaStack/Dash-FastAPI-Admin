from dash import ctx, no_update
from dash.dependencies import ALL, Input, MATCH, Output, State
from dash.exceptions import PreventUpdate
from api.system.role import RoleApi
from server import app
from utils.feedback_util import MessageManager
from utils.permission_util import PermissionManager
from utils.time_format_util import TimeFormatUtil


@app.callback(
    [
        Output(
            {'type': 'allocate_user-list-table', 'index': MATCH},
            'data',
            allow_duplicate=True,
        ),
        Output(
            {'type': 'allocate_user-list-table', 'index': MATCH},
            'pagination',
            allow_duplicate=True,
        ),
        Output(
            {'type': 'allocate_user-list-table', 'index': MATCH},
            'selectedRowKeys',
        ),
    ],
    [
        Input({'type': 'allocate_user-search', 'index': MATCH}, 'nClicks'),
        Input({'type': 'allocate_user-refresh', 'index': MATCH}, 'nClicks'),
        Input(
            {'type': 'allocate_user-list-table', 'index': MATCH}, 'pagination'
        ),
        Input(
            {'type': 'allocate_user-operations-container', 'index': MATCH},
            'data',
        ),
    ],
    [
        State(
            {'type': 'allocate_user-user_name-input', 'index': MATCH}, 'value'
        ),
        State(
            {'type': 'allocate_user-phonenumber-input', 'index': MATCH}, 'value'
        ),
        State('allocate_user-role_id-container', 'data'),
    ],
    prevent_initial_call=True,
)
def get_allocate_user_table_data(
    search_click,
    refresh_click,
    pagination,
    operations,
    user_name,
    phonenumber,
    role_id,
):
    """
    使用模式匹配回调MATCH模式，根据不同类型获取角色已分配用户列表及未分配用户列表（进行表格相关增删查改操作后均会触发此回调）
    """

    query_params = dict(
        role_id=int(role_id),
        user_name=user_name,
        phonenumber=phonenumber,
        page_num=1,
        page_size=10,
    )
    triggered_id = ctx.triggered_id
    if triggered_id.type == 'allocate_user-list-table':
        query_params.update(
            {
                'page_num': pagination['current'],
                'page_size': pagination['pageSize'],
            }
        )
    if search_click or refresh_click or pagination or operations:
        table_info = {}
        if triggered_id.index == 'allocated':
            table_info = RoleApi.allocated_user_list(query_params)
        if triggered_id.index == 'unallocated':
            table_info = RoleApi.unallocated_user_list(query_params)
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
            if item['status'] == '0':
                item['status'] = dict(tag='正常', color='blue')
            else:
                item['status'] = dict(tag='停用', color='volcano')
            item['create_time'] = TimeFormatUtil.format_time(
                item.get('create_time')
            )
            item['key'] = str(item['user_id'])
            if triggered_id.index == 'allocated':
                item['operation'] = [
                    {
                        'content': '取消授权',
                        'type': 'link',
                        'icon': 'antd-close-circle',
                    }
                    if PermissionManager.check_perms('system:role:remove')
                    else {},
                ]

        return [table_data, table_pagination, None]

    raise PreventUpdate


# 重置分配用户搜索表单数据回调
app.clientside_callback(
    """
    (reset_click) => {
        if (reset_click) {
            return [null, null, {'type': 'reset'}]
        }
        throw window.dash_clientside.PreventUpdate;
    }
    """,
    [
        Output(
            {'type': 'allocate_user-user_name-input', 'index': MATCH}, 'value'
        ),
        Output(
            {'type': 'allocate_user-phonenumber-input', 'index': MATCH}, 'value'
        ),
        Output(
            {'type': 'allocate_user-operations-container', 'index': MATCH},
            'data',
        ),
    ],
    Input({'type': 'allocate_user-reset', 'index': MATCH}, 'nClicks'),
    prevent_initial_call=True,
)


# 隐藏/显示分配用户搜索表单回调
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
        Output(
            {'type': 'allocate_user-search-form-container', 'index': MATCH},
            'hidden',
        ),
        Output(
            {'type': 'allocate_user-hidden-tooltip', 'index': MATCH}, 'title'
        ),
    ],
    Input({'type': 'allocate_user-hidden', 'index': MATCH}, 'nClicks'),
    State(
        {'type': 'allocate_user-search-form-container', 'index': MATCH},
        'hidden',
    ),
    prevent_initial_call=True,
)


@app.callback(
    Output(
        {'type': 'allocate_user-operation-button', 'index': 'delete'},
        'disabled',
    ),
    Input(
        {'type': 'allocate_user-list-table', 'index': 'allocated'},
        'selectedRowKeys',
    ),
    prevent_initial_call=True,
)
def change_allocated_user_delete_button_status(table_rows_selected):
    """
    根据选择的表格数据行数控制取批量消授权按钮状态回调
    """
    outputs_list = ctx.outputs_list
    if outputs_list:
        if table_rows_selected:
            return False

        return True

    raise PreventUpdate


@app.callback(
    [
        Output('allocate_user-modal', 'visible'),
        Output(
            {'type': 'allocate_user-search', 'index': 'unallocated'}, 'nClicks'
        ),
    ],
    Input('allocate_user-add', 'nClicks'),
    State({'type': 'allocate_user-search', 'index': 'unallocated'}, 'nClicks'),
    prevent_initial_call=True,
)
def allocate_user_modal(add_click, unallocated_user):
    """
    分配用户弹框中添加用户按钮回调
    """
    if add_click:
        return [True, unallocated_user + 1 if unallocated_user else 1]

    raise PreventUpdate


@app.callback(
    [
        Output(
            {
                'type': 'allocate_user-operations-container',
                'index': 'allocated',
            },
            'data',
            allow_duplicate=True,
        ),
        Output(
            {
                'type': 'allocate_user-operations-container',
                'index': 'unallocated',
            },
            'data',
            allow_duplicate=True,
        ),
    ],
    Input('allocate_user-modal', 'okCounts'),
    [
        State(
            {'type': 'allocate_user-list-table', 'index': 'unallocated'},
            'selectedRowKeys',
        ),
        State('allocate_user-role_id-container', 'data'),
    ],
    running=[[Output('allocate_user-modal', 'confirmLoading'), True, False]],
    prevent_initial_call=True,
)
def allocate_user_add_confirm(add_confirm, selected_row_keys, role_id):
    """
    添加用户确认回调，实现给角色分配用户操作
    """
    if add_confirm:
        if selected_row_keys:
            params = {
                'user_ids': ','.join(selected_row_keys),
                'role_id': int(role_id),
            }
            RoleApi.auth_user_select_all(params)
            MessageManager.success(content='授权成功')

            return [
                {'type': 'add'},
                {'type': 'add'},
            ]

        MessageManager.error(content='请选择用户')
        return [
            no_update,
            no_update,
        ]

    raise PreventUpdate


@app.callback(
    [
        Output('allocate_user-delete-text', 'children'),
        Output('allocate_user-delete-confirm-modal', 'visible'),
        Output('allocate_user-delete-ids-store', 'data'),
    ],
    [
        Input(
            {'type': 'allocate_user-operation-button', 'index': ALL}, 'nClicks'
        ),
        Input(
            {'type': 'allocate_user-list-table', 'index': 'allocated'},
            'nClicksButton',
        ),
    ],
    [
        State(
            {'type': 'allocate_user-list-table', 'index': 'allocated'},
            'selectedRowKeys',
        ),
        State(
            {'type': 'allocate_user-list-table', 'index': 'allocated'},
            'clickedContent',
        ),
        State(
            {'type': 'allocate_user-list-table', 'index': 'allocated'},
            'recentlyButtonClickedRow',
        ),
    ],
    prevent_initial_call=True,
)
def allocate_user_delete_modal(
    operation_click,
    button_click,
    selected_row_keys,
    clicked_content,
    recently_button_clicked_row,
):
    """
    显示取消授权二次确认弹窗回调
    """
    trigger_id = ctx.triggered_id
    if trigger_id.type == 'allocate_user-operation-button' or (
        trigger_id.type == 'allocate_user-list-table'
        and clicked_content == '取消授权'
    ):
        if trigger_id.type == 'allocate_user-operation-button':
            user_ids = ','.join(selected_row_keys)
            oper = {'oper_type': 'clear', 'user_ids': user_ids}
        else:
            if clicked_content == '取消授权':
                user_ids = recently_button_clicked_row['key']
                oper = {'oper_type': 'delete', 'user_ids': user_ids}
            else:
                return no_update

        return [f'是否确认取消用户id为{user_ids}的授权？', True, oper]

    raise PreventUpdate


@app.callback(
    Output(
        {
            'type': 'allocate_user-operations-container',
            'index': 'allocated',
        },
        'data',
        allow_duplicate=True,
    ),
    Input('allocate_user-delete-confirm-modal', 'okCounts'),
    [
        State('allocate_user-delete-ids-store', 'data'),
        State('allocate_user-role_id-container', 'data'),
    ],
    prevent_initial_call=True,
)
def allocate_user_delete_confirm(delete_confirm, user_ids_data, role_id):
    """
    取消授权弹窗确认回调，实现取消授权操作
    """
    if delete_confirm:
        oper_type = user_ids_data.get('oper_type')
        user_ids = user_ids_data.get('user_ids')
        if oper_type == 'clear':
            params = {'user_ids': user_ids, 'role_id': int(role_id)}
            RoleApi.auth_user_cancel_all(params)
            MessageManager.success(content='取消授权成功')

            return {'type': 'clear'}
        else:
            params = {'user_id': int(user_ids), 'role_id': int(role_id)}
            RoleApi.auth_user_cancel(params)
            MessageManager.success(content='取消授权成功')

            return {'type': 'delete'}

    raise PreventUpdate
