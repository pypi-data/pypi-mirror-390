# coding: utf-8

from enum import Enum
from typing import List, Callable, Any


class SourceEnum(Enum):
    # For CustoCustomizedAPIView which is modified from Django's APIView by the backend team of xmov.ai
    data = "data"
    query_params = "query_params"
    xmov_data = "xmov_data"  # alias of data
    xmov_query_params = "xmov_query_params"  # alias of query_params
    xmov_method = "xmov_method"
    xmov_GET = "xmov_GET"
    xmov_POST = "xmov_POST"
    xmov_COOKIES = "xmov_COOKIES"
    xmov_FILES = "xmov_FILES"
    xmov_META = "xmov_META"

    # For plain django request
    method = "method"
    GET = "GET"
    POST = "POST"
    COOKIES = "COOKIES"
    FILES = "FILES"
    META = "META"


class Field:
    data_type = None

    def __init__(self, source: SourceEnum,
                 validators: List[Callable] = [],
                 allow_none: bool = False,
                 post_callable: Callable = None,
                 parser: Callable = None):
        """ 初始化Field对象。 
            ⚠️注意：
                这里如果提供了post_callable，则会在检查data_type之后调用post_callable但会造成data_type不准确。
                例如，data_type是str, 但post_callable处理之后是其他类型。所以data_type应该是一个通用的类型，
                比如object。所以AnyField是更好的选择。
        Args:
            source: 数据来源。
            validators: 校验器列表。
            allow_none: 是否允许None值。
            post_callable: 后处理函数。
        """
        self.source = source
        self.validators = validators
        self.allow_none = allow_none
        self.post_callable = post_callable
        self.parser = parser

    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value):
        """ 设置Field的值。
            1. 检查value是否为None
            2. 检查value是否为正确的类型
            3. 如果post_callable提供，则调用它
            4. 设置value到instance
        Args:
            instance: 类实例。
            value: 要设置的值。
        """
        if value is None:
            if not self.allow_none:
                raise ValueError(f"value must not be None")
        elif not isinstance(value, self.data_type):
            raise ValueError(
                f"value must be {self.data_type}, but got {type(value)}")
        if self.post_callable and isinstance(self.post_callable, Callable):
            value = self.post_callable(value)
        elif self.post_callable and not isinstance(self.post_callable, Callable):
            raise ValueError(
                f"post_callable must be a callable, but got {type(self.post_callable)}")
        else:
            value = value
        self.value = value

    def parse_value(self, request, field_name: str):
        """  从request中解析数据。
        Args:
            request: 请求对象。 兼容common_rest.ComptiableRequest和DRF的Request对象。
            field_name: 字段名称。
        Returns:
            value: 解析后的值。
        """
        # For CompatiableRequest
        field: 'Field' = self
        if field.source == SourceEnum.data or field.source == SourceEnum.xmov_data:
            data = request.data
        elif field.source == SourceEnum.query_params or field.source == SourceEnum.xmov_query_params:
            data = request.query_params
        elif field.source == SourceEnum.xmov_method:
            data = request._request.method
        elif field.source == SourceEnum.xmov_GET:
            data = request._request.GET
        elif field.source == SourceEnum.xmov_POST:
            data = request._request.POST
        elif field.source == SourceEnum.xmov_COOKIES:
            data = request._request.COOKIES
        elif field.source == SourceEnum.xmov_FILES:
            data = request._request.FILES
        elif field.source == SourceEnum.xmov_META:
            data = request._request.META

        # For plain django request
        elif field.source == SourceEnum.method:
            data = request.method
        elif field.source == SourceEnum.GET:
            data = request.GET
        elif field.source == SourceEnum.POST:
            data = request.POST
        elif field.source == SourceEnum.COOKIES:
            data = request.COOKIES
        elif field.source == SourceEnum.FILES:
            data = request.FILES
        elif field.source == SourceEnum.META:
            data = request.META
        else:
            raise ValueError(f"invalid source: {field.source}")
        
        if isinstance(self.parser, Callable):
            value = self.parser(data)
        else:
            if field.source in [SourceEnum.xmov_method, SourceEnum.method]:
                value = data
            else:
                value = data.get(field_name) 
        return value

    def validate_value(self, value):
        """ 校验值。
            1. 检查value是否为None
            2. 检查value是否为正确的类型
            3. 如果post_callable提供，则调用它
            4. 设置value到instance
        Args:
            value: 要校验的值。
        Returns:
            value: 校验后的值。
        """
        if self.allow_none and value is None:
            return

        if not isinstance(value, self.data_type):
            raise ValueError(
                f"value must be {self.data_type}, but got {type(value)}")

        for validator in self.validators:
            validator(value)


class IntegerField(Field):
    data_type = int


class StringField(Field):
    data_type = str


class BooleanField(Field):
    data_type = bool


class DictField(Field):
    data_type = dict


class AnyField(Field):
    def __init__(self, *args, **kwargs):
        """ AnyField允许用户自定义数据类型。
        Args:
            *args: 参数。
            **kwargs: 关键字参数。
                data_type: 数据类型。
        """
        data_type = kwargs.pop('data_type', object)
        super().__init__(*args, **kwargs)
        self.data_type = data_type
