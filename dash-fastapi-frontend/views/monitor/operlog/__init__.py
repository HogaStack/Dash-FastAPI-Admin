import feffery_antd_components as fac
from dash import dcc, html
from callbacks.monitor_c import operlog_c  # noqa: F401
from components.ApiSelect import ApiSelect
from utils.permission_util import PermissionManager


def render(*args, **kwargs):
    return [
        # 用于导出成功后重置dcc.Download的状态，防止多次下载文件
        dcc.Store(id='operation_log-export-complete-judge-container'),
        # 绑定的导出组件
        dcc.Download(id='operation_log-export-container'),
        # 操作日志管理模块操作类型存储容器
        dcc.Store(id='operation_log-operations-store'),
        # 操作日志管理模块删除操作行key存储容器
        dcc.Store(id='operation_log-delete-ids-store'),
        fac.AntdRow(
            [
                fac.AntdCol(
                    [
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    html.Div(
                                        [
                                            fac.AntdForm(
                                                [
                                                    fac.AntdFormItem(
                                                        fac.AntdInput(
                                                            id='operation_log-title-input',
                                                            placeholder='请输入系统模块',
                                                            autoComplete='off',
                                                            allowClear=True,
                                                            style={
                                                                'width': 240
                                                            },
                                                        ),
                                                        label='系统模块',
                                                        style={
                                                            'paddingBottom': '10px'
                                                        },
                                                    ),
                                                    fac.AntdFormItem(
                                                        fac.AntdInput(
                                                            id='operation_log-oper_name-input',
                                                            placeholder='请输入操作人员',
                                                            autoComplete='off',
                                                            allowClear=True,
                                                            style={
                                                                'width': 240
                                                            },
                                                        ),
                                                        label='操作人员',
                                                        style={
                                                            'paddingBottom': '10px'
                                                        },
                                                    ),
                                                    fac.AntdFormItem(
                                                        ApiSelect(
                                                            dict_type='sys_oper_type',
                                                            id='operation_log-business_type-select',
                                                            placeholder='操作类型',
                                                            style={
                                                                'width': 240
                                                            },
                                                        ),
                                                        label='类型',
                                                        style={
                                                            'paddingBottom': '10px'
                                                        },
                                                    ),
                                                    fac.AntdFormItem(
                                                        ApiSelect(
                                                            dict_type='sys_common_status',
                                                            id='operation_log-status-select',
                                                            placeholder='操作状态',
                                                            style={
                                                                'width': 240
                                                            },
                                                        ),
                                                        label='状态',
                                                        style={
                                                            'paddingBottom': '10px'
                                                        },
                                                    ),
                                                    fac.AntdFormItem(
                                                        fac.AntdDateRangePicker(
                                                            id='operation_log-oper_time-range',
                                                            style={
                                                                'width': 240
                                                            },
                                                        ),
                                                        label='操作时间',
                                                        style={
                                                            'paddingBottom': '10px'
                                                        },
                                                    ),
                                                    fac.AntdFormItem(
                                                        fac.AntdButton(
                                                            '搜索',
                                                            id='operation_log-search',
                                                            type='primary',
                                                            icon=fac.AntdIcon(
                                                                icon='antd-search'
                                                            ),
                                                        ),
                                                        style={
                                                            'paddingBottom': '10px'
                                                        },
                                                    ),
                                                    fac.AntdFormItem(
                                                        fac.AntdButton(
                                                            '重置',
                                                            id='operation_log-reset',
                                                            icon=fac.AntdIcon(
                                                                icon='antd-sync'
                                                            ),
                                                        ),
                                                        style={
                                                            'paddingBottom': '10px'
                                                        },
                                                    ),
                                                ],
                                                layout='inline',
                                            )
                                        ],
                                        id='operation_log-search-form-container',
                                        hidden=False,
                                    ),
                                )
                            ]
                        ),
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    fac.AntdSpace(
                                        [
                                            fac.AntdButton(
                                                [
                                                    fac.AntdIcon(
                                                        icon='antd-delete'
                                                    ),
                                                    '删除',
                                                ],
                                                id={
                                                    'type': 'operation_log-operation-button',
                                                    'index': 'delete',
                                                },
                                                disabled=True,
                                                style={
                                                    'color': '#ff9292',
                                                    'background': '#ffeded',
                                                    'border-color': '#ffdbdb',
                                                },
                                            )
                                            if PermissionManager.check_perms(
                                                'monitor:operlog:remove'
                                            )
                                            else [],
                                            fac.AntdButton(
                                                [
                                                    fac.AntdIcon(
                                                        icon='antd-clear'
                                                    ),
                                                    '清空',
                                                ],
                                                id={
                                                    'type': 'operation_log-operation-button',
                                                    'index': 'clear',
                                                },
                                                style={
                                                    'color': '#ff9292',
                                                    'background': '#ffeded',
                                                    'border-color': '#ffdbdb',
                                                },
                                            )
                                            if PermissionManager.check_perms(
                                                'monitor:operlog:remove'
                                            )
                                            else [],
                                            fac.AntdButton(
                                                [
                                                    fac.AntdIcon(
                                                        icon='antd-arrow-down'
                                                    ),
                                                    '导出',
                                                ],
                                                id='operation_log-export',
                                                style={
                                                    'color': '#ffba00',
                                                    'background': '#fff8e6',
                                                    'border-color': '#ffe399',
                                                },
                                            )
                                            if PermissionManager.check_perms(
                                                'monitor:operlog:export'
                                            )
                                            else [],
                                        ],
                                        style={'paddingBottom': '10px'},
                                    ),
                                    span=16,
                                ),
                                fac.AntdCol(
                                    fac.AntdSpace(
                                        [
                                            html.Div(
                                                fac.AntdTooltip(
                                                    fac.AntdButton(
                                                        [
                                                            fac.AntdIcon(
                                                                icon='antd-search'
                                                            ),
                                                        ],
                                                        id='operation_log-hidden',
                                                        shape='circle',
                                                    ),
                                                    id='operation_log-hidden-tooltip',
                                                    title='隐藏搜索',
                                                )
                                            ),
                                            html.Div(
                                                fac.AntdTooltip(
                                                    fac.AntdButton(
                                                        [
                                                            fac.AntdIcon(
                                                                icon='antd-sync'
                                                            ),
                                                        ],
                                                        id='operation_log-refresh',
                                                        shape='circle',
                                                    ),
                                                    title='刷新',
                                                )
                                            ),
                                        ],
                                        style={
                                            'float': 'right',
                                            'paddingBottom': '10px',
                                        },
                                    ),
                                    span=8,
                                    style={'paddingRight': '10px'},
                                ),
                            ],
                            gutter=5,
                        ),
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    fac.AntdSpin(
                                        fac.AntdTable(
                                            id='operation_log-list-table',
                                            data=[],
                                            columns=[
                                                {
                                                    'dataIndex': 'oper_id',
                                                    'title': '日志编号',
                                                    'renderOptions': {
                                                        'renderType': 'ellipsis'
                                                    },
                                                },
                                                {
                                                    'dataIndex': 'title',
                                                    'title': '系统模块',
                                                    'renderOptions': {
                                                        'renderType': 'ellipsis'
                                                    },
                                                },
                                                {
                                                    'dataIndex': 'business_type_tag',
                                                    'title': '操作类型',
                                                    'renderOptions': {
                                                        'renderType': 'tags'
                                                    },
                                                },
                                                {
                                                    'dataIndex': 'oper_name',
                                                    'title': '操作人员',
                                                    'renderOptions': {
                                                        'renderType': 'ellipsis'
                                                    },
                                                },
                                                {
                                                    'dataIndex': 'oper_ip',
                                                    'title': '操作地址',
                                                    'renderOptions': {
                                                        'renderType': 'ellipsis'
                                                    },
                                                },
                                                {
                                                    'dataIndex': 'oper_location',
                                                    'title': '操作地点',
                                                    'renderOptions': {
                                                        'renderType': 'ellipsis'
                                                    },
                                                },
                                                {
                                                    'dataIndex': 'status_tag',
                                                    'title': '操作状态',
                                                    'renderOptions': {
                                                        'renderType': 'tags'
                                                    },
                                                },
                                                {
                                                    'dataIndex': 'oper_time',
                                                    'title': '操作日期',
                                                    'renderOptions': {
                                                        'renderType': 'ellipsis'
                                                    },
                                                },
                                                {
                                                    'dataIndex': 'cost_time',
                                                    'title': '消耗时间',
                                                    'renderOptions': {
                                                        'renderType': 'ellipsis'
                                                    },
                                                },
                                                {
                                                    'title': '操作',
                                                    'dataIndex': 'operation',
                                                    'width': 120,
                                                    'renderOptions': {
                                                        'renderType': 'button'
                                                    },
                                                },
                                            ],
                                            rowSelectionType='checkbox',
                                            rowSelectionWidth=50,
                                            bordered=True,
                                            sortOptions={
                                                'sortDataIndexes': [
                                                    'oper_name',
                                                    'oper_time',
                                                ],
                                                'multiple': False,
                                            },
                                            pagination={
                                                'pageSize': 10,
                                                'current': 1,
                                                'showSizeChanger': True,
                                                'pageSizeOptions': [
                                                    10,
                                                    30,
                                                    50,
                                                    100,
                                                ],
                                                'showQuickJumper': True,
                                                'total': 0,
                                            },
                                            mode='server-side',
                                            style={
                                                'width': '100%',
                                                'padding-right': '10px',
                                            },
                                        ),
                                        text='数据加载中',
                                    ),
                                )
                            ]
                        ),
                    ],
                    span=24,
                )
            ],
            gutter=5,
        ),
        # 操作日志明细modal
        fac.AntdModal(
            [
                fac.AntdForm(
                    [
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    fac.AntdFormItem(
                                        fac.AntdText(
                                            id={
                                                'type': 'operation_log-form-value',
                                                'index': 'title',
                                            }
                                        ),
                                        label='操作模块',
                                        required=True,
                                        id={
                                            'type': 'operation_log-form-label',
                                            'index': 'title',
                                        },
                                        labelCol={'span': 8},
                                        wrapperCol={'span': 16},
                                    ),
                                    span=12,
                                ),
                                fac.AntdCol(
                                    fac.AntdFormItem(
                                        fac.AntdText(
                                            id={
                                                'type': 'operation_log-form-value',
                                                'index': 'oper_url',
                                            }
                                        ),
                                        label='请求地址',
                                        required=True,
                                        id={
                                            'type': 'operation_log-form-label',
                                            'index': 'oper_url',
                                        },
                                        labelCol={'span': 8},
                                        wrapperCol={'span': 16},
                                    ),
                                    span=12,
                                ),
                            ],
                            gutter=5,
                        ),
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    fac.AntdFormItem(
                                        fac.AntdText(
                                            id={
                                                'type': 'operation_log-form-value',
                                                'index': 'login_info',
                                            }
                                        ),
                                        label='登录信息',
                                        required=True,
                                        id={
                                            'type': 'operation_log-form-label',
                                            'index': 'login_info',
                                        },
                                        labelCol={'span': 8},
                                        wrapperCol={'span': 16},
                                    ),
                                    span=12,
                                ),
                                fac.AntdCol(
                                    fac.AntdFormItem(
                                        fac.AntdText(
                                            id={
                                                'type': 'operation_log-form-value',
                                                'index': 'request_method',
                                            }
                                        ),
                                        label='请求方式',
                                        required=True,
                                        id={
                                            'type': 'operation_log-form-label',
                                            'index': 'request_method',
                                        },
                                        labelCol={'span': 8},
                                        wrapperCol={'span': 16},
                                    ),
                                    span=12,
                                ),
                            ],
                            gutter=5,
                        ),
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    fac.AntdFormItem(
                                        fac.AntdText(
                                            id={
                                                'type': 'operation_log-form-value',
                                                'index': 'method',
                                            }
                                        ),
                                        label='操作方法',
                                        required=True,
                                        id={
                                            'type': 'operation_log-form-label',
                                            'index': 'method',
                                        },
                                        labelCol={'span': 4},
                                        wrapperCol={'span': 20},
                                    ),
                                    span=24,
                                ),
                            ],
                        ),
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    fac.AntdFormItem(
                                        fac.AntdText(
                                            id={
                                                'type': 'operation_log-form-value',
                                                'index': 'oper_param',
                                            }
                                        ),
                                        label='请求参数',
                                        required=True,
                                        id={
                                            'type': 'operation_log-form-label',
                                            'index': 'oper_param',
                                        },
                                        labelCol={'span': 4},
                                        wrapperCol={'span': 20},
                                    ),
                                    span=24,
                                ),
                            ],
                        ),
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    fac.AntdFormItem(
                                        fac.AntdText(
                                            id={
                                                'type': 'operation_log-form-value',
                                                'index': 'json_result',
                                            }
                                        ),
                                        label='返回参数',
                                        required=True,
                                        id={
                                            'type': 'operation_log-form-label',
                                            'index': 'json_result',
                                        },
                                        labelCol={'span': 4},
                                        wrapperCol={'span': 20},
                                    ),
                                    span=24,
                                ),
                            ],
                        ),
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    fac.AntdFormItem(
                                        fac.AntdText(
                                            id={
                                                'type': 'operation_log-form-value',
                                                'index': 'status',
                                            }
                                        ),
                                        label='操作状态',
                                        required=True,
                                        id={
                                            'type': 'operation_log-form-label',
                                            'index': 'status',
                                        },
                                        labelCol={'span': 12},
                                        wrapperCol={'span': 12},
                                    ),
                                    span=8,
                                ),
                                fac.AntdCol(
                                    fac.AntdFormItem(
                                        fac.AntdText(
                                            id={
                                                'type': 'operation_log-form-value',
                                                'index': 'cost_time',
                                            }
                                        ),
                                        label='消耗时间',
                                        required=True,
                                        id={
                                            'type': 'operation_log-form-label',
                                            'index': 'cost_time',
                                        },
                                        labelCol={'span': 12},
                                        wrapperCol={'span': 12},
                                    ),
                                    span=6,
                                ),
                                fac.AntdCol(
                                    fac.AntdFormItem(
                                        fac.AntdText(
                                            id={
                                                'type': 'operation_log-form-value',
                                                'index': 'oper_time',
                                            }
                                        ),
                                        label='操作时间',
                                        required=True,
                                        id={
                                            'type': 'operation_log-form-label',
                                            'index': 'oper_time',
                                        },
                                        labelCol={'span': 8},
                                        wrapperCol={'span': 16},
                                    ),
                                    span=10,
                                ),
                            ],
                            gutter=5,
                        ),
                    ],
                    labelCol={'span': 8},
                    wrapperCol={'span': 16},
                    style={'marginRight': '15px'},
                )
            ],
            id='operation_log-modal',
            mask=False,
            width=850,
            renderFooter=False,
        ),
        # 删除操作日志二次确认modal
        fac.AntdModal(
            fac.AntdText('是否确认删除？', id='operation_log-delete-text'),
            id='operation_log-delete-confirm-modal',
            visible=False,
            title='提示',
            renderFooter=True,
            centered=True,
        ),
    ]
