import feffery_antd_components as fac
import feffery_utils_components as fuc
from dash import dcc, html
from callbacks import forget_c  # noqa: F401


def render():
    return html.Div(
        [
            fac.AntdCard(
                [
                    dcc.Store(
                        id='sms_code-session_id-container',
                        storage_type='session',
                    ),
                    fac.AntdForm(
                        [
                            fac.AntdFlex(
                                [
                                    fac.AntdFormItem(
                                        fac.AntdInput(
                                            placeholder='请输入用户名',
                                            id='forget-username',
                                            size='large',
                                            prefix=fac.AntdIcon(
                                                icon='antd-user'
                                            ),
                                        ),
                                        id='forget-username-form-item',
                                    ),
                                    fac.AntdFormItem(
                                        fac.AntdInput(
                                            placeholder='请输入新密码',
                                            id='forget-password',
                                            mode='password',
                                            passwordUseMd5=True,
                                            size='large',
                                            prefix=fac.AntdIcon(
                                                icon='antd-lock'
                                            ),
                                        ),
                                        id='forget-password-form-item',
                                    ),
                                    fac.AntdFormItem(
                                        fac.AntdInput(
                                            placeholder='请再次输入新密码',
                                            id='forget-password-again',
                                            mode='password',
                                            passwordUseMd5=True,
                                            size='large',
                                            prefix=fac.AntdIcon(
                                                icon='antd-lock'
                                            ),
                                        ),
                                        id='forget-password-again-form-item',
                                    ),
                                    fac.AntdFormItem(
                                        fac.AntdFlex(
                                            [
                                                fac.AntdInput(
                                                    placeholder='请输入短信验证码',
                                                    id='forget-input-captcha',
                                                    size='large',
                                                    prefix=fac.AntdIcon(
                                                        icon='antd-check-circle'
                                                    ),
                                                    style={'flex': '1 1 0%'},
                                                ),
                                                fac.AntdButton(
                                                    '获取验证码',
                                                    id='get-message-code',
                                                    size='large',
                                                ),
                                            ],
                                            gap='small',
                                        ),
                                        id='forget-captcha-form-item',
                                    ),
                                    fac.AntdFormItem(
                                        fac.AntdButton(
                                            '保存',
                                            id='forget-submit',
                                            type='primary',
                                            block=True,
                                            size='large',
                                        ),
                                        style={'marginTop': '20px'},
                                    ),
                                ],
                                vertical=True,
                            ),
                        ],
                        layout='vertical',
                        style={'width': '100%'},
                    ),
                    fuc.FefferyCountDown(id='message-code-count-down'),
                ],
                id='forget-form-container',
                title='重置密码',
                hoverable=True,
                extraLink={
                    'content': '返回登录',
                    'href': '/login',
                    'target': '_self',
                    'style': {'fontSize': '16px'},
                },
                styles={
                    'header': {
                        'fontWeight': 'bold',
                        'textAlign': 'center',
                        'fontSize': '30px',
                    }
                },
                style={
                    'position': 'fixed',
                    'top': '16%',
                    'left': '50%',
                    'width': '480px',
                    'minWidth': '420px',
                    'maxWidth': '75vw',
                    'padding': '0px 30px',
                    'transform': 'translateX(-50%)',
                },
            ),
        ],
        id='forget-page',
    )
