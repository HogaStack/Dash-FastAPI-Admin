import time
from dash import ctx, dcc, no_update
from dash.dependencies import ALL, Input, Output, State
from dash.exceptions import PreventUpdate
from typing import Dict
from api.system.post import PostApi
from config.constant import SysNormalDisableConstant
from server import app
from utils.common_util import ValidateUtil
from utils.dict_util import DictManager
from utils.feedback_util import MessageManager
from utils.permission_util import PermissionManager
from utils.time_format_util import TimeFormatUtil


def generate_post_table(query_params: Dict):
    """
    根据查询参数获取岗位表格数据及分页信息

    :param query_params: 查询参数
    :return: 岗位表格数据及分页信息
    """
    table_info = PostApi.list_post(query_params)
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
        item['status'] = DictManager.get_dict_tag(
            dict_type='sys_normal_disable', dict_value=item.get('status')
        )
        item['create_time'] = TimeFormatUtil.format_time(
            item.get('create_time')
        )
        item['key'] = str(item['post_id'])
        item['operation'] = [
            {'content': '修改', 'type': 'link', 'icon': 'antd-edit'}
            if PermissionManager.check_perms('system:post:edit')
            else {},
            {'content': '删除', 'type': 'link', 'icon': 'antd-delete'}
            if PermissionManager.check_perms('system:post:remove')
            else {},
        ]

    return [table_data, table_pagination]


@app.callback(
    output=dict(
        post_table_data=Output('post-list-table', 'data', allow_duplicate=True),
        post_table_pagination=Output(
            'post-list-table', 'pagination', allow_duplicate=True
        ),
        post_table_selectedrowkeys=Output('post-list-table', 'selectedRowKeys'),
    ),
    inputs=dict(
        search_click=Input('post-search', 'nClicks'),
        refresh_click=Input('post-refresh', 'nClicks'),
        pagination=Input('post-list-table', 'pagination'),
        operations=Input('post-operations-store', 'data'),
    ),
    state=dict(
        post_code=State('post-post_code-input', 'value'),
        post_name=State('post-post_name-input', 'value'),
        status_select=State('post-status-select', 'value'),
    ),
    prevent_initial_call=True,
)
def get_post_table_data(
    search_click,
    refresh_click,
    pagination,
    operations,
    post_code,
    post_name,
    status_select,
):
    """
    获取岗位表格数据回调（进行表格相关增删查改操作后均会触发此回调）
    """

    query_params = dict(
        post_code=post_code,
        post_name=post_name,
        status=status_select,
        page_num=1,
        page_size=10,
    )
    triggered_id = ctx.triggered_id
    if triggered_id == 'post-list-table':
        query_params.update(
            {
                'page_num': pagination['current'],
                'page_size': pagination['pageSize'],
            }
        )
    if search_click or refresh_click or pagination or operations:
        table_data, table_pagination = generate_post_table(query_params)
        return dict(
            post_table_data=table_data,
            post_table_pagination=table_pagination,
            post_table_selectedrowkeys=None,
        )

    raise PreventUpdate


# 重置岗位搜索表单数据回调
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
        Output('post-post_code-input', 'value'),
        Output('post-post_name-input', 'value'),
        Output('post-status-select', 'value'),
        Output('post-operations-store', 'data'),
    ],
    Input('post-reset', 'nClicks'),
    prevent_initial_call=True,
)


# 隐藏/显示岗位搜索表单回调
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
        Output('post-search-form-container', 'hidden'),
        Output('post-hidden-tooltip', 'title'),
    ],
    Input('post-hidden', 'nClicks'),
    State('post-search-form-container', 'hidden'),
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
    Output({'type': 'post-operation-button', 'index': 'edit'}, 'disabled'),
    Input('post-list-table', 'selectedRowKeys'),
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
    Output({'type': 'post-operation-button', 'index': 'delete'}, 'disabled'),
    Input('post-list-table', 'selectedRowKeys'),
    prevent_initial_call=True,
)


# 岗位表单数据双向绑定回调
app.clientside_callback(
    """
    (row_data, form_value) => {
        trigger_id = window.dash_clientside.callback_context.triggered_id;
        if (trigger_id === 'post-form-store') {
            return [window.dash_clientside.no_update, row_data];
        }
        if (trigger_id === 'post-form') {
            Object.assign(row_data, form_value);
            return [row_data, window.dash_clientside.no_update];
        }
        throw window.dash_clientside.PreventUpdate;
    }
    """,
    [
        Output('post-form-store', 'data', allow_duplicate=True),
        Output('post-form', 'values'),
    ],
    [
        Input('post-form-store', 'data'),
        Input('post-form', 'values'),
    ],
    prevent_initial_call=True,
)


@app.callback(
    output=dict(
        modal_visible=Output('post-modal', 'visible', allow_duplicate=True),
        modal_title=Output('post-modal', 'title'),
        form_value=Output('post-form-store', 'data', allow_duplicate=True),
        form_label_validate_status=Output(
            'post-form', 'validateStatuses', allow_duplicate=True
        ),
        form_label_validate_info=Output(
            'post-form', 'helps', allow_duplicate=True
        ),
        modal_type=Output('post-modal_type-store', 'data'),
    ),
    inputs=dict(
        operation_click=Input(
            {'type': 'post-operation-button', 'index': ALL}, 'nClicks'
        ),
        button_click=Input('post-list-table', 'nClicksButton'),
    ),
    state=dict(
        selected_row_keys=State('post-list-table', 'selectedRowKeys'),
        clicked_content=State('post-list-table', 'clickedContent'),
        recently_button_clicked_row=State(
            'post-list-table', 'recentlyButtonClickedRow'
        ),
    ),
    prevent_initial_call=True,
)
def add_edit_post_modal(
    operation_click,
    button_click,
    selected_row_keys,
    clicked_content,
    recently_button_clicked_row,
):
    """
    显示新增或编辑岗位弹窗回调
    """
    trigger_id = ctx.triggered_id
    if (
        trigger_id == {'index': 'add', 'type': 'post-operation-button'}
        or trigger_id == {'index': 'edit', 'type': 'post-operation-button'}
        or (trigger_id == 'post-list-table' and clicked_content == '修改')
    ):
        if trigger_id == {'index': 'add', 'type': 'post-operation-button'}:
            post_info = dict(
                post_name=None,
                post_code=None,
                post_sort=0,
                status=SysNormalDisableConstant.NORMAL,
                remark=None,
            )
            return dict(
                modal_visible=True,
                modal_title='新增岗位',
                form_value=post_info,
                form_label_validate_status=None,
                form_label_validate_info=None,
                modal_type={'type': 'add'},
            )
        elif trigger_id == {
            'index': 'edit',
            'type': 'post-operation-button',
        } or (trigger_id == 'post-list-table' and clicked_content == '修改'):
            if trigger_id == {'index': 'edit', 'type': 'post-operation-button'}:
                post_id = int(','.join(selected_row_keys))
            else:
                post_id = int(recently_button_clicked_row['key'])
            post_info_res = PostApi.get_post(post_id=post_id)
            post_info = post_info_res['data']
            return dict(
                modal_visible=True,
                modal_title='编辑岗位',
                form_value=post_info,
                form_label_validate_status=None,
                form_label_validate_info=None,
                modal_type={'type': 'edit'},
            )

    raise PreventUpdate


@app.callback(
    output=dict(
        form_label_validate_status=Output(
            'post-form', 'validateStatuses', allow_duplicate=True
        ),
        form_label_validate_info=Output(
            'post-form', 'helps', allow_duplicate=True
        ),
        modal_visible=Output('post-modal', 'visible'),
        operations=Output(
            'post-operations-store', 'data', allow_duplicate=True
        ),
    ),
    inputs=dict(confirm_trigger=Input('post-modal', 'okCounts')),
    state=dict(
        modal_type=State('post-modal_type-store', 'data'),
        form_value=State('post-form-store', 'data'),
        form_label=State(
            {'type': 'post-form-label', 'index': ALL, 'required': True}, 'label'
        ),
    ),
    running=[[Output('post-modal', 'confirmLoading'), True, False]],
    prevent_initial_call=True,
)
def post_confirm(confirm_trigger, modal_type, form_value, form_label):
    """
    新增或编辑岗位弹窗确认回调，实现新增或编辑操作
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
                PostApi.add_post(params_add)
            if modal_type == 'edit':
                PostApi.update_post(params_edit)
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
        Output('post-delete-text', 'children'),
        Output('post-delete-confirm-modal', 'visible'),
        Output('post-delete-ids-store', 'data'),
    ],
    [
        Input({'type': 'post-operation-button', 'index': ALL}, 'nClicks'),
        Input('post-list-table', 'nClicksButton'),
    ],
    [
        State('post-list-table', 'selectedRowKeys'),
        State('post-list-table', 'clickedContent'),
        State('post-list-table', 'recentlyButtonClickedRow'),
    ],
    prevent_initial_call=True,
)
def post_delete_modal(
    operation_click,
    button_click,
    selected_row_keys,
    clicked_content,
    recently_button_clicked_row,
):
    """
    显示删除岗位二次确认弹窗回调
    """
    trigger_id = ctx.triggered_id
    if trigger_id == {'index': 'delete', 'type': 'post-operation-button'} or (
        trigger_id == 'post-list-table' and clicked_content == '删除'
    ):
        if trigger_id == {'index': 'delete', 'type': 'post-operation-button'}:
            post_ids = ','.join(selected_row_keys)
        else:
            if clicked_content == '删除':
                post_ids = recently_button_clicked_row['key']
            else:
                raise PreventUpdate

        return [f'是否确认删除岗位编号为{post_ids}的岗位？', True, post_ids]

    raise PreventUpdate


@app.callback(
    Output('post-operations-store', 'data', allow_duplicate=True),
    Input('post-delete-confirm-modal', 'okCounts'),
    State('post-delete-ids-store', 'data'),
    prevent_initial_call=True,
)
def post_delete_confirm(delete_confirm, post_ids_data):
    """
    删除岗位弹窗确认回调，实现删除操作
    """
    if delete_confirm:
        params = post_ids_data
        PostApi.del_post(params)
        MessageManager.success(content='删除成功')

        return {'type': 'delete'}

    raise PreventUpdate


@app.callback(
    [
        Output('post-export-container', 'data', allow_duplicate=True),
        Output('post-export-complete-judge-container', 'data'),
    ],
    Input('post-export', 'nClicks'),
    [
        State('post-post_code-input', 'value'),
        State('post-post_name-input', 'value'),
        State('post-status-select', 'value'),
    ],
    running=[[Output('post-export', 'loading'), True, False]],
    prevent_initial_call=True,
)
def export_post_list(export_click, post_code, post_name, status):
    """
    导出岗位信息回调
    """
    if export_click:
        export_params = dict(
            post_code=post_code, post_name=post_name, status=status
        )
        export_post_res = PostApi.export_post(export_params)
        export_post = export_post_res.content
        MessageManager.success(content='导出成功')

        return [
            dcc.send_bytes(
                export_post,
                f'岗位信息_{time.strftime("%Y%m%d%H%M%S", time.localtime())}.xlsx',
            ),
            {'timestamp': time.time()},
        ]

    raise PreventUpdate


@app.callback(
    Output('post-export-container', 'data', allow_duplicate=True),
    Input('post-export-complete-judge-container', 'data'),
    prevent_initial_call=True,
)
def reset_post_export_status(data):
    """
    导出完成后重置下载组件数据回调，防止重复下载文件
    """
    time.sleep(0.5)
    if data:
        return None

    raise PreventUpdate
