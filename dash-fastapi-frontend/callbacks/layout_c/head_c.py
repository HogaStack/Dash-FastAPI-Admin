from dash import ctx, dcc, no_update
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from flask import session
from api.login import LoginApi
from server import app
from utils.cache_util import CacheManager
from utils.feedback_util import MessageManager


# 页首右侧个人中心选项卡回调
app.clientside_callback(
    """
    (nClicks, clickedKey) => {
        if (clickedKey == '退出登录') {
            return [
                window.dash_clientside.no_update,
                true,
                false
            ];
        } else if (clickedKey == '个人资料') {
            return [
                '/user/profile',
                false,
                false
            ];
        } else if ( clickedKey == '布局设置') {
            return [
                window.dash_clientside.no_update,
                false,
                true
            ]
        }
        throw window.dash_clientside.PreventUpdate;
     }
    """,
    [
        Output('dcc-url', 'pathname', allow_duplicate=True),
        Output('logout-modal', 'visible'),
        Output('layout-setting-drawer', 'visible'),
    ],
    Input('index-header-dropdown', 'nClicks'),
    State('index-header-dropdown', 'clickedKey'),
    prevent_initial_call=True,
)


# 退出登录回调
@app.callback(
    [
        Output('redirect-container', 'children', allow_duplicate=True),
        Output('token-container', 'data', allow_duplicate=True),
    ],
    Input('logout-modal', 'okCounts'),
    prevent_initial_call=True,
)
def logout_confirm(okCounts):
    if okCounts:
        result = LoginApi.logout()
        if result['code'] == 200:
            session.clear()
            CacheManager.clear()

            return [dcc.Location(pathname='/login', id='index-redirect'), None]

    raise PreventUpdate


# 全局页面重载回调
app.clientside_callback(
    """
    (nClicks) => {
        return true;
    }
    """,
    Output('trigger-reload-output', 'reload', allow_duplicate=True),
    Input('index-reload', 'nClicks'),
    prevent_initial_call=True,
)


# 布局设置回调
app.clientside_callback(
    """
    (visible, custom_color) => {
        if (visible) {
            if (custom_color) {
                return custom_color;
            }
        }
        throw window.dash_clientside.PreventUpdate;
    }
    """,
    Output('hex-color-picker', 'color', allow_duplicate=True),
    Input('layout-setting-drawer', 'visible'),
    State('custom-app-primary-color-container', 'data'),
    prevent_initial_call=True,
)


@app.callback(
    [
        Output('selected-color-input', 'value'),
        Output('selected-color-input', 'style'),
    ],
    Input('hex-color-picker', 'color'),
    State('selected-color-input', 'style'),
    prevent_initial_call=True,
)
def show_selected_color(pick_color, old_style):
    return [pick_color, {**old_style, 'background': pick_color}]


@app.callback(
    [
        Output('custom-app-primary-color-container', 'data'),
        Output('hex-color-picker', 'color', allow_duplicate=True),
    ],
    [Input('save-setting', 'nClicks'), Input('reset-setting', 'nClicks')],
    [
        State('selected-color-input', 'value'),
        State('system-app-primary-color-container', 'data'),
    ],
    prevent_initial_call=True,
)
def save_rest_layout_setting(
    save_click, reset_click, picked_color, system_color
):
    if save_click or reset_click:
        trigger_id = ctx.triggered_id
        if trigger_id == 'save-setting':
            MessageManager.success(content='保存成功')
            return [picked_color, no_update]

        elif trigger_id == 'reset-setting':
            MessageManager.success(content='重置成功')
            return [None, system_color]

    raise PreventUpdate
