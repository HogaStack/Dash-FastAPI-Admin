import feffery_antd_components as fac
from dash import dcc, html
from callbacks.system_c import post_c  # noqa: F401
from components.ApiRadioGroup import ApiRadioGroup
from components.ApiSelect import ApiSelect
from utils.permission_util import PermissionManager


def render(*args, **kwargs):
    return [
        # 用于导出成功后重置dcc.Download的状态，防止多次下载文件
        dcc.Store(id='post-export-complete-judge-container'),
        # 绑定的导出组件
        dcc.Download(id='post-export-container'),
        # 岗位管理模块操作类型存储容器
        dcc.Store(id='post-operations-store'),
        # 岗位管理模块弹窗类型存储容器
        dcc.Store(id='post-modal_type-store'),
        # 岗位管理模块表单数据存储容器
        dcc.Store(id='post-form-store'),
        # 岗位管理模块删除操作行key存储容器
        dcc.Store(id='post-delete-ids-store'),
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
                                                    fac.AntdSpace(
                                                        [
                                                            fac.AntdFormItem(
                                                                fac.AntdInput(
                                                                    id='post-post_code-input',
                                                                    placeholder='请输入岗位编码',
                                                                    autoComplete='off',
                                                                    allowClear=True,
                                                                    style={
                                                                        'width': 210
                                                                    },
                                                                ),
                                                                label='岗位编码',
                                                            ),
                                                            fac.AntdFormItem(
                                                                fac.AntdInput(
                                                                    id='post-post_name-input',
                                                                    placeholder='请输入岗位名称',
                                                                    autoComplete='off',
                                                                    allowClear=True,
                                                                    style={
                                                                        'width': 210
                                                                    },
                                                                ),
                                                                label='岗位名称',
                                                            ),
                                                            fac.AntdFormItem(
                                                                ApiSelect(
                                                                    dict_type='sys_normal_disable',
                                                                    id='post-status-select',
                                                                    placeholder='岗位状态',
                                                                    style={
                                                                        'width': 200
                                                                    },
                                                                ),
                                                                label='岗位状态',
                                                            ),
                                                            fac.AntdFormItem(
                                                                fac.AntdButton(
                                                                    '搜索',
                                                                    id='post-search',
                                                                    type='primary',
                                                                    icon=fac.AntdIcon(
                                                                        icon='antd-search'
                                                                    ),
                                                                )
                                                            ),
                                                            fac.AntdFormItem(
                                                                fac.AntdButton(
                                                                    '重置',
                                                                    id='post-reset',
                                                                    icon=fac.AntdIcon(
                                                                        icon='antd-sync'
                                                                    ),
                                                                )
                                                            ),
                                                        ],
                                                        style={
                                                            'paddingBottom': '10px'
                                                        },
                                                    ),
                                                ],
                                                layout='inline',
                                            )
                                        ],
                                        id='post-search-form-container',
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
                                                    'type': 'post-operation-button',
                                                    'index': 'add',
                                                },
                                                style={
                                                    'color': '#1890ff',
                                                    'background': '#e8f4ff',
                                                    'border-color': '#a3d3ff',
                                                },
                                            )
                                            if PermissionManager.check_perms(
                                                'system:post:add'
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
                                                    'type': 'post-operation-button',
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
                                                'system:post:edit'
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
                                                    'type': 'post-operation-button',
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
                                                'system:post:remove'
                                            )
                                            else [],
                                            fac.AntdButton(
                                                [
                                                    fac.AntdIcon(
                                                        icon='antd-arrow-down'
                                                    ),
                                                    '导出',
                                                ],
                                                id='post-export',
                                                style={
                                                    'color': '#ffba00',
                                                    'background': '#fff8e6',
                                                    'border-color': '#ffe399',
                                                },
                                            )
                                            if PermissionManager.check_perms(
                                                'system:post:export'
                                            )
                                            else [],
                                        ],
                                        style={
                                            'paddingBottom': '10px',
                                        },
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
                                                        id='post-hidden',
                                                        shape='circle',
                                                    ),
                                                    id='post-hidden-tooltip',
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
                                                        id='post-refresh',
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
                                            id='post-list-table',
                                            data=[],
                                            columns=[
                                                {
                                                    'dataIndex': 'post_id',
                                                    'title': '岗位编号',
                                                    'renderOptions': {
                                                        'renderType': 'ellipsis'
                                                    },
                                                },
                                                {
                                                    'dataIndex': 'post_code',
                                                    'title': '岗位编码',
                                                    'renderOptions': {
                                                        'renderType': 'ellipsis'
                                                    },
                                                },
                                                {
                                                    'dataIndex': 'post_name',
                                                    'title': '岗位名称',
                                                    'renderOptions': {
                                                        'renderType': 'ellipsis'
                                                    },
                                                },
                                                {
                                                    'dataIndex': 'post_sort',
                                                    'title': '岗位排序',
                                                    'renderOptions': {
                                                        'renderType': 'ellipsis'
                                                    },
                                                },
                                                {
                                                    'dataIndex': 'status',
                                                    'title': '状态',
                                                    'renderOptions': {
                                                        'renderType': 'tags'
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
        # 新增和编辑岗位表单modal
        fac.AntdModal(
            [
                fac.AntdForm(
                    [
                        fac.AntdFormItem(
                            fac.AntdInput(
                                name='post_name',
                                placeholder='请输入岗位名称',
                                allowClear=True,
                                style={'width': 350},
                            ),
                            label='岗位名称',
                            required=True,
                            id={
                                'type': 'post-form-label',
                                'index': 'post_name',
                                'required': True,
                            },
                            hasFeedback=True,
                        ),
                        fac.AntdFormItem(
                            fac.AntdInput(
                                name='post_code',
                                placeholder='请输入岗位编码',
                                allowClear=True,
                                style={'width': 350},
                            ),
                            label='岗位编码',
                            required=True,
                            id={
                                'type': 'post-form-label',
                                'index': 'post_code',
                                'required': True,
                            },
                            hasFeedback=True,
                        ),
                        fac.AntdFormItem(
                            fac.AntdInputNumber(
                                name='post_sort',
                                defaultValue=0,
                                min=0,
                                style={'width': 350},
                            ),
                            label='岗位顺序',
                            required=True,
                            id={
                                'type': 'post-form-label',
                                'index': 'post_sort',
                                'required': True,
                            },
                            hasFeedback=True,
                        ),
                        fac.AntdFormItem(
                            ApiRadioGroup(
                                dict_type='sys_normal_disable',
                                name='status',
                                defaultValue='0',
                                style={'width': 350},
                            ),
                            label='岗位状态',
                            id={
                                'type': 'post-form-label',
                                'index': 'status',
                                'required': False,
                            },
                            hasFeedback=True,
                        ),
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
                                'type': 'post-form-label',
                                'index': 'remark',
                                'required': False,
                            },
                            hasFeedback=True,
                        ),
                    ],
                    id='post-form',
                    enableBatchControl=True,
                    labelCol={'span': 6},
                    wrapperCol={'span': 18},
                )
            ],
            id='post-modal',
            mask=False,
            width=580,
            renderFooter=True,
            okClickClose=False,
        ),
        # 删除岗位二次确认modal
        fac.AntdModal(
            fac.AntdText('是否确认删除？', id='post-delete-text'),
            id='post-delete-confirm-modal',
            visible=False,
            title='提示',
            renderFooter=True,
            centered=True,
        ),
    ]
