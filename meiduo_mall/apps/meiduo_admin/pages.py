from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class Mypage(PageNumberPagination):
    page_size = 5
    max_page_size = 10
    page_query_param = 'page'
    page_size_query_param = 'pagesize'

    def get_paginated_response(self, data):
        return Response({
            "counts": self.page.paginator.count,  # 数据总数
            "lists": data,  # 用户数据
            "page": self.page.number,  # 当前页数
            "pages": self.page.paginator.num_pages,  # 总页数
            "pagesize": self.page_size  # 后端默认每页数量
        })
