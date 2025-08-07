import feffery_antd_components as fac
from dash import dcc, html
from callbacks.system_c import config_c  # noqa: F401
from components.ApiRadioGroup import ApiRadioGroup
from components.ApiSelect import ApiSelect
from utils.permission_util import PermissionManager


def render(*args, **kwargs):
    return [
        # 用于导出成功后重置dcc.Download的状态，防止多次下载文件
        dcc.Store(id='config-export-complete-judge-container'),
        # 绑定的导出组件
        dcc.Download(id='config-export-container'),
        # 参数管理模块操作类型存储容器
        dcc.Store(id='config-operations-store'),
        # 参数管理模块弹窗类型存储容器
        dcc.Store(id='config-modal_type-store'),
        # 参数管理模块表单数据存储容器
        dcc.Store(id='config-form-store'),
        # 参数管理模块删除操作行key存储容器
        dcc.Store(id='config-delete-ids-store'),
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
                                                            id='config-config_name-input',
                                                            placeholder='请输入参数名称',
                                                            autoComplete='off',
                                                            allowClear=True,
                                                            style={
                                                                'width': 235
                                                            },
                                                        ),
                                                        label='参数名称',
                                                        style={
                                                            'paddingBottom': '10px'
                                                        },
                                                    ),
                                                    fac.AntdFormItem(
                                                        fac.AntdInput(
                                                            id='config-config_key-input',
                                                            placeholder='请输入参数键名',
                                                            autoComplete='off',
                                                            allowClear=True,
                                                            style={
                                                                'width': 235
                                                            },
                                                        ),
                                                        label='参数键名',
                                                        style={
                                                            'paddingBottom': '10px'
                                                        },
                                                    ),
                                                    fac.AntdFormItem(
                                                        ApiSelect(
                                                            dict_type='sys_yes_no',
                                                            id='config-config_type-select',
                                                            placeholder='系统内置',
                                                            style={
                                                                'width': 235
                                                            },
                                                        ),
                                                        label='系统内置',
                                                        style={
                                                            'paddingBottom': '10px'
                                                        },
                                                    ),
                                                    fac.AntdFormItem(
                                                        fac.AntdDateRangePicker(
                                                            id='config-create_time-range',
                                                            style={
                                                                'width': 235
                                                            },
                                                        ),
                                                        label='创建时间',
                                                        style={
                                                            'paddingBottom': '10px'
                                                        },
                                                    ),
                                                    fac.AntdFormItem(
                                                        fac.AntdButton(
                                                            '搜索',
                                                            id='config-search',
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
                                                            id='config-reset',
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
                                        id='config-search-form-container',
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
                                                        icon='antd-plus'
                                                    ),
                                                    '新增',
                                                ],
                                                id={
                                                    'type': 'config-operation-button',
                                                    'index': 'add',
                                                },
                                                style={
                                                    'color': '#1890ff',
                                                    'background': '#e8f4ff',
                                                    'border-color': '#a3d3ff',
                                                },
                                            )
                                            if PermissionManager.check_perms(
                                                'system:config:add'
                                            )
                                            else [],
                                            fac.AntdButton(
                                                [
                                                    fac.AntdIcon(
                                                        icon='antd-edit'
                                                    ),
                                                    '修改',
                                                ],
                                                id={
                                                    'type': 'config-operation-button',
                                                    'index': 'edit',
                                                },
                                                disabled=True,
                                                style={
                                                    'color': '#71e2a3',
                                                    'background': '#e7faf0',
                                                    'border-color': '#d0f5e0',
                                                },
                                            )
                                            if PermissionManager.check_perms(
                                                'system:config:edit'
                                            )
                                            else [],
                                            fac.AntdButton(
                                                [
                                                    fac.AntdIcon(
                                                        icon='antd-minus'
                                                    ),
                                                    '删除',
                                                ],
                                                id={
                                                    'type': 'config-operation-button',
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
                                                'system:config:remove'
                                            )
                                            else [],
                                            fac.AntdButton(
                                                [
                                                    fac.AntdIcon(
                                                        icon='antd-arrow-down'
                                                    ),
                                                    '导出',
                                                ],
                                                id='config-export',
                                                style={
                                                    'color': '#ffba00',
                                                    'background': '#fff8e6',
                                                    'border-color': '#ffe399',
                                                },
                                            )
                                            if PermissionManager.check_perms(
                                                'system:config:export'
                                            )
                                            else [],
                                            fac.AntdButton(
                                                [
                                                    fac.AntdIcon(
                                                        icon='antd-sync'
                                                    ),
                                                    '刷新缓存',
                                                ],
                                                id='config-refresh-cache',
                                                style={
                                                    'color': '#ff9292',
                                                    'background': '#ffeded',
                                                    'border-color': '#ffdbdb',
                                                    'marginRight': '10px',
                                                },
                                            )
                                            if PermissionManager.check_perms(
                                                'system:config:remove'
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
                                                        id='config-hidden',
                                                        shape='circle',
                                                    ),
                                                    id='config-hidden-tooltip',
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
                                                        id='config-refresh',
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
                                            id='config-list-table',
                                            data=[],
                                            columns=[
                                                {
                                                    'dataIndex': 'config_id',
                                                    'title': '参数编号',
                                                    'renderOptions': {
                                                        'renderType': 'ellipsis'
                                                    },
                                                },
                                                {
                                                    'dataIndex': 'config_name',
                                                    'title': '参数名称',
                                                    'renderOptions': {
                                                        'renderType': 'ellipsis'
                                                    },
                                                },
                                                {
                                                    'dataIndex': 'config_key',
                                                    'title': '参数键名',
                                                    'renderOptions': {
                                                        'renderType': 'ellipsis'
                                                    },
                                                },
                                                {
                                                    'dataIndex': 'config_value',
                                                    'title': '参数键值',
                                                    'renderOptions': {
                                                        'renderType': 'ellipsis'
                                                    },
                                                },
                                                {
                                                    'dataIndex': 'config_type',
                                                    'title': '系统内置',
                                                    'renderOptions': {
                                                        'renderType': 'tags'
                                                    },
                                                },
                                                {
                                                    'dataIndex': 'remark',
                                                    'title': '备注',
                                                    'renderOptions': {
                                                        'renderType': 'ellipsis'
                                                    },
                                                },
                                                {
                                                    'dataIndex': 'create_time',
                                                    'title': '创建时间',
                                                    'renderOptions': {
                                                        'renderType': 'ellipsis'
                                                    },
                                                },
                                                {
                                                    'title': '操作',
                                                    'dataIndex': 'operation',
                                                    'width': 170,
                                                    'renderOptions': {
                                                        'renderType': 'button'
                                                    },
                                                },
                                            ],
                                            rowSelectionType='checkbox',
                                            rowSelectionWidth=50,
                                            bordered=True,
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
        # 新增和编辑参数配置表单modal
        fac.AntdModal(
            [
                fac.AntdForm(
                    [
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    fac.AntdFormItem(
                                        fac.AntdInput(
                                            name='config_name',
                                            placeholder='请输入参数名称',
                                            allowClear=True,
                                            style={'width': 350},
                                        ),
                                        label='参数名称',
                                        required=True,
                                        id={
                                            'type': 'config-form-label',
                                            'index': 'config_name',
                                            'required': True,
                                        },
                                    ),
                                    span=24,
                                ),
                            ]
                        ),
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    fac.AntdFormItem(
                                        fac.AntdInput(
                                            name='config_key',
                                            placeholder='请输入参数键名',
                                            allowClear=True,
                                            style={'width': 350},
                                        ),
                                        label='参数键名',
                                        required=True,
                                        id={
                                            'type': 'config-form-label',
                                            'index': 'config_key',
                                            'required': True,
                                        },
                                    ),
                                    span=24,
                                ),
                            ]
                        ),
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    fac.AntdFormItem(
                                        fac.AntdInput(
                                            name='config_value',
                                            placeholder='请输入参数键值',
                                            allowClear=True,
                                            style={'width': 350},
                                        ),
                                        label='参数键值',
                                        required=True,
                                        id={
                                            'type': 'config-form-label',
                                            'index': 'config_value',
                                            'required': True,
                                        },
                                    ),
                                    span=24,
                                ),
                            ]
                        ),
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    fac.AntdFormItem(
                                        ApiRadioGroup(
                                            dict_type='sys_yes_no',
                                            name='config_type',
                                            defaultValue='Y',
                                            style={'width': 350},
                                        ),
                                        label='系统内置',
                                        id={
                                            'type': 'config-form-label',
                                            'index': 'config_type',
                                            'required': False,
                                        },
                                    ),
                                    span=24,
                                ),
                            ]
                        ),
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    fac.AntdFormItem(
                                        fac.AntdInput(
                                            name='remark',
                                            placeholder='请输入内容',
                                            allowClear=True,
                                            mode='text-area',
                                            style={'width': 350},
                                        ),
                                        label='备注',
                                        id={
                                            'type': 'config-form-label',
                                            'index': 'remark',
                                            'required': False,
                                        },
                                    ),
                                    span=24,
                                ),
                            ]
                        ),
                    ],
                    id='config-form',
                    enableBatchControl=True,
                    labelCol={'span': 6},
                    wrapperCol={'span': 18},
                )
            ],
            id='config-modal',
            mask=False,
            width=580,
            renderFooter=True,
            okClickClose=False,
        ),
        # 删除参数配置二次确认modal
        fac.AntdModal(
            fac.AntdText('是否确认删除？', id='config-delete-text'),
            id='config-delete-confirm-modal',
            visible=False,
            title='提示',
            renderFooter=True,
            centered=True,
        ),
    ]
