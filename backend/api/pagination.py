from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Recipe


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_query_param = 'page'
    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data
        })


'''class RecipePagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_query_param = 'page'
    is_favorited = 'is_favorited'
    is_in_shopping_cart = 'is_in_shopping_cart'
    author = 'author'
    tags = 'tags'
    data = Recipe.objects.filter(is_favorited=is_favorited,
                                 is_in_shopping_cart=is_in_shopping_cart,
                                 author=author,
                                 tags=tags)
    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data
        })'''