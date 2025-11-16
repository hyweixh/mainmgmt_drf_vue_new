"""
分页类
"""

from rest_framework.pagination import PageNumberPagination


class Pagination(PageNumberPagination):
    page_query_param = "page"       # 页码
    page_size_query_param = 'size'  # 指定每页多少条数据
    page_size = 10                   # 默认一页展示