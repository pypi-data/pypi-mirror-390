# coding: utf-8

class Request:
    """ 请求数据 """

    def __init__(self, data, query_params):
        self.data = data
        self.query_params = query_params
