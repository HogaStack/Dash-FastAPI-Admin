from feffery_antd_components import AntdRadioGroup
from typing import Any, Dict, List, Literal, Optional, Union
from uuid import uuid4
from utils.dict_util import DictManager


class ApiRadioGroup(AntdRadioGroup):
    def __init__(
        self,
        dict_type: str,
        id: Optional[Union[str, Dict]] = str(uuid4()),
        key: Optional[str] = None,
        style: Optional[Dict] = None,
        className: Optional[Union[str, Dict]] = None,
        name: Optional[str] = None,
        direction: Optional[Literal['horizontal', 'vertical']] = 'horizontal',
        disabled: Optional[bool] = False,
        size: Optional[Literal['small', 'middle', 'large']] = 'middle',
        value: Optional[Any] = None,
        defaultValue: Optional[Any] = None,
        optionType: Optional[Literal['default', 'button']] = 'default',
        buttonStyle: Optional[Literal['outline', 'solid']] = 'outline',
        readOnly: Optional[bool] = False,
        batchPropsNames: Optional[List] = None,
        batchPropsValues: Optional[Dict] = None,
        persistence: Optional[Any] = None,
        persisted_props: Optional[Any] = None,
        persistence_type: Optional[Any] = None,
        **kwargs: Any,
    ):
        self.options = DictManager.get_dict_options(dict_type=dict_type)[0]
        super().__init__(
            id=id,
            key=key,
            style=style,
            className=className,
            name=name,
            direction=direction,
            options=self.options,
            disabled=disabled,
            size=size,
            value=value,
            defaultValue=defaultValue,
            optionType=optionType,
            buttonStyle=buttonStyle,
            readOnly=readOnly,
            batchPropsNames=batchPropsNames,
            batchPropsValues=batchPropsValues,
            persistence=persistence,
            persisted_props=persisted_props,
            persistence_type=persistence_type,
            **kwargs,
        )
