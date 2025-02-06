import requests
from flask import session, request
from typing import Dict, Optional
from config.constant import HttpStatusConstant
from config.enums import ApiMethod
from config.env import ApiConfig, AppConfig
from config.exception import (
    AuthException,
    RequestException,
    ServiceException,
    ServiceWarning,
)
from utils.cache_util import CacheManager
from utils.common_util import FilterUtil
from utils.log_util import logger


def api_request(
    url: str,
    method: ApiMethod,
    base_url: Optional[str] = ApiConfig.BaseUrl,
    headers: Optional[Dict] = {},
    params: Optional[Dict] = None,
    data: Optional[Dict] = None,
    json: Optional[Dict] = None,
    files: Optional[Dict] = None,
    timeout: Optional[int] = None,
    stream: Optional[bool] = False,
):
    """
    Api请求方法

    :param url: 请求url
    :param method: 请求方法
    :param base_url: 请求url前缀
    :param headers: 请求头
    :param params: 查询参数
    :param data: 表单参数
    :param json: 请求体
    :param files: 请求文件
    :param timeout: 请求超时时间
    :param stream: 是否为流式请求
    :return: 请求结果
    """
    api_url = base_url + url
    api_method = method.value
    user_agent = request.headers.get('User-Agent')
    authorization = (
        session.get('Authorization') if session.get('Authorization') else ''
    )
    remote_addr = (
        request.headers.get('X-Forwarded-For')
        if AppConfig.app_env == 'prod'
        else request.remote_addr
    )
    merged_headers = {'is_token': True, **headers}
    is_token = merged_headers.get('is_token')
    api_headers = {
        k: v for k, v in merged_headers.items() if isinstance(v, (str, bytes))
    }
    api_headers.update(
        {
            'remote_addr': remote_addr,
            'User-Agent': user_agent,
            'is_browser': 'no',
        }
    )
    if is_token:
        api_headers.update({'Authorization': 'Bearer ' + authorization})
    if api_method == 'get':
        response = requests.get(
            url=api_url,
            params=params,
            data=data,
            json=json,
            files=files,
            headers=api_headers,
            timeout=timeout,
            stream=stream,
        )
    elif api_method == 'post':
        response = requests.post(
            url=api_url,
            params=params,
            data=data,
            json=json,
            files=files,
            headers=api_headers,
            timeout=timeout,
            stream=stream,
        )
    elif api_method == 'delete':
        response = requests.delete(
            url=api_url,
            params=params,
            data=data,
            json=json,
            files=files,
            headers=api_headers,
            timeout=timeout,
            stream=stream,
        )
    elif api_method == 'put':
        response = requests.put(
            url=api_url,
            params=params,
            data=data,
            json=json,
            files=files,
            headers=api_headers,
            timeout=timeout,
            stream=stream,
        )
    elif api_method == 'patch':
        response = requests.patch(
            url=api_url,
            params=params,
            data=data,
            json=json,
            files=files,
            headers=api_headers,
            timeout=timeout,
            stream=stream,
        )

    data_list = [params, data, json, files]
    status_code = response.status_code
    request_user = (
        CacheManager.get('user_info').get('user_name')
        if CacheManager.get('user_info')
        else None
    )
    request_params = ','.join(
        [
            str(
                FilterUtil.fliter_params(
                    params_name=['password', 'old_password', 'new_password'],
                    fliter_dict=x,
                )
            )
            for x in data_list
            if x
        ]
    )
    log_message = LogMessage(
        request_user,
        remote_addr,
        api_method,
        url,
        request_params,
    )
    if status_code == HttpStatusConstant.SUCCESS:
        if stream:
            logger.info(log_message.generate('获取成功'))
            return response
        else:
            response_code = response.json().get('code')
            response_message = response.json().get('msg')
            response_log = log_message.generate(response_message)
            if response_code == HttpStatusConstant.SUCCESS:
                logger.info(response_log)
                return response.json()
            elif response_code == HttpStatusConstant.UNAUTHORIZED:
                logger.warning(response_log)
                raise AuthException(message=response_message)
            elif response_code == HttpStatusConstant.ERROR:
                logger.error(response_log)
                raise ServiceException(message=response_message)
            elif response_code == HttpStatusConstant.WARN:
                logger.warning(response_log)
                raise ServiceWarning(message=response_message)
            else:
                logger.error(response_log)
                raise RequestException(message=response_message)
    else:
        logger.error(log_message.generate('请求异常'))
        raise RequestException(message='请求异常')


class LogMessage:
    def __init__(
        self,
        request_user: str,
        request_ip: str,
        request_method: str,
        request_url: str,
        request_params: str,
    ):
        self.request_user = request_user
        self.request_ip = request_ip
        self.request_method = request_method
        self.request_url = request_url
        self.request_params = request_params

    def generate(self, message: str):
        return f'[api]请求人:{self.request_user}||请求IP:{self.request_ip}||请求方法:{self.request_method}||请求Api:{self.request_url}||请求参数:{self.request_params}||请求结果:{message}'
