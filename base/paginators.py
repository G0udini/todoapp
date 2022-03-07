from django.core.paginator import Paginator

TASK_LIST_OBJECTS_PER_PAGE = 10


class TaskPaginator(Paginator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, per_page=TASK_LIST_OBJECTS_PER_PAGE, **kwargs)

    def get_paginated_context(self, page_number):
        page = self.get_page(page_number)
        return self.num_pages, page.number, page.object_list
