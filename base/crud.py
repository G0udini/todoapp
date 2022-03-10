from base.models import Task, TickList
from django.db.models import F
from django.db.models.expressions import Case, When


class TaskQueryset:
    def __init__(self):
        self.queryset = Task.objects.all()

    def get_uncompleted_tasks_number(self, user, search):
        self._get_filtered_user_tasks(user, search)
        self._count_uncompleted_tasks()
        return self.queryset

    def get_task_list_queryset(self, user, search):
        self._get_filtered_user_tasks(user, search)
        self._annotate_queryset_with_ticks()
        return self.queryset

    def get_task_object(self, user, pk):
        self._get_all_user_tasks(user)
        self._get_task_by_pk(pk)
        return self.queryset

    def change_task_complete(self, user, pk):
        self.get_task_object(user, pk)
        self.queryset.complete = not self.queryset.complete
        self.queryset.save()

    def _get_task_by_pk(self, pk):
        self.queryset = self.queryset.get(pk=pk)

    def _get_all_user_tasks(self, user):
        self.queryset = self.queryset.filter(user=user)

    def _annotate_queryset_with_ticks(self):
        self.queryset = self.queryset.annotate(
            tickspers=Case(
                When(number_of_ticks=0, then=0),
                default=F("done_ticks") * 100 / F("number_of_ticks"),
            )
        )

    def _get_search_filter_queryset(self, search):
        self.queryset = self.queryset.filter(title__icontains=search)

    def _count_uncompleted_tasks(self):
        self.queryset = self.queryset.filter(complete=False).count()

    def _get_filtered_user_tasks(self, user, search):
        self._get_all_user_tasks(user)
        if search:
            self._get_search_filter_queryset(search)


class TickQueryset:
    @staticmethod
    def bulk_delete_empty_ticks(deletion_array):
        TickList.objects.filter(id__in=deletion_array).delete()


class UserQueryset:
    @staticmethod
    def set_new_task_order(user, position):
        user.set_task_order(position)
