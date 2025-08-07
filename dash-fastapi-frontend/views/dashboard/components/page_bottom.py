import feffery_antd_charts as fact
import feffery_antd_components as fac
import feffery_utils_components as fuc
from dash import html


def render_page_bottom():
    # 模拟数据
    radar_origin_data = [
        {
            'name': '个人',
            'ref': 10,
            'koubei': 8,
            'output': 4,
            'contribute': 5,
            'hot': 7,
        },
        {
            'name': '团队',
            'ref': 3,
            'koubei': 9,
            'output': 6,
            'contribute': 3,
            'hot': 1,
        },
        {
            'name': '部门',
            'ref': 4,
            'koubei': 1,
            'output': 6,
            'contribute': 5,
            'hot': 7,
        },
    ]

    radar_data = []
    radar_title_map = {
        'ref': '引用',
        'koubei': '口碑',
        'output': '产量',
        'contribute': '贡献',
        'hot': '热度',
    }

    for item in radar_origin_data:
        for key, value in item.items():
            if key != 'name':
                radar_data.append(
                    {
                        'name': item['name'],
                        'label': radar_title_map[key],
                        'value': value,
                    }
                )

    project_list = [
        {
            'id': 'xxx1',
            'title': 'Alipay',
            'logo': 'https://gw.alipayobjects.com/zos/rmsportal/WdGqmHpayyMjiEhcKoVE.png',
            'description': '那是一种内在的东西，他们到达不了，也无法触及的',
            'updatedAt': '2023-09-15T01:08:36.135Z',
            'member': '科学搬砖组',
            'href': '',
            'memberLink': '',
        },
        {
            'id': 'xxx2',
            'title': 'Angular',
            'logo': 'https://gw.alipayobjects.com/zos/rmsportal/zOsKZmFRdUtvpqCImOVY.png',
            'description': '希望是一个好东西，也许是最好的，好东西是不会消亡的',
            'updatedAt': '2017-07-24T00:00:00.000Z',
            'member': '全组都是吴彦祖',
            'href': '',
            'memberLink': '',
        },
        {
            'id': 'xxx3',
            'title': 'Ant Design',
            'logo': 'https://gw.alipayobjects.com/zos/rmsportal/dURIMkkrRFpPgTuzkwnB.png',
            'description': '城镇中有那么多的酒馆，她却偏偏走进了我的酒馆',
            'updatedAt': '2023-09-15T01:08:36.135Z',
            'member': '中二少女团',
            'href': '',
            'memberLink': '',
        },
        {
            'id': 'xxx4',
            'title': 'Ant Design Pro',
            'logo': 'https://gw.alipayobjects.com/zos/rmsportal/sfjbOqnsXXJgNCjCzDBL.png',
            'description': '那时候我只会想自己想要什么，从不想自己拥有什么',
            'updatedAt': '2017-07-23T00:00:00.000Z',
            'member': '程序员日常',
            'href': '',
            'memberLink': '',
        },
        {
            'id': 'xxx5',
            'title': 'Bootstrap',
            'logo': 'https://gw.alipayobjects.com/zos/rmsportal/siCrBXXhmvTQGWPNLBow.png',
            'description': '凛冬将至',
            'updatedAt': '2017-07-23T00:00:00.000Z',
            'member': '高逼格设计天团',
            'href': '',
            'memberLink': '',
        },
        {
            'id': 'xxx6',
            'title': 'React',
            'logo': 'https://gw.alipayobjects.com/zos/rmsportal/kZzEzemZyKLKFsojXItE.png',
            'description': '生命就像一盒巧克力，结果往往出人意料',
            'updatedAt': '2017-07-23T00:00:00.000Z',
            'member': '骗你来学计算机',
            'href': '',
            'memberLink': '',
        },
    ]

    activity_list = [
        {
            'id': 'trend-1',
            'updatedAt': '2023-09-15 01:08:36',
            'user': {
                'name': '曲丽丽',
                'avatar': 'https://gw.alipayobjects.com/zos/rmsportal/BiazfanxmamNRoxxVxka.png',
            },
            'group': {'name': '高逼格设计天团', 'link': 'http://github.com/'},
            'project': {'name': '六月迭代', 'link': 'http://github.com/'},
            'template': '新建项目',
        },
        {
            'id': 'trend-2',
            'updatedAt': '2023-09-15 01:08:36',
            'user': {
                'name': '付小小',
                'avatar': 'https://gw.alipayobjects.com/zos/rmsportal/cnrhVkzwxjPwAaCfPbdc.png',
            },
            'group': {'name': '高逼格设计天团', 'link': 'http://github.com/'},
            'project': {'name': '六月迭代', 'link': 'http://github.com/'},
            'template': '新建项目',
        },
        {
            'id': 'trend-3',
            'updatedAt': '2023-09-15 01:08:36',
            'user': {
                'name': '林东东',
                'avatar': 'https://gw.alipayobjects.com/zos/rmsportal/gaOngJwsRYRaVAuXXcmB.png',
            },
            'group': {'name': '中二少女团', 'link': 'http://github.com/'},
            'project': {'name': '六月迭代', 'link': 'http://github.com/'},
            'template': '新建项目',
        },
        {
            'id': 'trend-4',
            'updatedAt': '2023-09-15 01:08:36',
            'user': {
                'name': '周星星',
                'avatar': 'https://gw.alipayobjects.com/zos/rmsportal/WhxKECPNujWoWEFNdnJE.png',
            },
            'group': {'name': '白鹭酱油开发组', 'link': 'http://github.com/'},
            'project': {'name': '5 月日常迭代', 'link': 'http://github.com/'},
            'template': '发布了',
        },
        {
            'id': 'trend-5',
            'updatedAt': '2023-09-15 01:08:36',
            'user': {
                'name': '乐哥',
                'avatar': 'https://gw.alipayobjects.com/zos/rmsportal/jZUIxmJycoymBprLOUbT.png',
            },
            'group': {'name': '程序员日常', 'link': 'http://github.com/'},
            'project': {'name': '品牌迭代', 'link': 'http://github.com/'},
            'template': '新建项目',
        },
    ]

    return html.Div(
        [
            fac.AntdRow(
                [
                    fac.AntdCol(
                        [
                            fac.AntdCard(
                                [
                                    fac.AntdCardGrid(
                                        [
                                            html.Div(
                                                [
                                                    fac.AntdAvatar(
                                                        mode='image',
                                                        src=item.get('logo'),
                                                        size='small',
                                                    ),
                                                    html.A(item.get('title')),
                                                ],
                                                className='card-title',
                                            ),
                                            html.Div(
                                                item.get('description'),
                                                className='card-description',
                                            ),
                                            html.Div(
                                                [
                                                    html.A(item.get('member')),
                                                    html.Span(
                                                        '9小时前',
                                                        className='datetime',
                                                    ),
                                                ],
                                                className='project-item',
                                            ),
                                        ]
                                    )
                                    for item in project_list
                                ],
                                className='project-list',
                                title='进行中的项目',
                                variant='borderless',
                                extraLink={'content': '全部项目'},
                                styles={
                                    'body': {'padding': 0}
                                },
                                style={
                                    'marginBottom': '24px',
                                    'boxShadow': 'rgba(0, 0, 0, 0.1) 0px 4px 12px',
                                },
                            ),
                            fac.AntdCard(
                                fac.AntdSpace(
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        html.Div(
                                                            fac.AntdAvatar(
                                                                mode='image',
                                                                src=item.get(
                                                                    'user'
                                                                ).get('avatar'),
                                                                size='small',
                                                            ),
                                                            style={
                                                                'flex': '0 1',
                                                                'marginRight': '16px',
                                                            },
                                                        ),
                                                        html.Div(
                                                            [
                                                                html.Div(
                                                                    [
                                                                        html.Span(
                                                                            f"{item.get('user').get('name')} 在 "
                                                                        ),
                                                                        html.A(
                                                                            item.get(
                                                                                'group'
                                                                            ).get(
                                                                                'name'
                                                                            ),
                                                                            href=item.get(
                                                                                'group'
                                                                            ).get(
                                                                                'link'
                                                                            ),
                                                                        ),
                                                                        html.Span(
                                                                            f" {item.get('template')} "
                                                                        ),
                                                                        html.A(
                                                                            item.get(
                                                                                'project'
                                                                            ).get(
                                                                                'name'
                                                                            ),
                                                                            href=item.get(
                                                                                'project'
                                                                            ).get(
                                                                                'link'
                                                                            ),
                                                                        ),
                                                                    ],
                                                                    key=item.get(
                                                                        'id'
                                                                    ),
                                                                ),
                                                                html.Div(
                                                                    item.get(
                                                                        'updatedAt'
                                                                    ),
                                                                    style={
                                                                        'color': 'rgba(0,0,0,.45)',
                                                                        'fontSize': '14px',
                                                                        'lineHeight': '22px',
                                                                    },
                                                                ),
                                                            ],
                                                            style={
                                                                'flex': '1 1 auto'
                                                            },
                                                        ),
                                                    ],
                                                    style={'display': 'flex'},
                                                ),
                                                fac.AntdDivider(),
                                            ]
                                        )
                                        for item in activity_list
                                    ],
                                    direction='vertical',
                                    style={
                                        'width': '100%',
                                        'maxHeight': '500px',
                                        'overflowY': 'auto',
                                    },
                                ),
                                title='动态',
                                variant='borderless',
                                style={
                                    'marginBottom': '24px',
                                    'boxShadow': 'rgba(0, 0, 0, 0.1) 0px 4px 12px',
                                },
                            ),
                        ],
                        xl=16,
                        lg=24,
                        md=24,
                        sm=24,
                        xs=24,
                    ),
                    fac.AntdCol(
                        [
                            fac.AntdCard(
                                html.Div(
                                    [
                                        html.A('操作一'),
                                        html.A('操作二'),
                                        html.A('操作三'),
                                        html.A('操作四'),
                                        html.A('操作五'),
                                        fac.AntdButton(
                                            '添加',
                                            type='primary',
                                            size='small',
                                            icon=fac.AntdIcon(icon='antd-plus'),
                                            style={'marginLeft': '20px'},
                                        ),
                                    ],
                                    className='item-group',
                                ),
                                title='快速开始 / 便捷导航',
                                variant='borderless',
                                style={
                                    'marginBottom': '24px',
                                    'boxShadow': 'rgba(0, 0, 0, 0.1) 0px 4px 12px',
                                },
                            ),
                            fac.AntdCard(
                                html.Div(
                                    fact.AntdRadar(
                                        height=343,
                                        data=radar_data,
                                        xField='label',
                                        yField='value',
                                        seriesField='name',
                                        point={},
                                        legend={'position': 'bottom'},
                                    ),
                                    style={
                                        'minHeight': '400px',
                                        'margin': '0 auto',
                                        'paddingTop': '30px',
                                    },
                                ),
                                title='XX 指数',
                                variant='borderless',
                                styles={
                                    'body': {'padding': 0}
                                },
                                style={
                                    'marginBottom': '24px',
                                    'boxShadow': 'rgba(0, 0, 0, 0.1) 0px 4px 12px',
                                },
                            ),
                            fac.AntdCard(
                                html.Div(
                                    fac.AntdRow(
                                        [
                                            fac.AntdCol(
                                                html.A(
                                                    [
                                                        fac.AntdAvatar(
                                                            mode='image',
                                                            src=item.get(
                                                                'logo'
                                                            ),
                                                            size='small',
                                                        ),
                                                        html.Span(
                                                            item.get('member'),
                                                            className='member',
                                                        ),
                                                    ]
                                                ),
                                                span=12,
                                            )
                                            for item in project_list
                                        ]
                                    ),
                                    className='members',
                                ),
                                title='团队',
                                variant='borderless',
                                style={
                                    'marginBottom': '24px',
                                    'boxShadow': 'rgba(0, 0, 0, 0.1) 0px 4px 12px',
                                },
                            ),
                        ],
                        xl=8,
                        lg=24,
                        md=24,
                        sm=24,
                        xs=24,
                        style={'padding': '0 12px'},
                    ),
                ],
                gutter=24,
            ),
            fuc.FefferyStyle(
                rawStyle="""
                    .project-list .card-title {
                        font-size: 0;
                    }

                    .project-list .card-title a {
                        color: rgba(0, 0, 0, 0.85);
                        margin-left: 12px;
                        line-height: 24px;
                        height: 24px;
                        display: inline-block;
                        vertical-align: top;
                        font-size: 14px;
                    }

                    .project-list .card-title a:hover {
                        color: #1890ff;
                    }

                    .project-list .card-description {
                        color: rgba(0, 0, 0, 0.45);
                        height: 44px;
                        line-height: 22px;
                        overflow: hidden;
                    }

                    .project-list .project-item {
                        display: flex;
                        margin-top: 8px;
                        overflow: hidden;
                        font-size: 12px;
                        height: 20px;
                        line-height: 20px;
                    }

                    .project-list .project-item a {
                        color: rgba(0, 0, 0, 0.45);
                        display: inline-block;
                        flex: 1 1 0;
                    }

                    .project-list .project-item a:hover {
                        color: #1890ff;
                    }

                    .project-list .project-item .datetime {
                        color: rgba(0, 0, 0, 0.25);
                        flex: 0 0 auto;
                        float: right;
                    }

                    .project-list .ant-card-meta-description {
                        color: rgba(0, 0, 0, 0.45);
                        height: 44px;
                        line-height: 22px;
                        overflow: hidden;
                    }

                    .item-group {
                        padding: 20px 0 8px 24px;
                        font-size: 0;
                    }

                    .item-group a {
                        color: rgba(0, 0, 0, 0.65);
                        display: inline-block;
                        font-size: 14px;
                        margin-bottom: 13px;
                        width: 25%;
                        padding-left: 20px;
                    }

                    .members a {
                        display: block;
                        margin: 12px 0;
                        line-height: 24px;
                        height: 24px;
                    }

                    .members a .member {
                        font-size: 14px;
                        color: rgba(0, 0, 0, 0.65);
                        line-height: 24px;
                        max-width: 100px;
                        vertical-align: top;
                        margin-left: 12px;
                        transition: all 0.3s;
                        display: inline-block;
                    }

                    .members a .member:hover span {
                        color: #1890ff;
                    }
                    """
            ),
        ]
    )
