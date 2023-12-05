from rest_framework.pagination import PageNumberPagination


class ListPagination(PageNumberPagination):
    """
    Modifying the pagination style
    """
    page_size = 2
    page_query_param = 'page_size'
    max_page_size = 20
