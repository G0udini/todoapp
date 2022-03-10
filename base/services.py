from base.crud import TaskQueryset, TickQueryset, UserQueryset
from base.forms import TaskForm, TickListInlineFormSet
from base.paginators import TaskPaginator
from base.utils import TickFormsCalc


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
            "page_limit": total_pages,
            "page_number": page_number,
            "count": task_count,
        }

    def execute(self):
        tasks_queryset = self._get_queryset()
        uncompleted_count = self._get_count_tasks()
        total_pages, page_number, queryset = self._paginate(tasks_queryset)
        return self._build_context(
            total_pages, page_number, queryset, uncompleted_count
        )


class TaskQueryObjectService:
    def __init__(self, request, **kwargs):
        self.user = request.user
        self.pk = kwargs.get("pk")

    def _get_object(self):
        return TaskQueryset().get_task_object(user=self.user, pk=self.pk)

    def _get_object_or_none(self):
        return self._get_object() if self.pk else None


class TaskGetObjectService:
    def __init__(self, request, **kwargs):
        self.object_query = TaskQueryObjectService(request, **kwargs)

    def _build_base_context(self, object):
        return {
            "task_form": TaskForm(instance=object),
            "ticklist_form": TickListInlineFormSet(instance=object),
        }

    def _add_object_to_context(self, object):
        return {"task": object} if object else {}

    def _build_context(self, object):
        context = self._build_base_context(object)
        extra_context = self._add_object_to_context(object)
        context.update(extra_context)
        return context

    def execute_get_request(self):
        object = self.object_query._get_object_or_none()
        return self._build_context(object)


class TaskPostObjectService:
    def __init__(self, request, *args, **kwargs):
        self.request_data = request.POST
        self.user = request.user
        self.object_query = TaskQueryObjectService(request, *args, **kwargs)

    def _process_task_form(self, object):
        task_form = TaskForm(self.request_data, instance=object)
        if task_form.is_valid():
            self.task = task_form.save(commit=False)
            self.task.user = self.user
            return self._process_ticklist_form()

    def _process_ticklist_form(self):
        formset = TickListInlineFormSet(self.request_data, instance=self.task)
        if formset.is_valid():
            self._validate_ticks_number(formset)
            self.task.save()
            self._check_formset(formset)
            return True

    def _validate_ticks_number(self, formset):
        cnt_ticks, done_ticks = TickFormsCalc._calculate_ticks_done_and_cnt(formset)
        self.task.number_of_ticks = cnt_ticks
        self.task.done_ticks = done_ticks

    def _check_formset(self, formset):
        if deletion := TickFormsCalc._get_ticks_for_delete_or_save(self.task, formset):
            TickQueryset.bulk_delete_empty_ticks(deletion)

    def execute_post_request(self):
        object = self.object_query._get_object_or_none()
        return self._process_task_form(object)


class JSONProcessService:
    def __init__(self, request_object):
        self.user = request_object.request.user
        self.data = request_object.get_request_json()

    def build_400_context(self):
        return {
            "status": "400",
            "massage": "Bad Request",
            "detail": "Request not processed",
        }

    def build_200_context(self):
        return {
            "status": "200",
            "massage": "OK",
            "detail": "Success",
        }


class TaskReorderService:
    def __init__(self, request_object):
        self.object = JSONProcessService(request_object)

    def execute_task_reorder(self):
        if not self.object.data:
            return self.object.build_400_context()
        UserQueryset.set_new_task_order(self.object.user, self.object.data)
        return self.object.build_200_context()


class TaskCompleteService:
    def __init__(self, request_object):
        self.object = JSONProcessService(request_object)

    def execute_task_complete(self):
        if not self.object.data:
            return self.object.build_400_context()
        TaskQueryset().change_task_complete(self.object.user, self.object.data)
        return self.object.build_200_context()
