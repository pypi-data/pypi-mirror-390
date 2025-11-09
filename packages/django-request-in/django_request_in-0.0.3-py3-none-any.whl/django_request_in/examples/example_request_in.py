# coding: utf-8

from django_request_in.base_schema_in import BaseSchemaIn
from django_request_in.field import Integer, String, Boolean, SourceEnum
from django_request_in.validators import validate_x

class Request:
    """ 请求数据 """

    def __init__(self, data, query_params):
        self.data = data
        self.query_params = query_params


# 数据模型
class SchemaIn(BaseSchemaIn):
    """ 支持从request中解析数据，支持校验。"""
    x = Integer(source=SourceEnum.data, validators=[validate_x])
    y = String(source=SourceEnum.query_params, allow_none=True)
    z = Boolean(source=SourceEnum.query_params)


def main():
    request = Request(data={"x": 1, "y": 'xx', "z": False}, query_params={"x": 1, "y": None, "z": True})
    schema = SchemaIn(request)
    print(schema.x)
    print(schema.y)
    print(schema.z)

if __name__ == "__main__":
    main()
