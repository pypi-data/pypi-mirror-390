from django_request_in import SchemaIn, Request, BaseSchemaIn, IntegerField, StringField, BooleanField, SourceEnum, greater_than_zero


class SchemaIn(BaseSchemaIn):
    a = IntegerField(source=SourceEnum.data, validators=[greater_than_zero])
    b = StringField(source=SourceEnum.data, allow_none=True)
    c = BooleanField(source=SourceEnum.data)

    def to_dict(self):
        return {
            "a": self.a,
            "b": self.b,
            "c": self.c
        }


def test_schema_in():
    request = Request(
        data={"a": 1, "b": 'xx', "c": False}, 
        query_params={"a": 1, "b": None, "c": True}
        )
    schema = SchemaIn(request)
    print(schema.to_dict())