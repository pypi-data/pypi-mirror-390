# coding: utf-8

def greater_than_zero(value):
    """ 校验器 """
    if not isinstance(value, (int, float)):
        raise ValueError(f"value must be a number, but got {type(value)}")  
