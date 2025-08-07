import feffery_antd_components as fac
import time
import uuid
from dash import ctx, no_update
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
from typing import Dict
from api.system.menu import MenuApi
from config.constant import MenuConstant, SysNormalDisableConstant
from server import app
from utils.dict_util import DictManager
from utils.feedback_util import MessageManager
from utils.permission_util import PermissionManager
from utils.time_format_util import TimeFormatUtil
from utils.tree_util import TreeUtil
from views.system.menu.components import button_type, content_type, menu_type


def generate_menu_table(query_params: Dict):
    """
    根据查询参数获取菜单表格数据及展开信息

    :param query_params: 查询参数
    :return: 菜单表格数据及展开信息
    """
    table_info = MenuApi.list_menu(query_params)
    default_expanded_row_keys = []
    table_data = table_info['data']
    for item in table_data:
        default_expanded_row_keys.append(str(item['menu_id']))
        item['create_time'] = TimeFormatUtil.format_time(
            item.get('create_time')
        )
        item['key'] = str(item['menu_id'])
        item['icon'] = [
            {
                'type': 'link',
                'icon': item['icon'],
                'disabled': True,
                'style': {'color': 'rgba(0, 0, 0, 0.8)'},
            },
        ]
        if item['status'] == SysNormalDisableConstant.DISABLE:
            item['operation'] = [
                {'content': '修改', 'type': 'link', 'icon': 'antd-edit'}
                if PermissionManager.check_perms('system:menu:edit')
                else {},
                {
                    'content': '删除',
                    'type': 'link',
                    'icon': 'antd-delete',
                }
                if PermissionManager.check_perms('system:menu:remove')
                else {},
            ]
        else:
            item['operation'] = [
                {'content': '修改', 'type': 'link', 'icon': 'antd-edit'}
                if PermissionManager.check_perms('system:menu:edit')
                else {},
                {'content': '新增', 'type': 'link', 'icon': 'antd-plus'}
                if PermissionManager.check_perms('system:menu:add')
                else {},
                {
                    'content': '删除',
                    'type': 'link',
                    'icon': 'antd-delete',
                }
                if PermissionManager.check_perms('system:menu:remove')
                else {},
            ]
        item['status'] = DictManager.get_dict_tag(
            dict_type='sys_normal_disable', dict_value=item.get('status')
        )
    table_data_new = TreeUtil.list_to_tree(table_data, 'menu_id', 'parent_id')

    return [table_data_new, default_expanded_row_keys]


@app.callback(
    output=dict(
        menu_table_data=Output('menu-list-table', 'data', allow_duplicate=True),
        menu_table_key=Output('menu-list-table', 'key'),
        menu_table_defaultexpandedrowkeys=Output(
            'menu-list-table', 'defaultExpandedRowKeys'
        ),
        fold_click=Output('menu-fold', 'nClicks'),
    ),
    inputs=dict(
        search_click=Input('menu-search', 'nClicks'),
        refresh_click=Input('menu-refresh', 'nClicks'),
        operations=Input('menu-operations-store', 'data'),
        fold_click=Input('menu-fold', 'nClicks'),
    ),
    state=dict(
        menu_name=State('menu-menu_name-input', 'value'),
        status_select=State('menu-status-select', 'value'),
        in_default_expanded_row_keys=State(
            'menu-list-table', 'defaultExpandedRowKeys'
        ),
    ),
    prevent_initial_call=True,
)
def get_menu_table_data(
    search_click,
    refresh_click,
    operations,
    fold_click,
    menu_name,
    status_select,
    in_default_expanded_row_keys,
):
    """
    获取菜单表格数据回调（进行表格相关增删查改操作后均会触发此回调）
    """

    query_params = dict(menu_name=menu_name, status=status_select)
    if search_click or refresh_click or operations or fold_click:
        table_data, default_expanded_row_keys = generate_menu_table(
            query_params
        )
        if fold_click:
            if not in_default_expanded_row_keys:
                return dict(
                    menu_table_data=table_data,
                    menu_table_key=str(uuid.uuid4()),
                    menu_table_defaultexpandedrowkeys=default_expanded_row_keys,
                    fold_click=None,
                )

        return dict(
            menu_table_data=table_data,
            menu_table_key=str(uuid.uuid4()),
            menu_table_defaultexpandedrowkeys=[],
            fold_click=None,
        )

    return dict(
        menu_table_data=no_update,
        menu_table_key=no_update,
        menu_table_defaultexpandedrowkeys=no_update,
        fold_click=None,
    )


# 重置菜单搜索表单数据回调
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
        Output('menu-menu_name-input', 'value'),
        Output('menu-status-select', 'value'),
        Output('menu-operations-store', 'data'),
    ],
    Input('menu-reset', 'nClicks'),
    prevent_initial_call=True,
)


# 隐藏/显示菜单搜索表单回调
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
        Output('menu-search-form-container', 'hidden'),
        Output('menu-hidden-tooltip', 'title'),
    ],
    Input('menu-hidden', 'nClicks'),
    State('menu-search-form-container', 'hidden'),
    prevent_initial_call=True,
)


@app.callback(
    [Output('menu-icon', 'value'), Output('menu-icon', 'prefix')],
    Input('icon-category', 'value'),
    prevent_initial_call=True,
)
def get_select_icon(icon):
    """
    获取新增或编辑表单中选择的icon回调
    """
    if icon:
        return [icon, fac.AntdIcon(icon=icon)]

    raise PreventUpdate


@app.callback(
    output=dict(
        modal=dict(
            visible=Output('menu-modal', 'visible', allow_duplicate=True),
            title=Output('menu-modal', 'title'),
        ),
        form_value=dict(
            parent_tree=Output('menu-parent_id', 'treeData'),
            parent_id=Output('menu-parent_id', 'value'),
            menu_type=Output('menu-menu_type', 'value'),
            icon=Output('menu-icon', 'value', allow_duplicate=True),
            icon_prefix=Output('menu-icon', 'prefix', allow_duplicate=True),
            icon_category=Output('icon-category', 'value'),
            menu_name=Output('menu-menu_name', 'value'),
            order_num=Output('menu-order_num', 'value'),
        ),
        form_validate=[
            Output(
                'menu-parent_id-form-item',
                'validateStatus',
                allow_duplicate=True,
            ),
            Output(
                'menu-menu_name-form-item',
                'validateStatus',
                allow_duplicate=True,
            ),
            Output(
                'menu-order_num-form-item',
                'validateStatus',
                allow_duplicate=True,
            ),
            Output('menu-parent_id-form-item', 'help', allow_duplicate=True),
            Output('menu-menu_name-form-item', 'help', allow_duplicate=True),
            Output('menu-order_num-form-item', 'help', allow_duplicate=True),
        ],
        other=dict(
            edit_row_info=Output('menu-edit-id-store', 'data'),
            modal_type=Output('menu-modal_type-store', 'data'),
        ),
    ),
    inputs=dict(
        operation_click=Input(
            {'type': 'menu-operation-button', 'index': ALL}, 'nClicks'
        ),
        button_click=Input('menu-list-table', 'nClicksButton'),
    ),
    state=dict(
        clicked_content=State('menu-list-table', 'clickedContent'),
        recently_button_clicked_row=State(
            'menu-list-table', 'recentlyButtonClickedRow'
        ),
    ),
    prevent_initial_call=True,
)
def add_edit_menu_modal(
    operation_click, button_click, clicked_content, recently_button_clicked_row
):
    """
    显示新增或编辑菜单弹窗回调
    """
    trigger_id = ctx.triggered_id
    if trigger_id == {'index': 'add', 'type': 'menu-operation-button'} or (
        trigger_id == 'menu-list-table' and clicked_content != '删除'
    ):
        menu_params = dict(menu_name='')
        tree_info = MenuApi.list_menu(menu_params)
        tree_data = [dict(title='主类目', value='0', key='0', children=[])]
        tree_data[0]['children'] = TreeUtil.list_to_tree_select(
            tree_info['data'], 'menu_name', 'menu_id', 'menu_id', 'parent_id'
        )

        if trigger_id == {'index': 'add', 'type': 'menu-operation-button'}:
            return dict(
                modal=dict(visible=True, title='新增菜单'),
                form_value=dict(
                    parent_tree=tree_data,
                    parent_id='0',
                    menu_type=MenuConstant.TYPE_DIR,
                    icon=None,
                    icon_prefix=None,
                    icon_category=None,
                    menu_name=None,
                    order_num=None,
                ),
                form_validate=[None] * 6,
                other=dict(
                    edit_row_info=None,
                    modal_type={'type': 'add'},
                ),
            )
        elif trigger_id == 'menu-list-table' and clicked_content == '新增':
            return dict(
                modal=dict(visible=True, title='新增菜单'),
                form_value=dict(
                    parent_tree=tree_data,
                    parent_id=str(recently_button_clicked_row['key']),
                    menu_type=MenuConstant.TYPE_DIR,
                    icon=None,
                    icon_prefix=None,
                    icon_category=None,
                    menu_name=None,
                    order_num=None,
                ),
                form_validate=[None] * 6,
                other=dict(
                    edit_row_info=None,
                    modal_type={'type': 'add'},
                ),
            )
        elif trigger_id == 'menu-list-table' and clicked_content == '修改':
            menu_id = int(recently_button_clicked_row['key'])
            menu_info_res = MenuApi.get_menu(menu_id=menu_id)
            if menu_info_res['code'] == 200:
                menu_info = menu_info_res['data']
                return dict(
                    modal=dict(visible=True, title='编辑菜单'),
                    form_value=dict(
                        parent_tree=tree_data,
                        parent_id=str(menu_info.get('parent_id')),
                        menu_type=menu_info.get('menu_type'),
                        icon=menu_info.get('icon'),
                        icon_prefix=fac.AntdIcon(icon=menu_info.get('icon')),
                        icon_category=menu_info.get('icon'),
                        menu_name=menu_info.get('menu_name'),
                        order_num=menu_info.get('order_num'),
                    ),
                    form_validate=[None] * 6,
                    other=dict(
                        edit_row_info=menu_info,
                        modal_type={'type': 'edit'},
                    ),
                )

        return dict(
            modal=dict(visible=no_update, title=no_update),
            form_value=dict(
                parent_tree=no_update,
                parent_id=no_update,
                menu_type=no_update,
                icon=no_update,
                icon_prefix=no_update,
                icon_category=no_update,
                menu_name=no_update,
                order_num=no_update,
            ),
            form_validate=[no_update] * 6,
            other=dict(
                edit_row_info=None,
                modal_type=None,
            ),
        )

    raise PreventUpdate


@app.callback(
    [
        Output('content-by-menu-type', 'children'),
        Output('content-by-menu-type', 'key'),
        Output('menu-modal-menu-type-store', 'data'),
    ],
    Input('menu-menu_type', 'value'),
    prevent_initial_call=True,
)
def get_bottom_content(menu_value):
    """
    根据不同菜单类型渲染不同的子区域
    """
    if menu_value == MenuConstant.TYPE_DIR:
        return [
            content_type.render(),
            str(uuid.uuid4()),
            {'type': MenuConstant.TYPE_DIR},
        ]

    elif menu_value == MenuConstant.TYPE_MENU:
        return [
            menu_type.render(),
            str(uuid.uuid4()),
            {'type': MenuConstant.TYPE_MENU},
        ]

    elif menu_value == MenuConstant.TYPE_BUTTON:
        return [
            button_type.render(),
            str(uuid.uuid4()),
            {'type': MenuConstant.TYPE_BUTTON},
        ]

    raise PreventUpdate


@app.callback(
    [
        Output('menu-modal-M-trigger', 'data'),
        Output('menu-modal-C-trigger', 'data'),
        Output('menu-modal-F-trigger', 'data'),
    ],
    Input('menu-modal', 'okCounts'),
    State('menu-modal-menu-type-store', 'data'),
)
def modal_confirm_trigger(confirm, menu_type):
    """
    增加触发器，根据不同菜单类型触发不同的回调，解决组件不存在回调异常的问题
    """
    if confirm:
        if menu_type.get('type') == MenuConstant.TYPE_DIR:
            return [{'timestamp': time.time()}, no_update, no_update]
        if menu_type.get('type') == MenuConstant.TYPE_MENU:
            return [no_update, {'timestamp': time.time()}, no_update]

        if menu_type.get('type') == MenuConstant.TYPE_BUTTON:
            return [no_update, no_update, {'timestamp': time.time()}]

    raise PreventUpdate


@app.callback(
    [
        Output('menu-delete-text', 'children'),
        Output('menu-delete-confirm-modal', 'visible'),
        Output('menu-delete-ids-store', 'data'),
    ],
    [Input('menu-list-table', 'nClicksButton')],
    [
        State('menu-list-table', 'clickedContent'),
        State('menu-list-table', 'recentlyButtonClickedRow'),
    ],
    prevent_initial_call=True,
)
def menu_delete_modal(
    button_click, clicked_content, recently_button_clicked_row
):
    """
    显示删除菜单二次确认弹窗回调
    """
    if button_click:
        if clicked_content == '删除':
            menu_ids = recently_button_clicked_row['key']
        else:
            raise PreventUpdate

        return [
            f'是否确认删除菜单编号为{menu_ids}的菜单？',
            True,
            menu_ids,
        ]

    raise PreventUpdate


@app.callback(
    Output('menu-operations-store', 'data', allow_duplicate=True),
    Input('menu-delete-confirm-modal', 'okCounts'),
    State('menu-delete-ids-store', 'data'),
    prevent_initial_call=True,
)
def menu_delete_confirm(delete_confirm, menu_ids_data):
    """
    删除菜单弹窗确认回调，实现删除操作
    """
    if delete_confirm:
        params = menu_ids_data
        MenuApi.del_menu(params)
        MessageManager.success(content='删除成功')

        return {'type': 'delete'}

    raise PreventUpdate
