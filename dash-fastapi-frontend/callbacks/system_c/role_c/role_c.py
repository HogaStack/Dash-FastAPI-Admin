import feffery_antd_components as fac
import time
import uuid
from dash import ctx, dcc, no_update
from dash.dependencies import ALL, Input, Output, State
from dash.exceptions import PreventUpdate
from typing import Dict
from api.system.menu import MenuApi
from api.system.role import RoleApi
from config.constant import SysNormalDisableConstant
from server import app
from utils.common_util import ValidateUtil
from utils.feedback_util import MessageManager
from utils.permission_util import PermissionManager
from utils.time_format_util import TimeFormatUtil
from utils.tree_util import TreeUtil


def generate_role_table(query_params: Dict):
    """
    根据查询参数获取角色表格数据及分页信息

    :param query_params: 查询参数
    :return: 角色表格数据及分页信息
    """
    table_info = RoleApi.list_role(query_params)
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
        if item['status'] == SysNormalDisableConstant.NORMAL:
            item['status'] = dict(checked=True, disabled=item['role_id'] == 1)
        else:
            item['status'] = dict(checked=False, disabled=item['role_id'] == 1)
        item['create_time'] = TimeFormatUtil.format_time(
            item.get('create_time')
        )
        item['key'] = str(item['role_id'])
        if item['role_id'] == 1:
            item['operation'] = []
        else:
            item['operation'] = fac.AntdSpace(
                [
                    fac.AntdButton(
                        '修改',
                        id={
                            'type': 'role-operation-table',
                            'operation': 'edit',
                            'index': str(item['role_id']),
                        },
                        type='link',
                        icon=fac.AntdIcon(icon='antd-edit'),
                        style={'padding': 0},
                    )
                    if PermissionManager.check_perms('system:role:edit')
                    else [],
                    fac.AntdButton(
                        '删除',
                        id={
                            'type': 'role-operation-table',
                            'operation': 'delete',
                            'index': str(item['role_id']),
                        },
                        type='link',
                        icon=fac.AntdIcon(icon='antd-delete'),
                        style={'padding': 0},
                    )
                    if PermissionManager.check_perms('system:role:remove')
                    else [],
                    fac.AntdPopover(
                        fac.AntdButton(
                            '更多',
                            type='link',
                            icon=fac.AntdIcon(icon='antd-more'),
                            style={'padding': 0},
                        ),
                        content=fac.AntdSpace(
                            [
                                fac.AntdButton(
                                    '数据权限',
                                    id={
                                        'type': 'role-operation-table',
                                        'operation': 'datascope',
                                        'index': str(item['role_id']),
                                    },
                                    type='text',
                                    block=True,
                                    icon=fac.AntdIcon(icon='antd-check-circle'),
                                    style={'padding': 0},
                                ),
                                fac.AntdButton(
                                    '分配用户',
                                    id={
                                        'type': 'role-operation-table',
                                        'operation': 'allocation',
                                        'index': str(item['role_id']),
                                    },
                                    type='text',
                                    block=True,
                                    icon=fac.AntdIcon(icon='antd-user'),
                                    style={'padding': 0},
                                ),
                            ],
                            direction='vertical',
                        ),
                        placement='bottomRight',
                    )
                    if PermissionManager.check_perms('system:role:edit')
                    else [],
                ]
            )

    return [table_data, table_pagination]


@app.callback(
    output=dict(
        role_table_data=Output('role-list-table', 'data', allow_duplicate=True),
        role_table_pagination=Output(
            'role-list-table', 'pagination', allow_duplicate=True
        ),
        role_table_selectedrowkeys=Output('role-list-table', 'selectedRowKeys'),
    ),
    inputs=dict(
        search_click=Input('role-search', 'nClicks'),
        refresh_click=Input('role-refresh', 'nClicks'),
        pagination=Input('role-list-table', 'pagination'),
        operations=Input('role-operations-store', 'data'),
    ),
    state=dict(
        role_name=State('role-role_name-input', 'value'),
        role_key=State('role-role_key-input', 'value'),
        status_select=State('role-status-select', 'value'),
        create_time_range=State('role-create_time-range', 'value'),
    ),
    prevent_initial_call=True,
)
def get_role_table_data(
    search_click,
    refresh_click,
    pagination,
    operations,
    role_name,
    role_key,
    status_select,
    create_time_range,
):
    """
    获取角色表格数据回调（进行表格相关增删查改操作后均会触发此回调）
    """

    begin_time = None
    end_time = None
    if create_time_range:
        begin_time = create_time_range[0]
        end_time = create_time_range[1]
    query_params = dict(
        role_name=role_name,
        role_key=role_key,
        status=status_select,
        begin_time=begin_time,
        end_time=end_time,
        page_num=1,
        page_size=10,
    )
    triggered_id = ctx.triggered_id
    if triggered_id == 'role-list-table':
        query_params.update(
            {
                'page_num': pagination['current'],
                'page_size': pagination['pageSize'],
            }
        )
    if search_click or refresh_click or pagination or operations:
        table_data, table_pagination = generate_role_table(query_params)
        return dict(
            role_table_data=table_data,
            role_table_pagination=table_pagination,
            role_table_selectedrowkeys=None,
        )

    raise PreventUpdate


# 重置角色搜索表单数据回调
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
        Output('role-role_name-input', 'value'),
        Output('role-role_key-input', 'value'),
        Output('role-status-select', 'value'),
        Output('role-create_time-range', 'value'),
        Output('role-operations-store', 'data'),
    ],
    Input('role-reset', 'nClicks'),
    prevent_initial_call=True,
)


# 隐藏/显示角色搜索表单回调
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
        Output('role-search-form-container', 'hidden'),
        Output('role-hidden-tooltip', 'title'),
    ],
    Input('role-hidden', 'nClicks'),
    State('role-search-form-container', 'hidden'),
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
    Output({'type': 'role-operation-button', 'operation': 'edit'}, 'disabled'),
    Input('role-list-table', 'selectedRowKeys'),
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
        {'type': 'role-operation-button', 'operation': 'delete'}, 'disabled'
    ),
    Input('role-list-table', 'selectedRowKeys'),
    prevent_initial_call=True,
)


@app.callback(
    Output('role-menu-perms', 'expandedKeys'),
    Input('role-menu-perms-radio-fold-unfold', 'checked'),
    State('role-menu-perms', 'treeData'),
    prevent_initial_call=True,
)
def fold_unfold_role_menu(fold_unfold, menu_tree):
    """
    新增和编辑表单中展开/折叠checkbox回调
    """
    if menu_tree and fold_unfold is not None:
        expanded_keys = [menu.get('key') for menu in menu_tree]
        if fold_unfold:
            return expanded_keys
        else:
            return []

    return no_update


@app.callback(
    Output('role-menu-perms', 'checkedKeys', allow_duplicate=True),
    Input('role-menu-perms-radio-all-none', 'checked'),
    State('role-menu-perms', 'treeData'),
    prevent_initial_call=True,
)
def all_none_role_menu_mode(all_none, menu_tree):
    """
    新增和编辑表单中全选/全不选checkbox回调
    """
    if menu_tree and all_none is not None:
        if all_none:
            all_keys = TreeUtil.find_tree_all_keys(menu_tree, [])
            return all_keys
        else:
            return []

    return no_update


@app.callback(
    [
        Output('role-menu-perms', 'checkStrictly'),
        Output('role-menu-perms', 'key', allow_duplicate=True),
    ],
    Input('role-menu-perms-radio-parent-children', 'checked'),
    prevent_initial_call=True,
)
def change_role_menu_mode(parent_children):
    """
    新增和编辑表单中父子联动checkbox回调
    """
    return [not parent_children, str(uuid.uuid4())]


@app.callback(
    output=dict(
        modal_visible=Output('role-modal', 'visible', allow_duplicate=True),
        modal_title=Output('role-modal', 'title'),
        form_value=Output(
            {'type': 'role-form-value', 'index': ALL, 'required': ALL}, 'value'
        ),
        form_label_validate_status=Output(
            {'type': 'role-form-label', 'index': ALL, 'required': True},
            'validateStatus',
            allow_duplicate=True,
        ),
        form_label_validate_info=Output(
            {'type': 'role-form-label', 'index': ALL, 'required': True},
            'help',
            allow_duplicate=True,
        ),
        menu_perms_tree=Output('role-menu-perms', 'treeData'),
        menu_perms_checkedkeys=Output(
            'role-menu-perms', 'checkedKeys', allow_duplicate=True
        ),
        fold_unfold=Output('role-menu-perms-radio-fold-unfold', 'checked'),
        all_none=Output('role-menu-perms-radio-all-none', 'checked'),
        radio_parent_children=Output(
            'role-menu-perms-radio-parent-children', 'checked'
        ),
        edit_row_info=Output('role-edit-id-store', 'data'),
        modal_type=Output('role-modal_type-store', 'data'),
    ),
    inputs=dict(
        operation_click=Input(
            {'type': 'role-operation-button', 'operation': ALL}, 'nClicks'
        ),
        button_click=Input(
            {'type': 'role-operation-table', 'operation': ALL, 'index': ALL},
            'nClicks',
        ),
    ),
    state=dict(selected_row_keys=State('role-list-table', 'selectedRowKeys')),
    prevent_initial_call=True,
)
def add_edit_role_modal(operation_click, button_click, selected_row_keys):
    """
    显示新增或编辑角色弹窗回调
    """
    trigger_id = ctx.triggered_id
    if trigger_id.operation in ['add', 'edit']:
        # 获取所有输出表单项对应value的index
        form_value_list = [x['id']['index'] for x in ctx.outputs_list[2]]
        # 获取所有输出表单项对应label的index
        form_label_list = [x['id']['index'] for x in ctx.outputs_list[3]]
        if (
            trigger_id.type == 'role-operation-button'
            and trigger_id.operation == 'add'
        ):
            tree_info = MenuApi.treeselect()
            tree_data = tree_info['data']
            role_info = dict(
                role_name=None,
                role_key=None,
                role_sort=0,
                status=SysNormalDisableConstant.NORMAL,
                remark=None,
            )
            return dict(
                modal_visible=True,
                modal_title='新增角色',
                form_value=[role_info.get(k) for k in form_value_list],
                form_label_validate_status=[None] * len(form_label_list),
                form_label_validate_info=[None] * len(form_label_list),
                menu_perms_tree=tree_data,
                menu_perms_checkedkeys=None,
                fold_unfold=None,
                all_none=None,
                radio_parent_children=no_update,
                edit_row_info=None,
                modal_type={'type': 'add'},
            )
        elif trigger_id.operation == 'edit':
            if trigger_id.type == 'role-operation-button':
                role_id = int(','.join(selected_row_keys))
            else:
                role_id = int(trigger_id.index)
            role_info_res = RoleApi.get_role(role_id=role_id)
            tree_info = MenuApi.role_menu_treeselect(role_id=role_id)
            role_info = role_info_res['data']
            menu_check_strictly = role_info['menu_check_strictly']
            tree_data = tree_info['menus']
            checked_keys = [str(item) for item in tree_info['checked_keys']]
            return dict(
                modal_visible=True,
                modal_title='编辑角色',
                form_value=[role_info.get(k) for k in form_value_list],
                form_label_validate_status=[None] * len(form_label_list),
                form_label_validate_info=[None] * len(form_label_list),
                menu_perms_tree=tree_data,
                menu_perms_checkedkeys=checked_keys,
                fold_unfold=None,
                all_none=None,
                radio_parent_children=menu_check_strictly,
                edit_row_info=role_info if role_info else None,
                modal_type={'type': 'edit'},
            )

        return dict(
            modal_visible=no_update,
            modal_title=no_update,
            form_value=[no_update] * len(form_value_list),
            form_label_validate_status=[no_update] * len(form_value_list),
            form_label_validate_info=[no_update] * len(form_value_list),
            menu_perms_tree=no_update,
            menu_perms_checkedkeys=no_update,
            fold_unfold=no_update,
            all_none=no_update,
            radio_parent_children=no_update,
            edit_row_info=None,
            modal_type=None,
        )

    raise PreventUpdate


@app.callback(
    output=dict(
        form_label_validate_status=Output(
            {'type': 'role-form-label', 'index': ALL, 'required': True},
            'validateStatus',
            allow_duplicate=True,
        ),
        form_label_validate_info=Output(
            {'type': 'role-form-label', 'index': ALL, 'required': True},
            'help',
            allow_duplicate=True,
        ),
        modal_visible=Output('role-modal', 'visible'),
        operations=Output(
            'role-operations-store', 'data', allow_duplicate=True
        ),
    ),
    inputs=dict(confirm_trigger=Input('role-modal', 'okCounts')),
    state=dict(
        modal_type=State('role-modal_type-store', 'data'),
        edit_row_info=State('role-edit-id-store', 'data'),
        form_value=State(
            {'type': 'role-form-value', 'index': ALL, 'required': ALL}, 'value'
        ),
        form_label=State(
            {'type': 'role-form-label', 'index': ALL, 'required': True},
            'label',
        ),
        menu_checked_keys=State('role-menu-perms', 'checkedKeys'),
        menu_half_checked_keys=State('role-menu-perms', 'halfCheckedKeys'),
        parent_checked=State(
            'role-menu-perms-radio-parent-children', 'checked'
        ),
    ),
    running=[[Output('role-modal', 'confirmLoading'), True, False]],
    prevent_initial_call=True,
)
def role_confirm(
    confirm_trigger,
    modal_type,
    edit_row_info,
    form_value,
    form_label,
    menu_checked_keys,
    menu_half_checked_keys,
    parent_checked,
):
    """
    新增或编辑角色弹窗确认回调，实现新增或编辑操作
    """
    if confirm_trigger:
        # 获取所有输出表单项对应label的index
        form_label_output_list = [x['id']['index'] for x in ctx.outputs_list[0]]
        # 获取所有输入表单项对应的value及label
        form_value_state = {
            x['id']['index']: x.get('value') for x in ctx.states_list[2]
        }
        form_label_state = {
            x['id']['index']: x.get('value') for x in ctx.states_list[3]
        }
        if all(
            ValidateUtil.not_empty(item)
            for item in [
                form_value_state.get(k) for k in form_label_output_list
            ]
        ):
            menu_half_checked_keys = (
                menu_half_checked_keys if menu_half_checked_keys else []
            )
            menu_checked_keys = menu_checked_keys if menu_checked_keys else []
            if parent_checked:
                menu_perms = menu_half_checked_keys + menu_checked_keys
            else:
                menu_perms = menu_checked_keys
            params_add = form_value_state
            params_add['menu_ids'] = (
                [int(item) for item in menu_perms] if menu_perms else []
            )
            params_add['menu_check_strictly'] = parent_checked
            params_edit = params_add.copy()
            params_edit['role_id'] = (
                edit_row_info.get('role_id') if edit_row_info else None
            )
            modal_type = modal_type.get('type')
            if modal_type == 'add':
                RoleApi.add_role(params_add)
            if modal_type == 'edit':
                RoleApi.update_role(params_edit)
            if modal_type == 'add':
                MessageManager.success(content='新增成功')

                return dict(
                    form_label_validate_status=[None]
                    * len(form_label_output_list),
                    form_label_validate_info=[None]
                    * len(form_label_output_list),
                    modal_visible=False,
                    operations={'type': 'add'},
                )
            if modal_type == 'edit':
                MessageManager.success(content='编辑成功')

                return dict(
                    form_label_validate_status=[None]
                    * len(form_label_output_list),
                    form_label_validate_info=[None]
                    * len(form_label_output_list),
                    modal_visible=False,
                    operations={'type': 'edit'},
                )

            return dict(
                form_label_validate_status=[None] * len(form_label_output_list),
                form_label_validate_info=[None] * len(form_label_output_list),
                modal_visible=no_update,
                operations=no_update,
            )

        return dict(
            form_label_validate_status=[
                None
                if ValidateUtil.not_empty(form_value_state.get(k))
                else 'error'
                for k in form_label_output_list
            ],
            form_label_validate_info=[
                None
                if ValidateUtil.not_empty(form_value_state.get(k))
                else f'{form_label_state.get(k)}不能为空!'
                for k in form_label_output_list
            ],
            modal_visible=no_update,
            operations=no_update,
        )

    raise PreventUpdate


@app.callback(
    Output('role-operations-store', 'data', allow_duplicate=True),
    [
        Input('role-list-table', 'recentlySwitchDataIndex'),
        Input('role-list-table', 'recentlySwitchStatus'),
        Input('role-list-table', 'recentlySwitchRow'),
    ],
    prevent_initial_call=True,
)
def table_switch_role_status(
    recently_switch_data_index, recently_switch_status, recently_switch_row
):
    """
    表格内切换角色状态回调
    """
    if recently_switch_data_index:
        RoleApi.change_role_status(
            role_id=int(recently_switch_row['key']),
            status='0' if recently_switch_status else '1',
        )
        MessageManager.success(content='修改成功')

        return {'type': 'switch-status'}

    raise PreventUpdate


@app.callback(
    [
        Output('role-delete-text', 'children'),
        Output('role-delete-confirm-modal', 'visible'),
        Output('role-delete-ids-store', 'data'),
    ],
    [
        Input({'type': 'role-operation-button', 'operation': ALL}, 'nClicks'),
        Input(
            {'type': 'role-operation-table', 'operation': ALL, 'index': ALL},
            'nClicks',
        ),
    ],
    State('role-list-table', 'selectedRowKeys'),
    prevent_initial_call=True,
)
def role_delete_modal(operation_click, button_click, selected_row_keys):
    """
    显示删除角色二次确认弹窗回调
    """
    trigger_id = ctx.triggered_id
    if trigger_id.operation == 'delete':
        if trigger_id.type == 'role-operation-button':
            role_ids = ','.join(selected_row_keys)
        else:
            if trigger_id.type == 'role-operation-table':
                role_ids = trigger_id.index
            else:
                raise PreventUpdate

        return [
            f'是否确认删除角色编号为{role_ids}的角色？',
            True,
            role_ids,
        ]

    raise PreventUpdate


@app.callback(
    Output('role-operations-store', 'data', allow_duplicate=True),
    Input('role-delete-confirm-modal', 'okCounts'),
    State('role-delete-ids-store', 'data'),
    prevent_initial_call=True,
)
def role_delete_confirm(delete_confirm, role_ids_data):
    """
    删除角色弹窗确认回调，实现删除操作
    """
    if delete_confirm:
        params = role_ids_data
        RoleApi.del_role(params)
        MessageManager.success(content='删除成功')

        return {'type': 'delete'}

    raise PreventUpdate


@app.callback(
    [
        Output('role_to_allocated_user-modal', 'visible'),
        Output(
            {'type': 'allocate_user-search', 'index': 'allocated'}, 'nClicks'
        ),
        Output('allocate_user-role_id-container', 'data'),
    ],
    Input(
        {'type': 'role-operation-table', 'operation': ALL, 'index': ALL},
        'nClicks',
    ),
    State({'type': 'allocate_user-search', 'index': 'allocated'}, 'nClicks'),
    prevent_initial_call=True,
)
def role_to_allocated_user_modal(allocated_click, allocated_user_search_nclick):
    """
    显示角色分配用户弹窗回调
    """
    trigger_id = ctx.triggered_id
    if trigger_id.operation == 'allocation':
        return [
            True,
            allocated_user_search_nclick + 1
            if allocated_user_search_nclick
            else 1,
            trigger_id.index,
        ]

    raise PreventUpdate


@app.callback(
    [
        Output('role-export-container', 'data', allow_duplicate=True),
        Output('role-export-complete-judge-container', 'data'),
    ],
    Input('role-export', 'nClicks'),
    [
        State('role-role_name-input', 'value'),
        State('role-role_key-input', 'value'),
        State('role-status-select', 'value'),
        State('role-create_time-range', 'value'),
    ],
    running=[[Output('role-export', 'loading'), True, False]],
    prevent_initial_call=True,
)
def export_role_list(
    export_click, role_name, role_key, status_select, create_time_range
):
    """
    导出角色信息回调
    """
    if export_click:
        begin_time = None
        end_time = None
        if create_time_range:
            begin_time = create_time_range[0]
            end_time = create_time_range[1]
        export_params = dict(
            role_name=role_name,
            role_key=role_key,
            status=status_select,
            begin_time=begin_time,
            end_time=end_time,
        )
        export_role_res = RoleApi.export_role(export_params)
        export_role = export_role_res.content
        MessageManager.success(content='导出成功')

        return [
            dcc.send_bytes(
                export_role,
                f'角色信息_{time.strftime("%Y%m%d%H%M%S", time.localtime())}.xlsx',
            ),
            {'timestamp': time.time()},
        ]

    raise PreventUpdate


@app.callback(
    Output('role-export-container', 'data', allow_duplicate=True),
    Input('role-export-complete-judge-container', 'data'),
    prevent_initial_call=True,
)
def reset_role_export_status(data):
    """
    导出完成后重置下载组件数据回调，防止重复下载文件
    """
    time.sleep(0.5)
    if data:
        return None

    raise PreventUpdate
