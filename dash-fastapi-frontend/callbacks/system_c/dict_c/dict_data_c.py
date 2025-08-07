import time
from dash import ctx, dcc, no_update
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
from api.system.dict.data import DictDataApi
from config.constant import SysNormalDisableConstant
from server import app
from utils.cache_util import TTLCacheManager
from utils.common_util import ValidateUtil
from utils.dict_util import DictManager
from utils.feedback_util import MessageManager
from utils.permission_util import PermissionManager
from utils.time_format_util import TimeFormatUtil


@app.callback(
    output=dict(
        dict_data_table_data=Output(
            'dict_data-list-table', 'data', allow_duplicate=True
        ),
        dict_data_table_pagination=Output(
            'dict_data-list-table', 'pagination', allow_duplicate=True
        ),
        dict_data_table_selectedrowkeys=Output(
            'dict_data-list-table', 'selectedRowKeys'
        ),
    ),
    inputs=dict(
        search_click=Input('dict_data-search', 'nClicks'),
        refresh_click=Input('dict_data-refresh', 'nClicks'),
        pagination=Input('dict_data-list-table', 'pagination'),
        operations=Input('dict_data-operations-store', 'data'),
    ),
    state=dict(
        dict_type=State('dict_data-dict_type-select', 'value'),
        dict_label=State('dict_data-dict_label-input', 'value'),
        status_select=State('dict_data-status-select', 'value'),
    ),
    prevent_initial_call=True,
)
def get_dict_data_table_data(
    search_click,
    refresh_click,
    pagination,
    operations,
    dict_type,
    dict_label,
    status_select,
):
    """
    获取字典数据表格数据回调（进行表格相关增删查改操作后均会触发此回调）
    """

    query_params = dict(
        dict_type=dict_type,
        dict_label=dict_label,
        status=status_select,
        page_num=1,
        page_size=10,
    )
    triggered_id = ctx.triggered_id
    if triggered_id == 'dict_data-list-table':
        query_params.update(
            {
                'page_num': pagination['current'],
                'page_size': pagination['pageSize'],
            }
        )
    if search_click or refresh_click or pagination or operations:
        table_info = DictDataApi.list_data(query_params)
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
            item['key'] = str(item['dict_code'])
            item['operation'] = [
                {'content': '修改', 'type': 'link', 'icon': 'antd-edit'}
                if PermissionManager.check_perms('system:dict:edit')
                else {},
                {'content': '删除', 'type': 'link', 'icon': 'antd-delete'}
                if PermissionManager.check_perms('system:dict:remove')
                else {},
            ]

        return dict(
            dict_data_table_data=table_data,
            dict_data_table_pagination=table_pagination,
            dict_data_table_selectedrowkeys=None,
        )

    raise PreventUpdate


# 重置字典数据搜索表单数据回调
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
        Output('dict_data-dict_label-input', 'value'),
        Output('dict_data-status-select', 'value'),
        Output('dict_data-operations-store', 'data'),
    ],
    Input('dict_data-reset', 'nClicks'),
    prevent_initial_call=True,
)


# 隐藏/显示字典数据搜索表单回调
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
        Output('dict_data-search-form-container', 'hidden'),
        Output('dict_data-hidden-tooltip', 'title'),
    ],
    Input('dict_data-hidden', 'nClicks'),
    State('dict_data-search-form-container', 'hidden'),
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
    Output({'type': 'dict_data-operation-button', 'index': 'edit'}, 'disabled'),
    Input('dict_data-list-table', 'selectedRowKeys'),
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
        {'type': 'dict_data-operation-button', 'index': 'delete'}, 'disabled'
    ),
    Input('dict_data-list-table', 'selectedRowKeys'),
    prevent_initial_call=True,
)


# 字典数据表单数据双向绑定回调
app.clientside_callback(
    """
    (row_data, form_value) => {
        trigger_id = window.dash_clientside.callback_context.triggered_id;
        if (trigger_id === 'dict_data-form-store') {
            return [window.dash_clientside.no_update, row_data];
        }
        if (trigger_id === 'dict_data-form') {
            Object.assign(row_data, form_value);
            return [row_data, window.dash_clientside.no_update];
        }
        throw window.dash_clientside.PreventUpdate;
    }
    """,
    [
        Output('dict_data-form-store', 'data', allow_duplicate=True),
        Output('dict_data-form', 'values'),
    ],
    [
        Input('dict_data-form-store', 'data'),
        Input('dict_data-form', 'values'),
    ],
    prevent_initial_call=True,
)


@app.callback(
    output=dict(
        modal_visible=Output(
            'dict_data-modal', 'visible', allow_duplicate=True
        ),
        modal_title=Output('dict_data-modal', 'title'),
        form_value=Output('dict_data-form-store', 'data', allow_duplicate=True),
        form_label_validate_status=Output(
            'dict_data-form', 'validateStatuses', allow_duplicate=True
        ),
        form_label_validate_info=Output(
            'dict_data-form', 'helps', allow_duplicate=True
        ),
        modal_type=Output('dict_data-modal_type-store', 'data'),
    ),
    inputs=dict(
        operation_click=Input(
            {'type': 'dict_data-operation-button', 'index': ALL}, 'nClicks'
        ),
        button_click=Input('dict_data-list-table', 'nClicksButton'),
    ),
    state=dict(
        selected_row_keys=State('dict_data-list-table', 'selectedRowKeys'),
        clicked_content=State('dict_data-list-table', 'clickedContent'),
        recently_button_clicked_row=State(
            'dict_data-list-table', 'recentlyButtonClickedRow'
        ),
        dict_type_select=State('dict_data-dict_type-select', 'value'),
    ),
    prevent_initial_call=True,
)
def add_edit_dict_data_modal(
    operation_click,
    button_click,
    selected_row_keys,
    clicked_content,
    recently_button_clicked_row,
    dict_type_select,
):
    """
    显示新增或编辑字典数据弹窗回调
    """
    trigger_id = ctx.triggered_id
    if (
        trigger_id == {'index': 'add', 'type': 'dict_data-operation-button'}
        or trigger_id == {'index': 'edit', 'type': 'dict_data-operation-button'}
        or (trigger_id == 'dict_data-list-table' and clicked_content == '修改')
    ):
        if trigger_id == {'index': 'add', 'type': 'dict_data-operation-button'}:
            dict_data_info = dict(
                dict_type=dict_type_select,
                dict_label=None,
                dict_value=None,
                css_class=None,
                dict_sort=0,
                list_class='default',
                status=SysNormalDisableConstant.NORMAL,
                remark=None,
            )
            return dict(
                modal_visible=True,
                modal_title='新增字典数据',
                form_value=dict_data_info,
                form_label_validate_status=None,
                form_label_validate_info=None,
                modal_type={'type': 'add'},
            )
        elif trigger_id == {
            'index': 'edit',
            'type': 'dict_data-operation-button',
        } or (
            trigger_id == 'dict_data-list-table' and clicked_content == '修改'
        ):
            if trigger_id == {
                'index': 'edit',
                'type': 'dict_data-operation-button',
            }:
                dict_code = int(','.join(selected_row_keys))
            else:
                dict_code = int(recently_button_clicked_row['key'])
            dict_data_info_res = DictDataApi.get_data(dict_code=dict_code)
            dict_data_info = dict_data_info_res['data']
            return dict(
                modal_visible=True,
                modal_title='编辑字典数据',
                form_value=dict_data_info,
                form_label_validate_status=None,
                form_label_validate_info=None,
                modal_type={'type': 'edit'},
            )

    raise PreventUpdate


@app.callback(
    output=dict(
        form_label_validate_status=Output(
            'dict_data-form', 'validateStatuses', allow_duplicate=True
        ),
        form_label_validate_info=Output(
            'dict_data-form', 'helps', allow_duplicate=True
        ),
        modal_visible=Output('dict_data-modal', 'visible'),
        operations=Output(
            'dict_data-operations-store', 'data', allow_duplicate=True
        ),
    ),
    inputs=dict(confirm_trigger=Input('dict_data-modal', 'okCounts')),
    state=dict(
        modal_type=State('dict_data-modal_type-store', 'data'),
        form_value=State('dict_data-form-store', 'data'),
        form_label=State(
            {'type': 'dict_data-form-label', 'index': ALL, 'required': True},
            'label',
        ),
    ),
    running=[[Output('dict_data-modal', 'confirmLoading'), True, False]],
    prevent_initial_call=True,
)
def dict_data_confirm(confirm_trigger, modal_type, form_value, form_label):
    """
    新增或编字典数据弹窗确认回调，实现新增或编辑操作
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
                DictDataApi.add_data(params_add)
            if modal_type == 'edit':
                DictDataApi.update_data(params_edit)
            if modal_type == 'add':
                TTLCacheManager.delete(form_value.get('dict_type'))
                MessageManager.success('新增成功')

                return dict(
                    form_label_validate_status=None,
                    form_label_validate_info=None,
                    modal_visible=False,
                    operations={'type': 'add'},
                )
            if modal_type == 'edit':
                TTLCacheManager.delete(form_value.get('dict_type'))
                MessageManager.success('编辑成功')

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
        Output('dict_data-delete-text', 'children'),
        Output('dict_data-delete-confirm-modal', 'visible'),
        Output('dict_data-delete-ids-store', 'data'),
    ],
    [
        Input({'type': 'dict_data-operation-button', 'index': ALL}, 'nClicks'),
        Input('dict_data-list-table', 'nClicksButton'),
    ],
    [
        State('dict_data-list-table', 'selectedRows'),
        State('dict_data-list-table', 'clickedContent'),
        State('dict_data-list-table', 'recentlyButtonClickedRow'),
    ],
    prevent_initial_call=True,
)
def dict_data_delete_modal(
    operation_click,
    button_click,
    selected_rows,
    clicked_content,
    recently_button_clicked_row,
):
    """
    显示删除字典数据二次确认弹窗回调
    """
    trigger_id = ctx.triggered_id
    if trigger_id == {
        'index': 'delete',
        'type': 'dict_data-operation-button',
    } or (trigger_id == 'dict_data-list-table' and clicked_content == '删除'):
        if trigger_id == {
            'index': 'delete',
            'type': 'dict_data-operation-button',
        }:
            dict_codes = ','.join(
                [str(item.get('dict_code')) for item in selected_rows]
            )
            dict_types = ','.join(
                list(set([item.get('dict_type') for item in selected_rows]))
            )
        else:
            if clicked_content == '删除':
                dict_codes = recently_button_clicked_row['key']
                dict_types = recently_button_clicked_row['dict_type']
            else:
                return no_update

        return [
            f'是否确认删除字典编码为{dict_codes}的数据？',
            True,
            {'dict_codes': dict_codes, 'dict_types': dict_types},
        ]

    raise PreventUpdate


@app.callback(
    Output('dict_data-operations-store', 'data', allow_duplicate=True),
    Input('dict_data-delete-confirm-modal', 'okCounts'),
    State('dict_data-delete-ids-store', 'data'),
    prevent_initial_call=True,
)
def dict_data_delete_confirm(delete_confirm, dict_codes_data):
    """
    删除字典数据弹窗确认回调，实现删除操作
    """
    if delete_confirm:
        params = dict_codes_data.get('dict_codes')
        dict_types = dict_codes_data.get('dict_types')
        DictDataApi.del_data(params)
        TTLCacheManager.delete(dict_types)
        MessageManager.success('删除成功')

        return {'type': 'delete'}

    raise PreventUpdate


@app.callback(
    [
        Output('dict_data-export-container', 'data', allow_duplicate=True),
        Output('dict_data-export-complete-judge-container', 'data'),
    ],
    Input('dict_data-export', 'nClicks'),
    [
        State('dict_data-dict_type-select', 'value'),
        State('dict_data-dict_label-input', 'value'),
        State('dict_data-status-select', 'value'),
    ],
    running=[[Output('dict_data-export', 'loading'), True, False]],
    prevent_initial_call=True,
)
def export_dict_data_list(export_click, dict_type, dict_label, status_select):
    """
    导出字典数据信息回调
    """
    if export_click:
        export_params = dict(
            dict_type=dict_type,
            dict_label=dict_label,
            status=status_select,
        )
        export_dict_data_res = DictDataApi.export_data(export_params)
        export_dict_data = export_dict_data_res.content
        MessageManager.success('导出成功')

        return [
            dcc.send_bytes(
                export_dict_data,
                f'字典数据信息_{time.strftime("%Y%m%d%H%M%S", time.localtime())}.xlsx',
            ),
            {'timestamp': time.time()},
        ]

    raise PreventUpdate


@app.callback(
    Output('dict_data-export-container', 'data', allow_duplicate=True),
    Input('dict_data-export-complete-judge-container', 'data'),
    prevent_initial_call=True,
)
def reset_dict_data_export_status(data):
    """
    导出完成后重置下载组件数据回调，防止重复下载文件
    """
    time.sleep(0.5)
    if data:
        return None

    raise PreventUpdate
