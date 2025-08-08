from dash import dcc, html


def render_store_container():
    return html.Div(
        [
            # 应用主题颜色存储容器
            dcc.Store(id='system-app-primary-color-container', data='#1677ff'),
            dcc.Store(
                id='custom-app-primary-color-container', storage_type='session'
            ),
            # token存储容器
            dcc.Store(id='token-container', storage_type='session'),
            # 当前路由存储容器
            dcc.Store(id='current-pathname-container'),
            # 路由列表存储容器
            dcc.Store(id='router-list-container'),
        ]
    )
