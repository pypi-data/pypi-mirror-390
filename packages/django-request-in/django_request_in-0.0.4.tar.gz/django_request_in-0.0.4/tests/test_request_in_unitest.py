import unittest

from django_request_in import IntegerField, StringField, BooleanField, AnyField, SourceEnum, greater_than_zero, request_decorator, Request, SchemaIn


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

class TestDescriptor(unittest.TestCase):
    def setUp(self):
        self.request = Request(
            data={"x": 1, "y": 'xx', "z": False, "dog_name": "Husky"},
            query_params={"x": 1, "y": None, "z": True}
        )

    @request_decorator(
        x=IntegerField(source=SourceEnum.data, validators=[greater_than_zero]),
        y=StringField(source=SourceEnum.data, allow_none=True),
        z=BooleanField(source=SourceEnum.data),
        dog=AnyField(source=SourceEnum.data, data_type=Dog, parser=dog_parser, allow_none=True)
    )
    def request_in(self, request, x=None, y=None, z=None, dog=None):
        print(x)
        print(y)
        print(z)
        print(dog)
        return dict(x=x, y=y, z=z, dog=dog)

    def test_request_decorator(self):
        print('===> test_request_decorator <===')
        response = self.request_in(self.request)
        print('---->response', response)

    def test_descriptor(self):
        request = Request(
            data={"x": 1, "y": 'xx', "z": False},
            query_params={"x": 1, "y": None, "z": True}
        )
        p = SchemaIn(request)
        print(p.x)
        print(p.y)
        print(p.z)
        p.x = 4
        print(p.x)

    def test_xx(self):
        pass
