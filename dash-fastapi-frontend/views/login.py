import feffery_antd_components as fac
import feffery_utils_components as fuc
import time
from dash import dcc, html
from callbacks import login_c  # noqa: F401
from config.env import AppConfig


def render():
    return html.Div(
        [
            dcc.Store(id='login-success-container'),
            dcc.Store(id='captcha_image-session_id-container'),
            fuc.FefferyKeyPress(
                id='keyboard-enter-submit',
                keys='enter',
            ),
            html.Div(
                [
                    html.Div(
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Span(
                                                    html.Img(
                                                        alt='logo',
                                                        src='/assets/imgs/logo.png',
                                                    ),
                                                    className='ant-pro-form-login-logo',
                                                ),
                                                html.Span(
                                                    AppConfig.app_name,
                                                    className='ant-pro-form-login-title',
                                                ),
                                            ],
                                            className='ant-pro-form-login-header',
                                        ),
                                        html.Div(
                                            f'{AppConfig.app_name} 是 Dash 中最完备的中后台管理系统',
                                            className='ant-pro-form-login-desc ',
                                        ),
                                    ],
                                    className='ant-pro-form-login-top',
                                ),
                                html.Div(
                                    [
                                        fac.AntdForm(
                                            fac.AntdFlex(
                                                [
                                                    fac.AntdFormItem(
                                                        fac.AntdInput(
                                                            placeholder='请输入用户名',
                                                            id='login-username',
                                                            size='large',
                                                            prefix=fac.AntdIcon(
                                                                icon='antd-user'
                                                            ),
                                                        ),
                                                        id='login-username-form-item',
                                                    ),
                                                    fac.AntdFormItem(
                                                        fac.AntdInput(
                                                            placeholder='请输入密码',
                                                            id='login-password',
                                                            mode='password',
                                                            passwordUseMd5=True,
                                                            size='large',
                                                            prefix=fac.AntdIcon(
                                                                icon='antd-lock'
                                                            ),
                                                        ),
                                                        id='login-password-form-item',
                                                    ),
                                                    html.Div(
                                                        fac.AntdFormItem(
                                                            [
                                                                fac.AntdFlex(
                                                                    [
                                                                        fac.AntdInput(
                                                                            placeholder='请输入验证码',
                                                                            id='login-captcha',
                                                                            size='large',
                                                                            prefix=fac.AntdIcon(
                                                                                icon='antd-check-circle'
                                                                            ),
                                                                        ),
                                                                        fuc.FefferyDiv(
                                                                            [
                                                                                fac.AntdImage(
                                                                                    id='login-captcha-image',
                                                                                    src='',
                                                                                    height=39.6,
                                                                                    width=100,
                                                                                    preview=False,
                                                                                    style={
                                                                                        'border': '1px solid #d9d9d9',
                                                                                        'borderRadius': '8px',
                                                                                    },
                                                                                )
                                                                            ],
                                                                            id='login-captcha-image-container',
                                                                        ),
                                                                    ],
                                                                    align='center',
                                                                    gap='small',
                                                                ),
                                                            ],
                                                            id='login-captcha-form-item',
                                                        ),
                                                        id='captcha-row-container',
                                                    ),
                                                    fac.AntdFormItem(
                                                        fac.AntdFlex(
                                                            [
                                                                fac.AntdCheckbox(
                                                                    id='login-remember-me',
                                                                    label='记住我',
                                                                ),
                                                                fuc.FefferyDiv(
                                                                    id='forget-password-link-container'
                                                                ),
                                                            ],
                                                            align='center',
                                                            justify='space-between',
                                                        ),
                                                        style={
                                                            'marginBottom': '10px'
                                                        },
                                                    ),
                                                    fac.AntdFormItem(
                                                        fac.AntdButton(
                                                            '登录',
                                                            id='login-submit',
                                                            type='primary',
                                                            block=True,
                                                            size='large',
                                                        ),
                                                        style={
                                                            'marginBottom': '15px'
                                                        },
                                                    ),
                                                    fac.AntdFormItem(
                                                        fuc.FefferyDiv(
                                                            id='register-user-link-container',
                                                        ),
                                                    ),
                                                ],
                                                vertical=True,
                                            ),
                                            layout='vertical',
                                            style={'width': '100%'},
                                        ),
                                    ],
                                    className='ant-pro-form-login-main',
                                    style={
                                        'width': '328px',
                                        'minWidth': '280px',
                                        'maxWidth': '75vw',
                                    },
                                ),
                            ],
                            className='ant-pro-form-login-container',
                        ),
                        style={'flex': '1', 'padding': '32px 0'},
                    ),
                    fac.AntdFooter(
                        html.Div(
                            html.Div(
                                html.Span(
                                    f'Copyright © 2023-{time.localtime().tm_year} insistence.tech All Rights Reserved.',
                                    className='anticon anticon-copyright',
                                    role='img',
                                    **{'aria-label': 'copyright'},
                                ),
                                className='ant-pro-global-footer-copyright',
                            ),
                            className='ant-pro-global-footer',
                        ),
                        style={
                            'padding': '0px',
                            'background': 'none',
                        },
                    ),
                ],
                id='login-page',
                className='acss-trkbkn',
            ),
            fuc.FefferyTimeout(
                id='login-timeout',
                delay=500,
            ),
            fuc.FefferyStyle(
                rawStyle="""
                    .acss-trkbkn {
                        display: -webkit-box;
                        display: -webkit-flex;
                        display: -ms-flexbox;
                        display: flex;
                        -webkit-flex-direction: column;
                        -ms-flex-direction: column;
                        flex-direction: column;
                        height: 100vh;
                        overflow: auto;
                        -webkit-background-size: 100% 100%;
                        background-size: 100% 100%;
                    }
                    .ant-pro-form-login-container {
                        display: flex;
                        flex: 1;
                        flex-direction: column;
                        height: 100%;
                        padding-inline: 32px;
                        padding-block: 24px;
                        overflow: auto;
                        background: inherit;
                    }
                    .ant-pro-form-login-top {
                        text-align: center;
                    }
                    .ant-pro-form-login-header {
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        height: 44px;
                        line-height: 44px;
                    }
                    .ant-pro-form-login-logo {
                        width: 44px;
                        height: 44px;
                        margin-inline-end: 16px;
                        vertical-align: top;
                    }
                    .ant-pro-form-login-logo img {
                        width: 100%;
                    }
                    img {
                        vertical-align: middle;
                        border-style: none;
                    }
                    .ant-pro-form-login-title {
                        position: relative;
                        inset-block-start: 2px;
                        font-weight: 600;
                        font-size: 33px;
                    }
                    .ant-pro-form-login-desc {
                        margin-block-start: 12px;
                        margin-block-end: 40px;
                        color: rgba(0, 0, 0, 0.65);
                        font-size: 14px;
                    }
                    .ant-pro-form-login-main {
                        margin: 0 auto;
                    }
                    .ant-pro-global-footer {
                        margin-block: 0;
                        margin-block-start: 48px;
                        margin-block-end: 24px;
                        margin-inline: 0;
                        padding-block: 0;
                        padding-inline: 16px;
                        text-align: center;
                    }
                    .ant-pro-global-footer-copyright {
                        font-size: 14px;
                        color: rgba(0, 0, 0, 0.88);
                    }
                    .anticon {
                        display: inline-flex;
                        align-items: center;
                        color: inherit;
                        font-style: normal;
                        line-height: 0;
                        text-align: center;
                        text-transform: none;
                        vertical-align: -0.125em;
                        text-rendering: optimizeLegibility;
                        -webkit-font-smoothing: antialiased;
                        -moz-osx-font-smoothing: grayscale;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji';
                    }
                """
            ),
        ],
    )
