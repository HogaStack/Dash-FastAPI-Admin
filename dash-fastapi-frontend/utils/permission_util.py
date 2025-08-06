from typing import List, Union
from utils.cache_util import CacheManager


class PermissionManager:
    """
    权限管理器
    """

    @classmethod
    def check_perms(cls, perm: Union[str, List], is_strict: bool = False):
        """
        校验当前用户是否具有相应的权限标识

        :param perm: 权限标识
        :param is_strict: 当传入的权限标识是list类型时，是否开启严格模式，开启表示会校验列表中的每一个权限标识，所有的校验结果都需要为True才会通过
        :return: 校验结果
        """
        user_perm_list = (
            CacheManager.get('permissions').get('perms')
            if CacheManager.get('permissions')
            else []
        )
        if '*:*:*' in user_perm_list:
            return True
        if isinstance(perm, str):
            if perm in user_perm_list:
                return True
        if isinstance(perm, list):
            if is_strict:
                if all([perm_str in user_perm_list for perm_str in perm]):
                    return True
            else:
                if any([perm_str in user_perm_list for perm_str in perm]):
                    return True
        return False

    @classmethod
    def check_roles(cls, role_key: Union[str, List], is_strict: bool = False):
        """
        根据角色校验当前用户是否具有相应的权限

        :param role_key: 角色标识
        :param is_strict: 当传入的角色标识是list类型时，是否开启严格模式，开启表示会校验列表中的每一个角色标识，所有的校验结果都需要为True才会通过
        :return: 校验结果
        """
        user_role_list = (
            CacheManager.get('permissions').get('roles')
            if CacheManager.get('permissions')
            else []
        )
        if isinstance(role_key, str):
            if role_key in user_role_list:
                return True
        if isinstance(role_key, list):
            if is_strict:
                if all(
                    [
                        role_key_str in user_role_list
                        for role_key_str in role_key
                    ]
                ):
                    return True
            else:
                if any(
                    [
                        role_key_str in user_role_list
                        for role_key_str in role_key
                    ]
                ):
                    return True
        return False
