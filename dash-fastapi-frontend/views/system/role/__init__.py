import feffery_antd_components as fac
from dash import dcc, html
from callbacks.system_c.role_c import role_c  # noqa: F401
from components.ApiRadioGroup import ApiRadioGroup
from components.ApiSelect import ApiSelect
from utils.permission_util import PermissionManager
from . import data_scope, allocate_user


def render(*args, **kwargs):
    return [
        # 用于导出成功后重置dcc.Download的状态，防止多次下载文件
        dcc.Store(id='role-export-complete-judge-container'),
        # 绑定的导出组件
        dcc.Download(id='role-export-container'),
        # 角色管理模块操作类型存储容器
        dcc.Store(id='role-operations-store'),
        # 角色管理模块弹窗类型存储容器
        dcc.Store(id='role-modal_type-store'),
        # 角色管理模块修改操作行key存储容器
        dcc.Store(id='role-edit-id-store'),
        # 角色管理模块删除操作行key存储容器
        dcc.Store(id='role-delete-ids-store'),
        # 角色管理模块菜单权限存储容器
        dcc.Store(id='role-menu-store'),
        dcc.Store(id='current-role-menu-store'),
        # 角色管理模块数据权限存储容器
        dcc.Store(id='role-dept-store'),
        dcc.Store(id='current-role-dept-store'),
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
                                                            id='role-role_name-input',
                                                            placeholder='请输入角色名称',
                                                            autoComplete='off',
                                                            allowClear=True,
                                                            style={
                                                                'width': 220
                                                            },
                                                        ),
                                                        label='角色名称',
                                                        style={
                                                            'paddingBottom': '10px'
                                                        },
                                                    ),
                                                    fac.AntdFormItem(
                                                        fac.AntdInput(
                                                            id='role-role_key-input',
                                                            placeholder='请输入权限字符',
                                                            autoComplete='off',
                                                            allowClear=True,
                                                            style={
                                                                'width': 220
                                                            },
                                                        ),
                                                        label='权限字符',
                                                        style={
                                                            'paddingBottom': '10px'
                                                        },
                                                    ),
                                                    fac.AntdFormItem(
                                                        ApiSelect(
                                                            dict_type='sys_normal_disable',
                                                            id='role-status-select',
                                                            placeholder='角色状态',
                                                            style={
                                                                'width': 220
                                                            },
                                                        ),
                                                        label='状态',
                                                        style={
                                                            'paddingBottom': '10px'
                                                        },
                                                    ),
                                                    fac.AntdFormItem(
                                                        fac.AntdDateRangePicker(
                                                            id='role-create_time-range',
                                                            style={
                                                                'width': 240
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
                                                            id='role-search',
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
                                                            id='role-reset',
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
                                        id='role-search-form-container',
                                        hidden=False,
                                    ),
                                )
                            ]
                        ),
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    html.Div(
                                        [
                                            fac.AntdButton(
                                                [
                                                    fac.AntdIcon(
                                                        icon='antd-plus'
                                                    ),
                                                    '新增',
                                                ],
                                                id={
                                                    'type': 'role-operation-button',
                                                    'operation': 'add',
                                                },
                                                style={
                                                    'color': '#1890ff',
                                                    'background': '#e8f4ff',
                                                    'border-color': '#a3d3ff',
                                                    'marginRight': '10px',
                                                },
                                            )
                                            if PermissionManager.check_perms(
                                                'system:role:add'
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
                                                    'type': 'role-operation-button',
                                                    'operation': 'edit',
                                                },
                                                disabled=True,
                                                style={
                                                    'color': '#71e2a3',
                                                    'background': '#e7faf0',
                                                    'border-color': '#d0f5e0',
                                                    'marginRight': '10px',
                                                },
                                            )
                                            if PermissionManager.check_perms(
                                                'system:role:edit'
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
                                                    'type': 'role-operation-button',
                                                    'operation': 'delete',
                                                },
                                                disabled=True,
                                                style={
                                                    'color': '#ff9292',
                                                    'background': '#ffeded',
                                                    'border-color': '#ffdbdb',
                                                    'marginRight': '10px',
                                                },
                                            )
                                            if PermissionManager.check_perms(
                                                'system:role:remove'
                                            )
                                            else [],
                                            fac.AntdButton(
                                                [
                                                    fac.AntdIcon(
                                                        icon='antd-arrow-down'
                                                    ),
                                                    '导出',
                                                ],
                                                id='role-export',
                                                style={
                                                    'color': '#ffba00',
                                                    'background': '#fff8e6',
                                                    'border-color': '#ffe399',
                                                    'marginRight': '10px',
                                                },
                                            )
                                            if PermissionManager.check_perms(
                                                'system:role:export'
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
                                                        id='role-hidden',
                                                        shape='circle',
                                                    ),
                                                    id='role-hidden-tooltip',
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
                                                        id='role-refresh',
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
                                            id='role-list-table',
                                            data=[],
                                            columns=[
                                                {
                                                    'dataIndex': 'role_id',
                                                    'title': '角色编号',
                                                    'renderOptions': {
                                                        'renderType': 'ellipsis'
                                                    },
                                                },
                                                {
                                                    'dataIndex': 'role_name',
                                                    'title': '角色名称',
                                                    'renderOptions': {
                                                        'renderType': 'ellipsis'
                                                    },
                                                },
                                                {
                                                    'dataIndex': 'role_key',
                                                    'title': '权限字符',
                                                    'renderOptions': {
                                                        'renderType': 'ellipsis'
                                                    },
                                                },
                                                {
                                                    'dataIndex': 'role_sort',
                                                    'title': '显示顺序',
                                                    'renderOptions': {
                                                        'renderType': 'ellipsis'
                                                    },
                                                },
                                                {
                                                    'dataIndex': 'status',
                                                    'title': '状态',
                                                    'width': 100,
                                                    'renderOptions': {
                                                        'renderType': 'switch'
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
                                                    'width': 200,
                                                    'dataIndex': 'operation',
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
        # 新增和编辑角色表单modal
        fac.AntdModal(
            [
                fac.AntdForm(
                    [
                        fac.AntdFormItem(
                            fac.AntdInput(
                                id={
                                    'type': 'role-form-value',
                                    'index': 'role_name',
                                    'required': True,
                                },
                                placeholder='请输入角色名称',
                                allowClear=True,
                                style={'width': 350},
                            ),
                            label='角色名称',
                            required=True,
                            id={
                                'type': 'role-form-label',
                                'index': 'role_name',
                                'required': True,
                            },
                            labelCol={'span': 6},
                            wrapperCol={'span': 18},
                        ),
                        fac.AntdFormItem(
                            fac.AntdInput(
                                id={
                                    'type': 'role-form-value',
                                    'index': 'role_key',
                                    'required': True,
                                },
                                placeholder='请输入权限字符',
                                allowClear=True,
                                style={'width': 350},
                            ),
                            label='权限字符',
                            tooltip='控制器中定义的权限字符，如：common',
                            required=True,
                            id={
                                'type': 'role-form-label',
                                'index': 'role_key',
                                'required': True,
                            },
                            labelCol={'span': 6},
                            wrapperCol={'span': 18},
                        ),
                        fac.AntdFormItem(
                            fac.AntdInputNumber(
                                id={
                                    'type': 'role-form-value',
                                    'index': 'role_sort',
                                    'required': True,
                                },
                                placeholder='请输入角色顺序',
                                defaultValue=0,
                                min=0,
                                style={'width': 350},
                            ),
                            label='角色顺序',
                            required=True,
                            id={
                                'type': 'role-form-label',
                                'index': 'role_sort',
                                'required': True,
                            },
                            labelCol={'span': 6},
                            wrapperCol={'span': 18},
                        ),
                        fac.AntdFormItem(
                            ApiRadioGroup(
                                dict_type='sys_normal_disable',
                                id={
                                    'type': 'role-form-value',
                                    'index': 'status',
                                    'required': False,
                                },
                                style={'width': 350},
                            ),
                            label='状态',
                            id={
                                'type': 'role-form-label',
                                'index': 'status',
                                'required': False,
                            },
                            labelCol={'span': 6},
                            wrapperCol={'span': 18},
                        ),
                        fac.AntdFormItem(
                            [
                                fac.AntdRow(
                                    [
                                        fac.AntdCol(
                                            fac.AntdCheckbox(
                                                id='role-menu-perms-radio-fold-unfold',
                                                label='展开/折叠',
                                            ),
                                            span=7,
                                        ),
                                        fac.AntdCol(
                                            fac.AntdCheckbox(
                                                id='role-menu-perms-radio-all-none',
                                                label='全选/全不选',
                                            ),
                                            span=8,
                                        ),
                                        fac.AntdCol(
                                            fac.AntdCheckbox(
                                                id='role-menu-perms-radio-parent-children',
                                                label='父子联动',
                                                checked=True,
                                            ),
                                            span=6,
                                        ),
                                    ],
                                    style={'paddingTop': '6px'},
                                ),
                                fac.AntdRow(
                                    fac.AntdCol(
                                        html.Div(
                                            [
                                                fac.AntdTree(
                                                    id='role-menu-perms',
                                                    treeData=[],
                                                    multiple=True,
                                                    checkable=True,
                                                    showLine=False,
                                                    selectable=False,
                                                )
                                            ],
                                            style={
                                                'border': 'solid 1px rgba(0, 0, 0, 0.2)',
                                                'border-radius': '5px',
                                                'width': 350,
                                            },
                                        )
                                    ),
                                    style={'paddingTop': '6px'},
                                ),
                            ],
                            label='菜单权限',
                            id='role-menu-perms-form-item',
                            labelCol={'span': 6},
                            wrapperCol={'span': 18},
                        ),
                        fac.AntdFormItem(
                            fac.AntdInput(
                                id={
                                    'type': 'role-form-value',
                                    'index': 'remark',
                                    'required': False,
                                },
                                placeholder='请输入内容',
                                allowClear=True,
                                mode='text-area',
                                style={'width': 350},
                            ),
                            label='备注',
                            id={
                                'type': 'role-form-label',
                                'index': 'remark',
                                'required': False,
                            },
                            labelCol={'span': 6},
                            wrapperCol={'span': 18},
                        ),
                    ]
                )
            ],
            id='role-modal',
            mask=False,
            width=600,
            renderFooter=True,
            okClickClose=False,
        ),
        # 删除角色二次确认modal
        fac.AntdModal(
            fac.AntdText('是否确认删除？', id='role-delete-text'),
            id='role-delete-confirm-modal',
            visible=False,
            title='提示',
            renderFooter=True,
            centered=True,
        ),
        # 数据权限modal
        fac.AntdModal(
            data_scope.render(),
            id='role-datascope-modal',
            title='数据权限',
            mask=False,
            width=600,
            renderFooter=True,
            okClickClose=False,
        ),
        # 分配用户modal
        fac.AntdModal(
            allocate_user.render(),
            id='role_to_allocated_user-modal',
            title='分配用户',
            mask=False,
            maskClosable=False,
            width=1000,
            renderFooter=False,
            okClickClose=False,
        ),
    ]
