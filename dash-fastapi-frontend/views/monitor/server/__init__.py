import feffery_antd_components as fac
from dash import html
from api.monitor.server import ServerApi


def render(*args, **kwargs):
    server_info_res = ServerApi.get_server()
    server_info = server_info_res.get('data')
    cpu = [
        dict(name=key, value=value)
        for key, value in server_info.get('cpu').items()
    ]
    for item in cpu:
        if item.get('name') == 'cpu_num':
            item['name'] = '核心数'
        if item.get('name') == 'used':
            item['name'] = '用户使用率'
            item['value'] = f"{item['value']}%"
        if item.get('name') == 'sys':
            item['name'] = '系统使用率'
            item['value'] = f"{item['value']}%"
        if item.get('name') == 'free':
            item['name'] = '当前空闲率'
            item['value'] = f"{item['value']}%"
    mem = [
        dict(name=key, value=value)
        for key, value in server_info.get('mem').items()
    ]
    for item in mem:
        if item.get('name') == 'total':
            item['name'] = '总内存'
        if item.get('name') == 'used':
            item['name'] = '已用内存'
        if item.get('name') == 'free':
            item['name'] = '剩余内存'
        if item.get('name') == 'usage':
            item['name'] = '使用率'
            item['value'] = f"{item['value']}%"
    sys = server_info.get('sys')
    py = server_info.get('py')
    sys_files = server_info.get('sys_files')

    return [
        html.Div(
            [
                fac.AntdRow(
                    [
                        fac.AntdCol(
                            fac.AntdCard(
                                [
                                    fac.AntdTable(
                                        data=cpu,
                                        columns=[
                                            {
                                                'dataIndex': 'name',
                                                'title': '属性',
                                                'renderOptions': {
                                                    'renderType': 'ellipsis'
                                                },
                                            },
                                            {
                                                'dataIndex': 'value',
                                                'title': '值',
                                                'renderOptions': {
                                                    'renderType': 'ellipsis'
                                                },
                                            },
                                        ],
                                        bordered=False,
                                        pagination={'hideOnSinglePage': True},
                                    )
                                ],
                                title=html.Div(
                                    [
                                        fac.AntdIcon(icon='antd-box-plot'),
                                        fac.AntdText(
                                            'CPU', style={'marginLeft': '10px'}
                                        ),
                                    ]
                                ),
                                size='small',
                                style={
                                    'boxShadow': 'rgba(99, 99, 99, 0.2) 0px 2px 8px 0px'
                                },
                            ),
                            span=12,
                        ),
                        fac.AntdCol(
                            fac.AntdCard(
                                [
                                    fac.AntdTable(
                                        data=mem,
                                        columns=[
                                            {
                                                'dataIndex': 'name',
                                                'title': '属性',
                                                'renderOptions': {
                                                    'renderType': 'ellipsis'
                                                },
                                            },
                                            {
                                                'dataIndex': 'value',
                                                'title': '内存',
                                                'renderOptions': {
                                                    'renderType': 'ellipsis'
                                                },
                                            },
                                        ],
                                        bordered=False,
                                        pagination={'hideOnSinglePage': True},
                                    )
                                ],
                                title=html.Div(
                                    [
                                        fac.AntdIcon(icon='antd-file-text'),
                                        fac.AntdText(
                                            '内存', style={'marginLeft': '10px'}
                                        ),
                                    ]
                                ),
                                size='small',
                                style={
                                    'boxShadow': 'rgba(99, 99, 99, 0.2) 0px 2px 8px 0px'
                                },
                            ),
                            span=12,
                        ),
                    ],
                    gutter=20,
                ),
                fac.AntdRow(
                    [
                        fac.AntdCol(
                            fac.AntdCard(
                                [
                                    fac.AntdDescriptions(
                                        [
                                            fac.AntdDescriptionItem(
                                                sys.get('computer_name'),
                                                label='服务器名称',
                                            ),
                                            fac.AntdDescriptionItem(
                                                sys.get('os_name'),
                                                label='操作系统',
                                            ),
                                            fac.AntdDescriptionItem(
                                                sys.get('computer_ip'),
                                                label='服务器IP',
                                            ),
                                            fac.AntdDescriptionItem(
                                                sys.get('os_arch'),
                                                label='系统架构',
                                            ),
                                        ],
                                        bordered=True,
                                        column=2,
                                        styles={'label': {'textAlign': 'center'}},
                                        style={
                                            'width': '100%',
                                            'textAlign': 'center',
                                            'marginLeft': '20px',
                                            'marginRight': '20px',
                                        },
                                    )
                                ],
                                title=html.Div(
                                    [
                                        fac.AntdIcon(icon='antd-desktop'),
                                        fac.AntdText(
                                            '服务器信息',
                                            style={'marginLeft': '10px'},
                                        ),
                                    ]
                                ),
                                size='small',
                                style={
                                    'boxShadow': 'rgba(99, 99, 99, 0.2) 0px 2px 8px 0px'
                                },
                            ),
                            span=24,
                        ),
                    ],
                    gutter=20,
                    style={'marginTop': '20px', 'marginBottom': '20px'},
                ),
                fac.AntdRow(
                    [
                        fac.AntdCol(
                            fac.AntdCard(
                                [
                                    fac.AntdDescriptions(
                                        [
                                            fac.AntdDescriptionItem(
                                                py.get('name'),
                                                label='Python名称',
                                            ),
                                            fac.AntdDescriptionItem(
                                                py.get('version'),
                                                label='Python版本',
                                            ),
                                            fac.AntdDescriptionItem(
                                                py.get('start_time'),
                                                label='启动时间',
                                            ),
                                            fac.AntdDescriptionItem(
                                                py.get('run_time'),
                                                label='运行时长',
                                            ),
                                            fac.AntdDescriptionItem(
                                                py.get('home'), label='安装路径'
                                            ),
                                            fac.AntdDescriptionItem(
                                                sys.get('user_dir'),
                                                label='项目路径',
                                            ),
                                        ],
                                        bordered=True,
                                        column=2,
                                        styles={'label': {'textAlign': 'center'}},
                                        style={
                                            'width': '100%',
                                            'textAlign': 'center',
                                            'marginLeft': '20px',
                                            'marginRight': '20px',
                                        },
                                    )
                                ],
                                title=html.Div(
                                    [
                                        fac.AntdIcon(icon='antd-filter'),
                                        fac.AntdText(
                                            'Python解释器信息',
                                            style={'marginLeft': '10px'},
                                        ),
                                    ]
                                ),
                                size='small',
                                style={
                                    'boxShadow': 'rgba(99, 99, 99, 0.2) 0px 2px 8px 0px'
                                },
                            ),
                            span=24,
                        ),
                    ],
                    gutter=20,
                    style={'marginTop': '20px', 'marginBottom': '20px'},
                ),
                fac.AntdRow(
                    [
                        fac.AntdCol(
                            fac.AntdCard(
                                [
                                    fac.AntdTable(
                                        data=sys_files,
                                        columns=[
                                            {
                                                'dataIndex': 'dir_name',
                                                'title': '盘符路径',
                                                'renderOptions': {
                                                    'renderType': 'ellipsis'
                                                },
                                            },
                                            {
                                                'dataIndex': 'sys_type_name',
                                                'title': '文件系统',
                                                'renderOptions': {
                                                    'renderType': 'ellipsis'
                                                },
                                            },
                                            {
                                                'dataIndex': 'type_name',
                                                'title': '盘符名称',
                                                'renderOptions': {
                                                    'renderType': 'ellipsis'
                                                },
                                            },
                                            {
                                                'dataIndex': 'total',
                                                'title': '总大小',
                                                'renderOptions': {
                                                    'renderType': 'ellipsis'
                                                },
                                            },
                                            {
                                                'dataIndex': 'free',
                                                'title': '可用大小',
                                                'renderOptions': {
                                                    'renderType': 'ellipsis'
                                                },
                                            },
                                            {
                                                'dataIndex': 'used',
                                                'title': '已用大小',
                                                'renderOptions': {
                                                    'renderType': 'ellipsis'
                                                },
                                            },
                                            {
                                                'dataIndex': 'usage',
                                                'title': '已用百分比',
                                                'renderOptions': {
                                                    'renderType': 'ellipsis'
                                                },
                                            },
                                        ],
                                        bordered=False,
                                        pagination={'hideOnSinglePage': True},
                                    )
                                ],
                                title=html.Div(
                                    [
                                        fac.AntdIcon(icon='antd-file-sync'),
                                        fac.AntdText(
                                            '磁盘状态',
                                            style={'marginLeft': '10px'},
                                        ),
                                    ]
                                ),
                                size='small',
                                style={
                                    'boxShadow': 'rgba(99, 99, 99, 0.2) 0px 2px 8px 0px'
                                },
                            ),
                            span=24,
                        ),
                    ],
                    gutter=20,
                    style={'marginTop': '20px', 'marginBottom': '20px'},
                ),
            ],
        ),
    ]
