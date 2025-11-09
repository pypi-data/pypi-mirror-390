# coding: utf-8

from django_request_in import SourceEnum, Field, IntegerField, StringField, BooleanField, greater_than_zero


class BaseSchemaIn:
    def __init__(self, request: 'Request'):
        filed_keys = [k for k, v in self.__class__.__dict__.items()
                      if isinstance(v, Field)]
        fileds = [v for k, v in self.__class__.__dict__.items()
                  if isinstance(v, Field)]
        items = zip(filed_keys, fileds)
        print(filed_keys)
        for key, field in items:
            value = field.parse_value(request, field_name=key)
            field.validate_value(value)
            setattr(self, key, value)


class SchemaIn(BaseSchemaIn):
    """ 支持从request中解析数据，支持校验。
    
    Args:
        request: 请求对象。
    Returns:
        SchemaIn对象。
    Raises:
        ValueError: 如果请求对象不是Request类型。
    Example:
        >>> request = Request(data={"x": 1, "y": 'xx', "z": False}, query_params={"x": 1, "y": None, "z": True})
        >>> schema = SchemaIn(request)  # 实际使用时，request可以是ComptiableRequest或DRF的Request对象。
        >>> print(schema.x)
        >>> print(schema.y)
        >>> print(schema.z)
    """
    x = IntegerField(source=SourceEnum.data, validators=[greater_than_zero])
    y = StringField(source=SourceEnum.query_params, allow_none=True)
    z = BooleanField(source=SourceEnum.query_params)
