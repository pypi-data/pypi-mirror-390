# coding: utf-8

from typing import Dict, Callable
from django_request_in.fields import SourceEnum, Field


def view_decorator(**fileld_kwargs: Field) -> Callable:
    """ Decorator for request_in.
    Args:
        **fileld_kwargs: Keyword arguments for the fields. The key is the field name, and the value is the Field-like object.
    Returns:
        A decorator function that wraps the view function.
    """
    def wrapper(view_func):
        def inner_wrapper(self, request, *args, **kwargs):
            params = {}
            for field_name, field in fileld_kwargs.items():
                value = field.parse_value(request, field_name)
                field.validate_value(value)
                params[field_name] = value
            return view_func(self, request, **params)
        return inner_wrapper
    return wrapper


def function_decorator(**fileld_kwargs: Field) -> Callable:
    def wrapper(func):
        def inner_wrapper(request, *args, **kwargs):
            params = {}
            for field_name, field in fileld_kwargs.items():
                value = field.parse_value(request, field_name)
                field.validate_value(value)
                params[field_name] = value
            return func(request, **params)
        return inner_wrapper
    return wrapper
