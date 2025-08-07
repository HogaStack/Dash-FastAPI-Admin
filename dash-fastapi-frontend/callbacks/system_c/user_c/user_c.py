import base64
import time
from io import BytesIO
from dash import ctx, dcc, no_update
from dash.dependencies import ALL, Input, Output, State
from dash.exceptions import PreventUpdate
from typing import Dict
from api.system.user import UserApi
from config.constant import SysNormalDisableConstant
from server import app
from utils.common_util import ValidateUtil
from utils.feedback_util import MessageManager
from utils.permission_util import PermissionManager
from utils.time_format_util import TimeFormatUtil


def generate_user_table(query_params: Dict):
    """
    根据查询参数获取用户表格数据及分页信息

    :param query_params: 查询参数
    :return: 用户表格数据及分页信息
    """
    table_info = UserApi.list_user(query_params)
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
            item['status'] = dict(checked=True, disabled=item['user_id'] == 1)
        else:
            item['status'] = dict(checked=False, disabled=item['user_id'] == 1)
        item['dept_name'] = (
            item.get('dept').get('dept_name') if item.get('dept') else None
        )
        item['create_time'] = TimeFormatUtil.format_time(
            item.get('create_time')
        )
        item['key'] = str(item['user_id'])
        if item['user_id'] == 1:
            item['operation'] = []
        else:
            item['operation'] = [
                {'title': '修改', 'icon': 'antd-edit'}
                if PermissionManager.check_perms('system:user:edit')
                else None,
                {'title': '删除', 'icon': 'antd-delete'}
                if PermissionManager.check_perms('system:user:remove')
                else None,
                {'title': '重置密码', 'icon': 'antd-key'}
                if PermissionManager.check_perms('system:user:resetPwd')
                else None,
                {'title': '分配角色', 'icon': 'antd-check-circle'}
                if PermissionManager.check_perms('system:user:edit')
                else None,
            ]

    return [table_data, table_pagination]


app.clientside_callback(
    """(dept_input) => dept_input""",
    Output('dept-tree', 'searchKeyword'),
    Input('dept-input-search', 'value'),
    prevent_initial_call=True,
)


@app.callback(
    output=dict(
        user_table_data=Output('user-list-table', 'data', allow_duplicate=True),
        user_table_pagination=Output(
            'user-list-table', 'pagination', allow_duplicate=True
        ),
        user_table_selectedrowkeys=Output('user-list-table', 'selectedRowKeys'),
    ),
    inputs=dict(
        selected_dept_tree=Input('dept-tree', 'selectedKeys'),
        search_click=Input('user-search', 'nClicks'),
        refresh_click=Input('user-refresh', 'nClicks'),
        pagination=Input('user-list-table', 'pagination'),
        operations=Input('user-operations-store', 'data'),
    ),
    state=dict(
        user_name=State('user-user_name-input', 'value'),
        phone_number=State('user-phone_number-input', 'value'),
        status_select=State('user-status-select', 'value'),
        create_time_range=State('user-create_time-range', 'value'),
    ),
    prevent_initial_call=True,
)
def get_user_table_data_by_dept_tree(
    selected_dept_tree,
    search_click,
    refresh_click,
    pagination,
    operations,
    user_name,
    phone_number,
    status_select,
    create_time_range,
):
    """
    获取用户表格数据回调（进行表格相关增删查改操作后均会触发此回调）
    """
    dept_id = None
    begin_time = None
    end_time = None
    if create_time_range:
        begin_time = create_time_range[0]
        end_time = create_time_range[1]
    if selected_dept_tree:
        dept_id = int(selected_dept_tree[0])
    query_params = dict(
        dept_id=dept_id,
        user_name=user_name,
        phonenumber=phone_number,
        status=status_select,
        begin_time=begin_time,
        end_time=end_time,
        page_num=1,
        page_size=10,
    )
    triggered_id = ctx.triggered_id
    if triggered_id == 'user-list-table':
        query_params.update(
            {
                'page_num': pagination['current'],
                'page_size': pagination['pageSize'],
            }
        )
    if (
        selected_dept_tree
        or search_click
        or refresh_click
        or pagination
        or operations
    ):
        table_data, table_pagination = generate_user_table(query_params)

        return dict(
            user_table_data=table_data,
            user_table_pagination=table_pagination,
            user_table_selectedrowkeys=None,
        )

    raise PreventUpdate


# 重置用户搜索表单数据回调
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
        Output('dept-tree', 'selectedKeys'),
        Output('user-user_name-input', 'value'),
        Output('user-phone_number-input', 'value'),
        Output('user-status-select', 'value'),
        Output('user-create_time-range', 'value'),
        Output('user-operations-store', 'data'),
    ],
    Input('user-reset', 'nClicks'),
    prevent_initial_call=True,
)


# 隐藏/显示用户搜索表单回调
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
        Output('user-search-form-container', 'hidden'),
        Output('user-hidden-tooltip', 'title'),
    ],
    Input('user-hidden', 'nClicks'),
    State('user-search-form-container', 'hidden'),
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
    Output({'type': 'user-operation-button', 'index': 'edit'}, 'disabled'),
    Input('user-list-table', 'selectedRowKeys'),
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
    Output({'type': 'user-operation-button', 'index': 'delete'}, 'disabled'),
    Input('user-list-table', 'selectedRowKeys'),
    prevent_initial_call=True,
)


# 用户表单数据双向绑定回调
app.clientside_callback(
    """
    (row_data, form_value) => {
        trigger_id = window.dash_clientside.callback_context.triggered_id;
        if (trigger_id === 'user-form-store') {
            return [window.dash_clientside.no_update, row_data];
        }
        if (trigger_id === 'user-form') {
            Object.assign(row_data, form_value);
            return [row_data, window.dash_clientside.no_update];
        }
        throw window.dash_clientside.PreventUpdate;
    }
    """,
    [
        Output('user-form-store', 'data', allow_duplicate=True),
        Output('user-form', 'values'),
    ],
    [
        Input('user-form-store', 'data'),
        Input('user-form', 'values'),
    ],
    prevent_initial_call=True,
)


@app.callback(
    output=dict(
        modal_visible=Output('user-modal', 'visible', allow_duplicate=True),
        modal_title=Output('user-modal', 'title'),
        dept_tree=Output('user-dpet-tree', 'treeData'),
        post_option=Output('user-post', 'options'),
        role_option=Output('user-role', 'options'),
        user_name_disabled=Output('user-form-user_name', 'disabled'),
        password_disabled=Output('user-form-password', 'disabled'),
        user_name_password_container=Output(
            'user-user_name-password-container', 'hidden'
        ),
        form_value=Output('user-form-store', 'data', allow_duplicate=True),
        form_label_validate_status=Output(
            'user-form', 'validateStatuses', allow_duplicate=True
        ),
        form_label_validate_info=Output(
            'user-form', 'helps', allow_duplicate=True
        ),
        modal_type=Output('user-modal_type-store', 'data'),
    ),
    inputs=dict(
        operation_click=Input(
            {'type': 'user-operation-button', 'index': ALL}, 'nClicks'
        ),
        dropdown_click=Input('user-list-table', 'nClicksDropdownItem'),
    ),
    state=dict(
        selected_row_keys=State('user-list-table', 'selectedRowKeys'),
        recently_clicked_dropdown_item_title=State(
            'user-list-table', 'recentlyClickedDropdownItemTitle'
        ),
        recently_dropdown_item_clicked_row=State(
            'user-list-table', 'recentlyDropdownItemClickedRow'
        ),
    ),
    prevent_initial_call=True,
)
def add_edit_user_modal(
    operation_click,
    dropdown_click,
    selected_row_keys,
    recently_clicked_dropdown_item_title,
    recently_dropdown_item_clicked_row,
):
    """
    显示新增或编辑用户弹窗回调
    """
    trigger_id = ctx.triggered_id
    if (
        trigger_id == {'index': 'add', 'type': 'user-operation-button'}
        or trigger_id == {'index': 'edit', 'type': 'user-operation-button'}
        or (
            trigger_id == 'user-list-table'
            and recently_clicked_dropdown_item_title == '修改'
        )
    ):
        tree_info = UserApi.dept_tree_select()
        tree_data = tree_info['data']
        if trigger_id == {'index': 'add', 'type': 'user-operation-button'}:
            detail_info = UserApi.get_user(user_id='')
            post_option = detail_info['posts']
            role_option = detail_info['roles']
            user_info = dict(
                nick_name=None,
                dept_id=None,
                phonenumber=None,
                email=None,
                user_name=None,
                password=None,
                post_ids=None,
                user_ids=None,
                sex=None,
                status=SysNormalDisableConstant.NORMAL,
                remark=None,
            )
            return dict(
                modal_visible=True,
                modal_title='新增用户',
                dept_tree=tree_data,
                post_option=[
                    dict(label=item['post_name'], value=item['post_id'])
                    for item in post_option
                    if item
                ]
                or [],
                role_option=[
                    dict(label=item['role_name'], value=item['role_id'])
                    for item in role_option
                    if item
                ]
                or [],
                user_name_disabled=False,
                password_disabled=False,
                user_name_password_container=False,
                form_value=user_info,
                form_label_validate_status=None,
                form_label_validate_info=None,
                modal_type={'type': 'add'},
            )
        elif trigger_id == {
            'index': 'edit',
            'type': 'user-operation-button',
        } or (
            trigger_id == 'user-list-table'
            and recently_clicked_dropdown_item_title == '修改'
        ):
            if trigger_id == {'index': 'edit', 'type': 'user-operation-button'}:
                user_id = int(','.join(selected_row_keys))
            else:
                user_id = int(recently_dropdown_item_clicked_row['key'])
            user_info_res = UserApi.get_user(user_id=user_id)
            user_info = user_info_res['data']
            post_option = user_info_res['posts']
            role_option = user_info_res['roles']
            post_ids = user_info['post_ids']
            role_ids = user_info['role_ids']
            user_info['post_ids'] = (
                [int(item) for item in post_ids.split(',')] if post_ids else []
            )
            user_info['role_ids'] = (
                [int(item) for item in role_ids.split(',')] if role_ids else []
            )
            return dict(
                modal_visible=True,
                modal_title='编辑用户',
                dept_tree=tree_data,
                post_option=[
                    dict(label=item['post_name'], value=item['post_id'])
                    for item in post_option
                    if item
                ]
                or [],
                role_option=[
                    dict(label=item['role_name'], value=item['role_id'])
                    for item in role_option
                    if item
                ]
                or [],
                user_name_disabled=True,
                password_disabled=True,
                user_name_password_container=True,
                form_value=user_info,
                form_label_validate_status=None,
                form_label_validate_info=None,
                modal_type={'type': 'edit'},
            )

    raise PreventUpdate


@app.callback(
    output=dict(
        form_label_validate_status=Output(
            'user-form', 'validateStatuses', allow_duplicate=True
        ),
        form_label_validate_info=Output(
            'user-form', 'helps', allow_duplicate=True
        ),
        modal_visible=Output('user-modal', 'visible'),
        operations=Output(
            'user-operations-store', 'data', allow_duplicate=True
        ),
    ),
    inputs=dict(confirm_trigger=Input('user-modal', 'okCounts')),
    state=dict(
        modal_type=State('user-modal_type-store', 'data'),
        form_value=State('user-form-store', 'data'),
        form_label=State(
            {'type': 'user-form-label', 'index': ALL, 'required': True}, 'label'
        ),
    ),
    running=[[Output('user-modal', 'confirmLoading'), True, False]],
    prevent_initial_call=True,
)
def user_confirm(confirm_trigger, modal_type, form_value, form_label):
    """
    新增或编辑用户弹窗确认回调，实现新增或编辑操作
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
            params_add['post_ids'] = (
                [int(item) for item in params_add.get('post_ids')]
                if params_add.get('post_ids')
                else []
            )
            params_add['role_ids'] = (
                [int(item) for item in params_add.get('role_ids')]
                if params_add.get('role_ids')
                else []
            )
            params_edit = params_add.copy()
            params_edit['role'] = []
            modal_type = modal_type.get('type')
            if modal_type == 'add':
                UserApi.add_user(params_add)
            if modal_type == 'edit':
                UserApi.update_user(params_edit)
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
    Output('user-operations-store', 'data', allow_duplicate=True),
    [
        Input('user-list-table', 'recentlySwitchDataIndex'),
        Input('user-list-table', 'recentlySwitchStatus'),
        Input('user-list-table', 'recentlySwitchRow'),
    ],
    prevent_initial_call=True,
)
def table_switch_user_status(
    recently_switch_data_index, recently_switch_status, recently_switch_row
):
    """
    表格内切换用户状态回调
    """
    if recently_switch_data_index:
        UserApi.change_user_status(
            user_id=int(recently_switch_row['key']),
            status='0' if recently_switch_status else '1',
        )
        MessageManager.success(content='修改成功')

        return {'type': 'switch-status'}

    raise PreventUpdate


@app.callback(
    [
        Output('user-delete-text', 'children'),
        Output('user-delete-confirm-modal', 'visible'),
        Output('user-delete-ids-store', 'data'),
    ],
    [
        Input({'type': 'user-operation-button', 'index': ALL}, 'nClicks'),
        Input('user-list-table', 'nClicksDropdownItem'),
    ],
    [
        State('user-list-table', 'selectedRowKeys'),
        State('user-list-table', 'recentlyClickedDropdownItemTitle'),
        State('user-list-table', 'recentlyDropdownItemClickedRow'),
    ],
    prevent_initial_call=True,
)
def user_delete_modal(
    operation_click,
    dropdown_click,
    selected_row_keys,
    recently_clicked_dropdown_item_title,
    recently_dropdown_item_clicked_row,
):
    """
    显示删除用户二次确认弹窗回调
    """
    trigger_id = ctx.triggered_id
    if trigger_id == {'index': 'delete', 'type': 'user-operation-button'} or (
        trigger_id == 'user-list-table'
        and recently_clicked_dropdown_item_title == '删除'
    ):
        if trigger_id == {'index': 'delete', 'type': 'user-operation-button'}:
            user_ids = ','.join(selected_row_keys)
        else:
            if recently_clicked_dropdown_item_title == '删除':
                user_ids = recently_dropdown_item_clicked_row['key']
            else:
                raise PreventUpdate

        return [
            f'是否确认删除用户编号为{user_ids}的用户？',
            True,
            user_ids,
        ]

    raise PreventUpdate


@app.callback(
    Output('user-operations-store', 'data', allow_duplicate=True),
    Input('user-delete-confirm-modal', 'okCounts'),
    State('user-delete-ids-store', 'data'),
    prevent_initial_call=True,
)
def user_delete_confirm(delete_confirm, user_ids_data):
    """
    删除用户弹窗确认回调，实现删除操作
    """
    if delete_confirm:
        params = user_ids_data
        UserApi.del_user(params)
        MessageManager.success(content='删除成功')

        return {'type': 'delete'}

    raise PreventUpdate


@app.callback(
    [
        Output(
            'user-reset-password-confirm-modal', 'visible', allow_duplicate=True
        ),
        Output('reset-password-row-key-store', 'data'),
        Output('reset-password-input', 'value'),
    ],
    Input('user-list-table', 'nClicksDropdownItem'),
    [
        State('user-list-table', 'recentlyClickedDropdownItemTitle'),
        State('user-list-table', 'recentlyDropdownItemClickedRow'),
    ],
    prevent_initial_call=True,
)
def user_reset_password_modal(
    dropdown_click,
    recently_clicked_dropdown_item_title,
    recently_dropdown_item_clicked_row,
):
    """
    显示重置用户密码弹窗回调
    """
    if dropdown_click:
        if recently_clicked_dropdown_item_title == '重置密码':
            user_id = recently_dropdown_item_clicked_row['key']
        else:
            raise PreventUpdate

        return [True, user_id, None]

    raise PreventUpdate


@app.callback(
    [
        Output('user-operations-store', 'data', allow_duplicate=True),
        Output(
            'user-reset-password-confirm-modal', 'visible', allow_duplicate=True
        ),
    ],
    Input('user-reset-password-confirm-modal', 'okCounts'),
    [
        State('reset-password-row-key-store', 'data'),
        State('reset-password-input', 'value'),
    ],
    running=[
        [
            Output('user-reset-password-confirm-modal', 'confirmLoading'),
            True,
            False,
        ]
    ],
    prevent_initial_call=True,
)
def user_reset_password_confirm(reset_confirm, user_id_data, reset_password):
    """
    重置用户密码弹窗确认回调，实现重置密码操作
    """
    if reset_confirm:
        UserApi.reset_user_pwd(
            user_id=int(user_id_data), password=reset_password
        )
        MessageManager.success(content='重置成功')

        return [{'type': 'reset-password'}, False]

    raise PreventUpdate


@app.callback(
    [
        Output('user_to_allocated_role-modal', 'visible'),
        Output('allocate_role-user_id-container', 'data'),
        Output('allocate_role-nick_name-input', 'value'),
        Output('allocate_role-user_name-input', 'value'),
        Output('allocate_role-list-table', 'selectedRowKeys'),
        Output('allocate_role-list-table', 'data'),
    ],
    Input('user-list-table', 'nClicksDropdownItem'),
    [
        State('user-list-table', 'recentlyClickedDropdownItemTitle'),
        State('user-list-table', 'recentlyDropdownItemClickedRow'),
    ],
    prevent_initial_call=True,
)
def role_to_allocated_user_modal(
    dropdown_click,
    recently_clicked_dropdown_item_title,
    recently_dropdown_item_clicked_row,
):
    """
    显示用户分配角色弹窗回调
    """
    if dropdown_click and recently_clicked_dropdown_item_title == '分配角色':
        user_id = int(recently_dropdown_item_clicked_row['key'])
        allocated_role_info = UserApi.get_auth_role(user_id=user_id)
        table_data = allocated_role_info.get('roles')
        selected_row_keys = []
        for item in table_data:
            item['create_time'] = TimeFormatUtil.format_time(
                item.get('create_time')
            )
            item['key'] = str(item['role_id'])
            if item.get('flag'):
                selected_row_keys.append(str(item['role_id']))
        return [
            True,
            user_id,
            allocated_role_info.get('user').get('nick_name'),
            allocated_role_info.get('user').get('user_name'),
            selected_row_keys,
            table_data,
        ]

    raise PreventUpdate


# 显示用户导入弹窗及重置上传弹窗组件状态回调
app.clientside_callback(
    """
    (nClicks) => {
        if (nClicks) {
            return [
                true, 
                null, 
                false
            ];
        }
        return [
            false,
            window.dash_clientside.no_update,
            window.dash_clientside.no_update
        ];
    }
    """,
    [
        Output('user-import-confirm-modal', 'visible', allow_duplicate=True),
        Output('user-upload-choose', 'contents'),
        Output('user-import-update-check', 'checked'),
    ],
    Input('user-import', 'nClicks'),
    prevent_initial_call=True,
)


@app.callback(
    output=dict(
        result_modal_visible=Output('batch-result-modal', 'visible'),
        import_modal_visible=Output(
            'user-import-confirm-modal', 'visible', allow_duplicate=True
        ),
        batch_result=Output('batch-result-content', 'children'),
        operations=Output(
            'user-operations-store', 'data', allow_duplicate=True
        ),
    ),
    inputs=dict(import_confirm=Input('user-import-confirm-modal', 'okCounts')),
    state=dict(
        contents=State('user-upload-choose', 'contents'),
        is_update=State('user-import-update-check', 'checked'),
    ),
    running=[
        [Output('user-import-confirm-modal', 'confirmLoading'), True, False],
        [Output('user-import-confirm-modal', 'okText'), '导入中', '导入'],
    ],
    prevent_initial_call=True,
)
def user_import_confirm(import_confirm, contents, is_update):
    """
    用户导入弹窗确认回调，实现批量导入用户操作
    """
    if import_confirm:
        if contents:
            # url = list_upload_task_record[-1].get('url')
            # batch_param = dict(url=url, is_update=is_update)
            batch_import_result = UserApi.import_user(
                file=BytesIO(base64.b64decode(contents.split(',', 1)[1])),
                update_support=is_update,
            )
            MessageManager.success(content='导入成功')

            return dict(
                result_modal_visible=True
                if batch_import_result.get('msg')
                else False,
                import_modal_visible=True
                if batch_import_result.get('msg')
                else False,
                batch_result=batch_import_result.get('msg'),
                operations={'type': 'batch-import'},
            )
        else:
            MessageManager.warning(content='请上传需要导入的文件')

            return dict(
                result_modal_visible=no_update,
                import_modal_visible=True,
                batch_result=no_update,
                operations=no_update,
            )

    raise PreventUpdate


@app.callback(
    [
        Output('user-export-container', 'data', allow_duplicate=True),
        Output(
            'user-export-complete-judge-container', 'data', allow_duplicate=True
        ),
    ],
    Input('download-user-import-template', 'nClicks'),
    prevent_initial_call=True,
)
def download_user_template(download_click):
    """
    下载导入用户模板回调
    """
    if download_click:
        download_template_res = UserApi.download_template()
        download_template = download_template_res.content
        MessageManager.success(content='下载成功')

        return [
            dcc.send_bytes(
                download_template,
                f'用户导入模板_{time.strftime("%Y%m%d%H%M%S", time.localtime())}.xlsx',
            ),
            {'timestamp': time.time()},
        ]

    raise PreventUpdate


@app.callback(
    [
        Output('user-export-container', 'data', allow_duplicate=True),
        Output(
            'user-export-complete-judge-container', 'data', allow_duplicate=True
        ),
    ],
    Input('user-export', 'nClicks'),
    [
        State('dept-tree', 'selectedKeys'),
        State('user-user_name-input', 'value'),
        State('user-phone_number-input', 'value'),
        State('user-status-select', 'value'),
        State('user-create_time-range', 'value'),
    ],
    running=[[Output('user-export', 'loading'), True, False]],
    prevent_initial_call=True,
)
def export_user_list(
    export_click,
    selected_dept_tree,
    user_name,
    phone_number,
    status_select,
    create_time_range,
):
    """
    导出用户信息回调
    """
    if export_click:
        dept_id = None
        begin_time = None
        end_time = None
        if create_time_range:
            begin_time = create_time_range[0]
            end_time = create_time_range[1]
        if selected_dept_tree:
            dept_id = int(selected_dept_tree[0])
        export_params = dict(
            dept_id=dept_id,
            user_name=user_name,
            phonenumber=phone_number,
            status=status_select,
            begin_time=begin_time,
            end_time=end_time,
        )
        export_user_res = UserApi.export_user(export_params)
        MessageManager.success(content='导出成功')

        export_user = export_user_res.content

        return [
            dcc.send_bytes(
                export_user,
                f'用户信息_{time.strftime("%Y%m%d%H%M%S", time.localtime())}.xlsx',
            ),
            {'timestamp': time.time()},
        ]

    raise PreventUpdate


@app.callback(
    Output('user-export-container', 'data', allow_duplicate=True),
    Input('user-export-complete-judge-container', 'data'),
    prevent_initial_call=True,
)
def reset_user_export_status(data):
    """
    导出完成后重置下载组件数据回调，防止重复下载文件
    """
    time.sleep(0.5)
    if data:
        return None

    raise PreventUpdate
