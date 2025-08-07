import feffery_antd_components as fac
import feffery_utils_components as fuc
from dash import dcc, html
from api.monitor.cache import CacheApi
from callbacks.monitor_c.cache_c import control_c  # noqa: F401


def render(*args, **kwargs):
    cache_info_res = CacheApi.get_cache()
    cache_info = cache_info_res.get('data')
    command_stats = cache_info.get('command_stats')
    db_size = cache_info.get('db_size')
    info = cache_info.get('info')

    return [
        dcc.Store(
            id='init-echarts-data-container',
            data=dict(
                command_stats=command_stats,
                used_memory_human=info.get('used_memory_human'),
            ),
        ),
        dcc.Store(id='echarts-data-container'),
        fuc.FefferyTimeout(id='init-echarts-timeout', delay=500),
        html.Div(
            [
                fac.AntdRow(
                    [
                        fac.AntdCol(
                            fac.AntdCard(
                                [
                                    fac.AntdDescriptions(
                                        [
                                            fac.AntdDescriptionItem(
                                                info.get('redis_version'),
                                                label='Redis版本',
                                            ),
                                            fac.AntdDescriptionItem(
                                                '单机'
                                                if info.get('redis_mode')
                                                == 'standalone'
                                                else '集群',
                                                label='运行模式',
                                            ),
                                            fac.AntdDescriptionItem(
                                                info.get('tcp_port'),
                                                label='端口',
                                            ),
                                            fac.AntdDescriptionItem(
                                                info.get('connected_clients'),
                                                label='客户端数',
                                            ),
                                            fac.AntdDescriptionItem(
                                                info.get('uptime_in_days'),
                                                label='运行时间(天)',
                                            ),
                                            fac.AntdDescriptionItem(
                                                info.get('used_memory_human'),
                                                label='使用内存',
                                            ),
                                            fac.AntdDescriptionItem(
                                                info.get(
                                                    'used_cpu_user_children'
                                                ),
                                                label='使用CPU',
                                            ),
                                            fac.AntdDescriptionItem(
                                                info.get('maxmemory_human'),
                                                label='内存配置',
                                            ),
                                            fac.AntdDescriptionItem(
                                                '否'
                                                if info.get('aof_enabled') == 0
                                                else '是',
                                                label='AOF是否开启',
                                            ),
                                            fac.AntdDescriptionItem(
                                                info.get(
                                                    'rdb_last_bgsave_status'
                                                ),
                                                label='RDB是否成功',
                                            ),
                                            fac.AntdDescriptionItem(
                                                db_size, label='Key数量'
                                            ),
                                            fac.AntdDescriptionItem(
                                                f'{info.get("instantaneous_input_kbps")}kps/{info.get("instantaneous_output_kbps")}kps',
                                                label='网络入口/出口',
                                            ),
                                        ],
                                        bordered=True,
                                        column=4,
                                        styles={
                                            'label': {
                                                'fontWeight': 600,
                                                'textAlign': 'center',
                                            }
                                        },
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
                                            '基本信息',
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
                ),
                fac.AntdRow(
                    [
                        fac.AntdCol(
                            fac.AntdCard(
                                [
                                    html.Div(
                                        id='command-stats-charts-container',
                                        style={
                                            'height': '420px',
                                            'width': '100%',
                                        },
                                    ),
                                ],
                                title=html.Div(
                                    [
                                        fac.AntdIcon(icon='antd-pie-chart'),
                                        fac.AntdText(
                                            '命令统计',
                                            style={'marginLeft': '10px'},
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
                                    html.Div(
                                        id='memory-charts-container',
                                        style={
                                            'height': '420px',
                                            'width': '100%',
                                        },
                                    ),
                                ],
                                title=html.Div(
                                    [
                                        fac.AntdIcon(icon='antd-compass'),
                                        fac.AntdText(
                                            '内存信息',
                                            style={'marginLeft': '10px'},
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
                    style={'marginTop': '20px', 'marginBottom': '20px'},
                ),
            ],
        ),
    ]
