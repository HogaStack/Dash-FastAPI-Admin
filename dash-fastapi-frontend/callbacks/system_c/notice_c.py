import uuid
from dash import ctx, no_update
from dash.dependencies import ALL, Input, Output, State
from dash.exceptions import PreventUpdate
from typing import Dict
from api.system.notice import NoticeApi
from config.constant import SysNoticeStatusConstant, SysNoticeTypeConstant
from config.env import ApiConfig
from server import app
from utils.common_util import ValidateUtil
from utils.dict_util import DictManager
from utils.feedback_util import MessageManager
from utils.permission_util import PermissionManager
from utils.string_util import StringUtil
from utils.time_format_util import TimeFormatUtil


def generate_notice_table(query_params: Dict):
    """
    根据查询参数获取通知公告表格数据及分页信息

    :param query_params: 查询参数
    :return: 通知公告表格数据及分页信息
    """
    table_info = NoticeApi.list_notice(query_params)
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
            dict_type='sys_notice_status', dict_value=item.get('status')
        )
        item['notice_type'] = DictManager.get_dict_tag(
            dict_type='sys_notice_type', dict_value=item.get('notice_type')
        )
        item['create_time'] = TimeFormatUtil.format_time(
            item.get('create_time')
        )
        item['key'] = str(item['notice_id'])
        item['operation'] = [
            {'content': '修改', 'type': 'link', 'icon': 'antd-edit'}
            if PermissionManager.check_perms('system:notice:edit')
            else {},
            {'content': '删除', 'type': 'link', 'icon': 'antd-delete'}
            if PermissionManager.check_perms('system:notice:remove')
            else {},
        ]

    return [table_data, table_pagination]


@app.callback(
    output=dict(
        notice_table_data=Output(
            'notice-list-table', 'data', allow_duplicate=True
        ),
        notice_table_pagination=Output(
            'notice-list-table', 'pagination', allow_duplicate=True
        ),
        notice_table_selectedrowkeys=Output(
            'notice-list-table', 'selectedRowKeys'
        ),
    ),
    inputs=dict(
        search_click=Input('notice-search', 'nClicks'),
        refresh_click=Input('notice-refresh', 'nClicks'),
        pagination=Input('notice-list-table', 'pagination'),
        operations=Input('notice-operations-store', 'data'),
    ),
    state=dict(
        notice_title=State('notice-notice_title-input', 'value'),
        update_by=State('notice-update_by-input', 'value'),
        notice_type=State('notice-notice_type-select', 'value'),
        create_time_range=State('notice-create_time-range', 'value'),
    ),
    prevent_initial_call=True,
)
def get_notice_table_data(
    search_click,
    refresh_click,
    pagination,
    operations,
    notice_title,
    update_by,
    notice_type,
    create_time_range,
):
    """
    获取通知公告表格数据回调（进行表格相关增删查改操作后均会触发此回调）
    """
    begin_time = None
    end_time = None
    if create_time_range:
        begin_time = create_time_range[0]
        end_time = create_time_range[1]

    query_params = dict(
        notice_title=notice_title,
        update_by=update_by,
        notice_type=notice_type,
        begin_time=begin_time,
        end_time=end_time,
        page_num=1,
        page_size=10,
    )
    triggered_id = ctx.triggered_id
    if triggered_id == 'notice-list-table':
        query_params.update(
            {
                'page_num': pagination['current'],
                'page_size': pagination['pageSize'],
            }
        )
    if search_click or refresh_click or pagination or operations:
        table_data, table_pagination = generate_notice_table(query_params)

        return dict(
            notice_table_data=table_data,
            notice_table_pagination=table_pagination,
            notice_table_selectedrowkeys=None,
        )

    raise PreventUpdate


# 重置通知公告搜索表单数据回调
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
        Output('notice-notice_title-input', 'value'),
        Output('notice-update_by-input', 'value'),
        Output('notice-notice_type-select', 'value'),
        Output('notice-create_time-range', 'value'),
        Output('notice-operations-store', 'data'),
    ],
    Input('notice-reset', 'nClicks'),
    prevent_initial_call=True,
)


# 隐藏/显示通知公告搜索表单回调
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
        Output('notice-search-form-container', 'hidden'),
        Output('notice-hidden-tooltip', 'title'),
    ],
    Input('notice-hidden', 'nClicks'),
    State('notice-search-form-container', 'hidden'),
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
    Output({'type': 'notice-operation-button', 'index': 'edit'}, 'disabled'),
    Input('notice-list-table', 'selectedRowKeys'),
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
    Output({'type': 'notice-operation-button', 'index': 'delete'}, 'disabled'),
    Input('notice-list-table', 'selectedRowKeys'),
    prevent_initial_call=True,
)


@app.callback(
    output=dict(
        modal=dict(
            visible=Output('notice-modal', 'visible', allow_duplicate=True),
            title=Output('notice-modal', 'title'),
        ),
        form_value=dict(
            notice_title=Output('notice-notice_title', 'value'),
            notice_type=Output('notice-notice_type', 'value'),
            status=Output('notice-status', 'value'),
            notice_content=Output('notice-content', 'htmlValue'),
            editor_key=Output('notice-content', 'key'),
        ),
        form_validate=[
            Output(
                'notice-notice_title-form-item',
                'validateStatus',
                allow_duplicate=True,
            ),
            Output(
                'notice-notice_type-form-item',
                'validateStatus',
                allow_duplicate=True,
            ),
            Output(
                'notice-notice_title-form-item', 'help', allow_duplicate=True
            ),
            Output(
                'notice-notice_type-form-item', 'help', allow_duplicate=True
            ),
        ],
        other=dict(
            edit_row_info=Output('notice-edit-id-store', 'data'),
            modal_type=Output('notice-modal_type-store', 'data'),
        ),
    ),
    inputs=dict(
        operation_click=Input(
            {'type': 'notice-operation-button', 'index': ALL}, 'nClicks'
        ),
        button_click=Input('notice-list-table', 'nClicksButton'),
    ),
    state=dict(
        selected_row_keys=State('notice-list-table', 'selectedRowKeys'),
        clicked_content=State('notice-list-table', 'clickedContent'),
        recently_button_clicked_row=State(
            'notice-list-table', 'recentlyButtonClickedRow'
        ),
    ),
    prevent_initial_call=True,
)
def add_edit_notice_modal(
    operation_click,
    button_click,
    selected_row_keys,
    clicked_content,
    recently_button_clicked_row,
):
    """
    显示新增或编辑通知公告弹窗回调
    """
    trigger_id = ctx.triggered_id
    if (
        trigger_id == {'index': 'add', 'type': 'notice-operation-button'}
        or trigger_id == {'index': 'edit', 'type': 'notice-operation-button'}
        or (trigger_id == 'notice-list-table' and clicked_content == '修改')
    ):
        if trigger_id == {'index': 'add', 'type': 'notice-operation-button'}:
            return dict(
                modal=dict(visible=True, title='新增通知公告'),
                form_value=dict(
                    notice_title=None,
                    notice_type=SysNoticeTypeConstant.NOTICE,
                    status=SysNoticeStatusConstant.NORMAL,
                    notice_content=None,
                    editor_key=str(uuid.uuid4()),
                ),
                form_validate=[None] * 4,
                other=dict(
                    edit_row_info=None,
                    modal_type={'type': 'add'},
                ),
            )
        elif trigger_id == {
            'index': 'edit',
            'type': 'notice-operation-button',
        } or (trigger_id == 'notice-list-table' and clicked_content == '修改'):
            if trigger_id == {
                'index': 'edit',
                'type': 'notice-operation-button',
            }:
                notice_id = int(','.join(selected_row_keys))
            else:
                notice_id = int(recently_button_clicked_row['key'])
            notice_info_res = NoticeApi.get_notice(notice_id=notice_id)
            notice_info = notice_info_res['data']
            notice_content = notice_info.get('notice_content')

            return dict(
                modal=dict(visible=True, title='编辑通知公告'),
                form_value=dict(
                    notice_title=notice_info.get('notice_title'),
                    notice_type=notice_info.get('notice_type'),
                    status=notice_info.get('status'),
                    notice_content=StringUtil.insert_before_substring(
                        notice_content, '/profile/upload/', ApiConfig.BaseUrl
                    ),
                    editor_key=str(uuid.uuid4()),
                ),
                form_validate=[None] * 4,
                other=dict(
                    edit_row_info=notice_info if notice_info else None,
                    modal_type={'type': 'edit'},
                ),
            )

        return dict(
            modal=dict(visible=no_update, title=no_update),
            form_value=dict(
                notice_title=no_update,
                notice_type=no_update,
                status=no_update,
                notice_content=no_update,
                editor_key=no_update,
            ),
            form_validate=[no_update] * 4,
            other=dict(
                edit_row_info=None,
                modal_type=None,
            ),
        )

    raise PreventUpdate


@app.callback(
    output=dict(
        notice_title_form_status=Output(
            'notice-notice_title-form-item',
            'validateStatus',
            allow_duplicate=True,
        ),
        notice_type_form_status=Output(
            'notice-notice_type-form-item',
            'validateStatus',
            allow_duplicate=True,
        ),
        notice_title_form_help=Output(
            'notice-notice_title-form-item', 'help', allow_duplicate=True
        ),
        notice_type_form_help=Output(
            'notice-notice_type-form-item', 'help', allow_duplicate=True
        ),
        modal_visible=Output('notice-modal', 'visible'),
        operations=Output(
            'notice-operations-store', 'data', allow_duplicate=True
        ),
    ),
    inputs=dict(confirm_trigger=Input('notice-modal', 'okCounts')),
    state=dict(
        modal_type=State('notice-modal_type-store', 'data'),
        edit_row_info=State('notice-edit-id-store', 'data'),
        notice_title=State('notice-notice_title', 'value'),
        notice_type=State('notice-notice_type', 'value'),
        status=State('notice-status', 'value'),
        notice_content=State('notice-content', 'htmlValue'),
    ),
    running=[[Output('notice-modal', 'confirmLoading'), True, False]],
    prevent_initial_call=True,
)
def notice_confirm(
    confirm_trigger,
    modal_type,
    edit_row_info,
    notice_title,
    notice_type,
    status,
    notice_content,
):
    """
    新增或编辑通知公告弹窗确认回调，实现新增或编辑操作
    """
    if confirm_trigger:
        if all(
            ValidateUtil.not_empty(item)
            for item in [notice_title, notice_type]
        ):
            params_add = dict(
                notice_title=notice_title,
                notice_type=notice_type,
                status=status,
                notice_content=notice_content.replace(ApiConfig.BaseUrl, ''),
            )
            params_edit = dict(
                notice_id=edit_row_info.get('notice_id')
                if edit_row_info
                else None,
                notice_title=notice_title,
                notice_type=notice_type,
                status=status,
                notice_content=notice_content.replace(ApiConfig.BaseUrl, ''),
            )
            modal_type = modal_type.get('type')
            if modal_type == 'add':
                NoticeApi.add_notice(params_add)
            if modal_type == 'edit':
                NoticeApi.update_notice(params_edit)
            if modal_type == 'add':
                MessageManager.success(content='新增成功')

                return dict(
                    notice_title_form_status=None,
                    notice_type_form_status=None,
                    notice_title_form_help=None,
                    notice_type_form_help=None,
                    modal_visible=False,
                    operations={'type': 'add'},
                )
            if modal_type == 'edit':
                MessageManager.success(content='编辑成功')

                return dict(
                    notice_title_form_status=None,
                    notice_type_form_status=None,
                    notice_title_form_help=None,
                    notice_type_form_help=None,
                    modal_visible=False,
                    operations={'type': 'edit'},
                )

            return dict(
                notice_title_form_status=None,
                notice_type_form_status=None,
                notice_title_form_help=None,
                notice_type_form_help=None,
                modal_visible=no_update,
                operations=no_update,
            )

        return dict(
            notice_title_form_status=None
            if ValidateUtil.not_empty(notice_title)
            else 'error',
            notice_type_form_status=None
            if ValidateUtil.not_empty(notice_type)
            else 'error',
            notice_title_form_help=None
            if ValidateUtil.not_empty(notice_title)
            else '请输入公告标题！',
            notice_type_form_help=None
            if ValidateUtil.not_empty(notice_type)
            else '请输入公告类型！',
            modal_visible=no_update,
            operations=no_update,
        )

    raise PreventUpdate


@app.callback(
    [
        Output('notice-delete-text', 'children'),
        Output('notice-delete-confirm-modal', 'visible'),
        Output('notice-delete-ids-store', 'data'),
    ],
    [
        Input({'type': 'notice-operation-button', 'index': ALL}, 'nClicks'),
        Input('notice-list-table', 'nClicksButton'),
    ],
    [
        State('notice-list-table', 'selectedRowKeys'),
        State('notice-list-table', 'clickedContent'),
        State('notice-list-table', 'recentlyButtonClickedRow'),
    ],
    prevent_initial_call=True,
)
def notice_delete_modal(
    operation_click,
    button_click,
    selected_row_keys,
    clicked_content,
    recently_button_clicked_row,
):
    """
    显示删除通知公告二次确认弹窗回调
    """
    trigger_id = ctx.triggered_id
    if trigger_id == {'index': 'delete', 'type': 'notice-operation-button'} or (
        trigger_id == 'notice-list-table' and clicked_content == '删除'
    ):
        trigger_id = ctx.triggered_id

        if trigger_id == {'index': 'delete', 'type': 'notice-operation-button'}:
            notice_ids = ','.join(selected_row_keys)
        else:
            if clicked_content == '删除':
                notice_ids = recently_button_clicked_row['key']
            else:
                return no_update

        return [f'是否确认删除序号为{notice_ids}的通知公告？', True, notice_ids]

    raise PreventUpdate


@app.callback(
    Output('notice-operations-store', 'data', allow_duplicate=True),
    Input('notice-delete-confirm-modal', 'okCounts'),
    State('notice-delete-ids-store', 'data'),
    prevent_initial_call=True,
)
def notice_delete_confirm(delete_confirm, notice_ids_data):
    """
    删除岗通知公告弹窗确认回调，实现删除操作
    """
    if delete_confirm:
        params = notice_ids_data
        NoticeApi.del_notice(params)
        MessageManager.success(content='删除成功')

        return ({'type': 'delete'},)

    raise PreventUpdate
