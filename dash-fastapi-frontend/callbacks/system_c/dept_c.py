import uuid
from dash import ctx, no_update
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
from typing import Dict
from api.system.dept import DeptApi
from config.constant import SysNormalDisableConstant
from server import app
from utils.common_util import ValidateUtil
from utils.dict_util import DictManager
from utils.feedback_util import MessageManager
from utils.permission_util import PermissionManager
from utils.time_format_util import TimeFormatUtil
from utils.tree_util import TreeUtil


def generate_dept_table(query_params: Dict):
    """
    根据查询参数获取部门表格数据及展开信息

    :param query_params: 查询参数
    :return: 部门表格数据及展开信息
    """
    table_info = DeptApi.list_dept(query_params)
    default_expanded_row_keys = []
    table_data = table_info['data']
    for item in table_data:
        default_expanded_row_keys.append(str(item['dept_id']))
        item['create_time'] = TimeFormatUtil.format_time(
            item.get('create_time')
        )
        item['key'] = str(item['dept_id'])
        if item['parent_id'] == 0:
            item['operation'] = [
                {'content': '修改', 'type': 'link', 'icon': 'antd-edit'}
                if PermissionManager.check_perms('system:dept:edit')
                else {},
                {'content': '新增', 'type': 'link', 'icon': 'antd-plus'}
                if PermissionManager.check_perms('system:dept:add')
                else {},
            ]
        elif item['status'] == '1':
            item['operation'] = [
                {'content': '修改', 'type': 'link', 'icon': 'antd-edit'}
                if PermissionManager.check_perms('system:dept:edit')
                else {},
                {
                    'content': '删除',
                    'type': 'link',
                    'icon': 'antd-delete',
                }
                if PermissionManager.check_perms('system:dept:remove')
                else {},
            ]
        else:
            item['operation'] = [
                {'content': '修改', 'type': 'link', 'icon': 'antd-edit'}
                if PermissionManager.check_perms('system:dept:edit')
                else {},
                {'content': '新增', 'type': 'link', 'icon': 'antd-plus'}
                if PermissionManager.check_perms('system:dept:add')
                else {},
                {
                    'content': '删除',
                    'type': 'link',
                    'icon': 'antd-delete',
                }
                if PermissionManager.check_perms('system:dept:remove')
                else {},
            ]
        item['status'] = DictManager.get_dict_tag(
            dict_type='sys_normal_disable', dict_value=item.get('status')
        )
    table_data_new = TreeUtil.list_to_tree(table_data, 'dept_id', 'parent_id')

    return [table_data_new, default_expanded_row_keys]


@app.callback(
    output=dict(
        dept_table_data=Output('dept-list-table', 'data', allow_duplicate=True),
        dept_table_key=Output('dept-list-table', 'key'),
        dept_table_defaultexpandedrowkeys=Output(
            'dept-list-table', 'defaultExpandedRowKeys'
        ),
        fold_click=Output('dept-fold', 'nClicks'),
    ),
    inputs=dict(
        search_click=Input('dept-search', 'nClicks'),
        refresh_click=Input('dept-refresh', 'nClicks'),
        operations=Input('dept-operations-store', 'data'),
        fold_click=Input('dept-fold', 'nClicks'),
    ),
    state=dict(
        dept_name=State('dept-dept_name-input', 'value'),
        status_select=State('dept-status-select', 'value'),
        in_default_expanded_row_keys=State(
            'dept-list-table', 'defaultExpandedRowKeys'
        ),
    ),
    prevent_initial_call=True,
)
def get_dept_table_data(
    search_click,
    refresh_click,
    operations,
    fold_click,
    dept_name,
    status_select,
    in_default_expanded_row_keys,
):
    """
    获取部门表格数据回调（进行表格相关增删查改操作后均会触发此回调）
    """
    query_params = dict(dept_name=dept_name, status=status_select)
    if search_click or refresh_click or operations or fold_click:
        table_data, default_expanded_row_keys = generate_dept_table(
            query_params
        )
        if fold_click:
            if in_default_expanded_row_keys:
                return dict(
                    dept_table_data=table_data,
                    dept_table_key=str(uuid.uuid4()),
                    dept_table_defaultexpandedrowkeys=[],
                    fold_click=None,
                )

        return dict(
            dept_table_data=table_data,
            dept_table_key=str(uuid.uuid4()),
            dept_table_defaultexpandedrowkeys=default_expanded_row_keys,
            fold_click=None,
        )

    return dict(
        dept_table_data=no_update,
        dept_table_key=no_update,
        dept_table_defaultexpandedrowkeys=no_update,
        fold_click=None,
    )


# 重置部门搜索表单数据回调
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
        Output('dept-dept_name-input', 'value'),
        Output('dept-status-select', 'value'),
        Output('dept-operations-store', 'data'),
    ],
    Input('dept-reset', 'nClicks'),
    prevent_initial_call=True,
)

# 隐藏/显示部门搜索表单回调
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
        Output('dept-search-form-container', 'hidden'),
        Output('dept-hidden-tooltip', 'title'),
    ],
    Input('dept-hidden', 'nClicks'),
    State('dept-search-form-container', 'hidden'),
    prevent_initial_call=True,
)


# 部门表单数据双向绑定回调
app.clientside_callback(
    """
    (row_data, form_value) => {
        trigger_id = window.dash_clientside.callback_context.triggered_id;
        if (trigger_id === 'dept-form-store') {
            return [window.dash_clientside.no_update, row_data];
        }
        if (trigger_id === 'dept-form') {
            Object.assign(row_data, form_value);
            return [row_data, window.dash_clientside.no_update];
        }
        throw window.dash_clientside.PreventUpdate;
    }
    """,
    [
        Output('dept-form-store', 'data', allow_duplicate=True),
        Output('dept-form', 'values'),
    ],
    [
        Input('dept-form-store', 'data'),
        Input('dept-form', 'values'),
    ],
    prevent_initial_call=True,
)


@app.callback(
    output=dict(
        modal_visible=Output('dept-modal', 'visible', allow_duplicate=True),
        modal_title=Output('dept-modal', 'title'),
        parent_id_div_ishidden=Output('dept-parent_id-div', 'hidden'),
        parent_id_tree=Output('dept-tree-select', 'treeData'),
        form_value=Output('dept-form-store', 'data', allow_duplicate=True),
        form_label_validate_status=Output(
            'dept-form', 'validateStatuses', allow_duplicate=True
        ),
        form_label_validate_info=Output(
            'dept-form', 'helps', allow_duplicate=True
        ),
        modal_type=Output('dept-modal_type-store', 'data'),
    ),
    inputs=dict(
        operation_click=Input(
            {'type': 'dept-operation-button', 'index': ALL}, 'nClicks'
        ),
        button_click=Input('dept-list-table', 'nClicksButton'),
    ),
    state=dict(
        clicked_content=State('dept-list-table', 'clickedContent'),
        recently_button_clicked_row=State(
            'dept-list-table', 'recentlyButtonClickedRow'
        ),
    ),
    prevent_initial_call=True,
)
def add_edit_dept_modal(
    operation_click, button_click, clicked_content, recently_button_clicked_row
):
    """
    显示新增或编辑部门弹窗回调
    """
    trigger_id = ctx.triggered_id
    if trigger_id == {'index': 'add', 'type': 'dept-operation-button'} or (
        trigger_id == 'dept-list-table' and clicked_content != '删除'
    ):
        if trigger_id == 'dept-list-table' and clicked_content == '修改':
            tree_info = DeptApi.list_dept_exclude_child(
                dept_id=int(recently_button_clicked_row['key'])
            )
        else:
            dept_params = dict(dept_name='')
            tree_info = DeptApi.list_dept(dept_params)
        tree_data = TreeUtil.list_to_tree_select(
            tree_info['data'], 'dept_name', 'dept_id', 'dept_id', 'parent_id'
        )

        if trigger_id == {
            'index': 'add',
            'type': 'dept-operation-button',
        } or (trigger_id == 'dept-list-table' and clicked_content == '新增'):
            dept_info = dict(
                parent_id=None
                if trigger_id
                == {'index': 'add', 'type': 'dept-operation-button'}
                else str(recently_button_clicked_row['key']),
                dept_name=None,
                order_num=None,
                leader=None,
                phone=None,
                email=None,
                status=SysNormalDisableConstant.NORMAL,
            )
            return dict(
                modal_visible=True,
                modal_title='新增部门',
                parent_id_div_ishidden=False,
                parent_id_tree=tree_data,
                form_value=dept_info,
                form_label_validate_status=None,
                form_label_validate_info=None,
                modal_type={'type': 'add'},
            )
        elif trigger_id == 'dept-list-table' and clicked_content == '修改':
            dept_id = int(recently_button_clicked_row['key'])
            dept_info_res = DeptApi.get_dept(dept_id=dept_id)
            dept_info = dept_info_res['data']
            return dict(
                modal_visible=True,
                modal_title='编辑部门',
                parent_id_div_ishidden=dept_info.get('parent_id') == 0,
                parent_id_tree=tree_data,
                form_value=dept_info,
                form_label_validate_status=None,
                form_label_validate_info=None,
                modal_type={'type': 'edit'},
            )

    raise PreventUpdate


@app.callback(
    output=dict(
        form_label_validate_status=Output(
            'dept-form', 'validateStatuses', allow_duplicate=True
        ),
        form_label_validate_info=Output(
            'dept-form', 'helps', allow_duplicate=True
        ),
        modal_visible=Output('dept-modal', 'visible'),
        operations=Output(
            'dept-operations-store', 'data', allow_duplicate=True
        ),
    ),
    inputs=dict(confirm_trigger=Input('dept-modal', 'okCounts')),
    state=dict(
        modal_type=State('dept-modal_type-store', 'data'),
        form_value=State('dept-form-store', 'data'),
        form_label=State(
            {'type': 'dept-form-label', 'index': ALL, 'required': True}, 'label'
        ),
    ),
    running=[[Output('dept-modal', 'confirmLoading'), True, False]],
    prevent_initial_call=True,
)
def dept_confirm(confirm_trigger, modal_type, form_value, form_label):
    """
    新增或编辑部门弹窗确认回调，实现新增或编辑操作
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
                DeptApi.add_dept(params_add)
            if modal_type == 'edit':
                DeptApi.update_dept(params_edit)
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
    [
        Output('dept-delete-text', 'children'),
        Output('dept-delete-confirm-modal', 'visible'),
        Output('dept-delete-ids-store', 'data'),
    ],
    [Input('dept-list-table', 'nClicksButton')],
    [
        State('dept-list-table', 'clickedContent'),
        State('dept-list-table', 'recentlyButtonClickedRow'),
    ],
    prevent_initial_call=True,
)
def dept_delete_modal(
    button_click, clicked_content, recently_button_clicked_row
):
    """
    显示删除部门二次确认弹窗回调
    """
    if button_click:
        if clicked_content == '删除':
            dept_ids = recently_button_clicked_row['key']
        else:
            raise PreventUpdate

        return [
            f'是否确认删除部门编号为{dept_ids}的部门？',
            True,
            dept_ids,
        ]

    raise PreventUpdate


@app.callback(
    Output('dept-operations-store', 'data', allow_duplicate=True),
    Input('dept-delete-confirm-modal', 'okCounts'),
    State('dept-delete-ids-store', 'data'),
    prevent_initial_call=True,
)
def dept_delete_confirm(delete_confirm, dept_ids_data):
    """
    删除部门弹窗确认回调，实现删除操作
    """
    if delete_confirm:
        params = dept_ids_data
        DeptApi.del_dept(params)
        MessageManager.success(content='删除成功')

        return {'type': 'delete'}

    raise PreventUpdate
