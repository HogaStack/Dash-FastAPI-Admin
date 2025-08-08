import feffery_antd_components as fac
import feffery_utils_components as fuc
from dash import dcc, html
from callbacks import app_c, router_c  # noqa: F401
from config.env import AppConfig
from server import app
from store.store import render_store_container


app.layout = html.Div(
    [
        # 注入url监听
        fuc.FefferyLocation(id='url-container'),
        # 用于回调pathname信息
        dcc.Location(id='dcc-url', refresh=False),
        # 注入全局配置容器和页面内容挂载点
        fac.AntdConfigProvider(
            html.Div(id='app-mount'),
            id='app-config-provider',
        ),
        # 注入快捷搜索面板
        fuc.FefferyShortcutPanel(
            id='search-panel',
            data=[],
            placeholder='输入你想要搜索的菜单...',
            panelStyles={'accentColor': '#1890ff', 'zIndex': 99999},
        ),
        # 注入全局store容器
        render_store_container(),
        # 重定向容器
        html.Div(id='redirect-container'),
        # 登录消息失效对话框提示
        fac.AntdModal(
            html.Div(
                [
                    fac.AntdIcon(
                        icon='fc-high-priority', style={'font-size': '28px'}
                    ),
                    fac.AntdText(
                        '登录状态已过期，您可以继续留在该页面，或者重新登录',
                        style={'margin-left': '5px'},
                    ),
                ]
            ),
            id='token-invalid-modal',
            visible=False,
            title='系统提示',
            okText='重新登录',
            renderFooter=True,
            centered=True,
        ),
        # 注入全局消息提示容器
        fac.Fragment(id='global-message-container'),
        # 注入全局通知信息容器
        fac.Fragment(id='global-notification-container'),
    ]
)


if __name__ == '__main__':
    app.run(
        host=AppConfig.app_host,
        port=AppConfig.app_port,
        debug=AppConfig.app_debug,
    )
