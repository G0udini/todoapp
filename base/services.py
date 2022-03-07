from base.crud import TaskQueryset
from base.paginators import TaskPaginator


class TaskListService:
    def __init__(self, request):
        self.user = request.user
        self.search_field = request.GET.get("search-area", "")
        self.page_number = request.GET.get("page", 1)

    def _get_queryset(self):
        return TaskQueryset().get_task_list_queryset(
            user=self.user, search=self.search_field
        )

    def _get_count_tasks(self):
        return TaskQueryset().get_uncompleted_tasks_number(
            user=self.user, search=self.search_field
        )

    def _paginate(self, queryset):
        paginator = TaskPaginator(queryset)
        return paginator.get_paginated_context(self.page_number)

    def _build_context(self, total_pages, page_number, queryset, task_count):
        return {
            "tasks": queryset,
            "search_input": self.search_field,
            "page_number": total_pages,
            "page_limit": page_number,
            "count": task_count,
        }

    def execute(self):
        tasks_queryset = self._get_queryset()
        uncompleted_count = self._get_count_tasks()
        total_pages, page_number, queryset = self._paginate(tasks_queryset)
        return self._build_context(
            total_pages, page_number, queryset, uncompleted_count
        )
