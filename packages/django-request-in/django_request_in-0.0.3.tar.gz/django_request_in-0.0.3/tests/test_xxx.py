# coding: utf-8
import pytest
from django_request_in import IntegerField, StringField, BooleanField, AnyField, SourceEnum, greater_than_zero, view_decorator, function_decorator, Request


class Dog(object):
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f"Dog(name={self.name})"

    def __repr__(self):
        return self.__str__()


def dog_parser(data: dict) -> Dog:
    dog_name = data.get("dog_name", "default")
    # return Dog(dog_name)
    return None


@pytest.fixture
def request_data():
    return Request(
        data={"x": 1, "y": 'xx', "z": False, "dog_name": "Husky"},
        query_params={"x": 1, "y": None, "z": True}
    )


@function_decorator(
    x=IntegerField(source=SourceEnum.data, validators=[greater_than_zero]),
    y=StringField(source=SourceEnum.data, allow_none=True),
    z=BooleanField(source=SourceEnum.data),
    dog=AnyField(source=SourceEnum.data, data_type=Dog,
                parser=dog_parser, allow_none=True)
)
def request_in(request_data, x=None, y=None, z=None, dog=None):
    """  function_decorator 装饰器示例。function_decorator可以从request_data解析出参数作为函数参数。
    Args:
        request_data: 请求数据。
        x: 整数。
        y: 字符串。
        z: 布尔值。
        dog: 狗对象。
    Returns:
        dict: 返回数据。
    """
    print(x)
    print(y)
    print(z)
    print(dog)
    return dict(x=x, y=y, z=z, dog=dog)


def test_request_in(request_data):
    response = request_in(request_data)
    print(response)

