from typing import Union
from config.enums import ApiMethod
from utils.request import api_request


class UserApi:
    """
    用户管理模块相关接口
    """

    @classmethod
    def list_user(cls, query: dict):
        """
        查询用户列表接口

        :param query: 查询用户参数
        :return:
        """
        return api_request(
            url='/system/user/list',
            method=ApiMethod.GET,
            params=query,
        )

    @classmethod
    def get_user(cls, user_id: Union[int, str]):
        """
        查询用户详情接口

        :param user_id: 用户id
        :return:
        """
        return api_request(
            url=f'/system/user/{user_id}',
            method=ApiMethod.GET,
        )

    @classmethod
    def add_user(cls, json: dict):
        """
        新增用户接口

        :param json: 新增用户参数
        :return:
        """
        return api_request(
            url='/system/user',
            method=ApiMethod.POST,
            json=json,
        )

    @classmethod
    def update_user(cls, json: dict):
        """
        修改用户接口

        :param json: 修改用户参数
        :return:
        """
        return api_request(
            url='/system/user',
            method=ApiMethod.PUT,
            json=json,
        )

    @classmethod
    def del_user(cls, user_id: str):
        """
        删除用户接口

        :param user_id: 用户id
        :return:
        """
        return api_request(
            url=f'/system/user/{user_id}',
            method=ApiMethod.DELETE,
        )

    @classmethod
    def download_template(cls):
        """
        下载用户导入模板接口

        :return:
        """
        return api_request(
            url='/system/user/importTemplate',
            method=ApiMethod.POST,
            stream=True,
        )

    @classmethod
    def import_user(cls, file: bytes, update_support: bool):
        """
        导入用户接口

        :param file: 导入模板文件
        :param update_support: 是否更新已存在的用户数据
        :return:
        """
        return api_request(
            url='/system/user/importData',
            method=ApiMethod.POST,
            files={'file': file},
            params={'update_support': update_support},
        )

    @classmethod
    def export_user(cls, data: dict):
        """
        导出用户接口

        :param data: 导出用户参数
        :return:
        """
        return api_request(
            url='/system/user/export',
            method=ApiMethod.POST,
            data=data,
            stream=True,
        )

    @classmethod
    def reset_user_pwd(cls, user_id: int, password: str):
        """
        用户密码重置接口

        :param user_id: 用户id
        :param password: 用户密码
        :return:
        """
        return api_request(
            url='/system/user/resetPwd',
            method=ApiMethod.PUT,
            json=dict(user_id=user_id, password=password),
        )

    @classmethod
    def change_user_status(cls, user_id: int, status: str):
        """
        用户状态修改接口

        :param user_id: 用户id
        :param password: 用户状态
        :return:
        """
        return api_request(
            url='/system/user/changeStatus',
            method=ApiMethod.PUT,
            json=dict(user_id=user_id, status=status),
        )

    @classmethod
    def get_user_profile(cls):
        """
        查询用户个人信息接口

        :return:
        """
        return api_request(
            url='/system/user/profile',
            method=ApiMethod.GET,
        )

    @classmethod
    def update_user_profile(cls, json: dict):
        """
        修改用户个人信息接口

        :param json: 修改用户个人信息参数
        :return:
        """
        return api_request(
            url='/system/user/profile',
            method=ApiMethod.PUT,
            json=json,
        )

    @classmethod
    def update_user_pwd(cls, old_password: str, new_password: str):
        """
        用户个人密码重置接口

        :param old_password: 用户旧密码
        :param new_password: 用户新密码
        :return:
        """
        return api_request(
            url='/system/user/profile/updatePwd',
            method=ApiMethod.PUT,
            data=dict(old_password=old_password, new_password=new_password),
        )

    @classmethod
    def upload_avatar(cls, files: dict):
        """
        用户头像上传接口

        :param files: 用户头像参数
        :return:
        """
        return api_request(
            url='/system/user/profile/avatar',
            method=ApiMethod.POST,
            files=files,
        )

    @classmethod
    def get_auth_role(cls, user_id: int):
        """
        查询授权角色接口
        """
        return api_request(
            url=f'/system/user/authRole/{user_id}',
            method=ApiMethod.GET,
        )

    @classmethod
    def update_auth_role(cls, params: dict):
        """
        保存授权角色接口

        :param params: 授权角色参数
        :return:
        """
        return api_request(
            url='/system/user/authRole',
            method=ApiMethod.PUT,
            params=params,
        )

    @classmethod
    def dept_tree_select(cls):
        """
        查询部门下拉树结构接口

        :return:
        """
        return api_request(
            url='/system/user/deptTree',
            method=ApiMethod.GET,
        )
