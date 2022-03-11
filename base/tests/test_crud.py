from django.test import TestCase
from django.contrib.auth.models import User
from base.crud import TaskQueryset, TickQueryset, UserQueryset
from base.models import Task, TickList


class CrudModelTest(TestCase):
    fixtures = ["user.json", "base.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.get(id=1)
        # self.client.force_login(user=cls.user)

    def setUp(self):
        self.task_queryset = TaskQueryset()

    # Test TaskQueryset methods
    def test_get_task_by_pk(self):
        self.task_queryset._get_task_by_pk(1)
        task = self.task_queryset.queryset
        task_form_db = Task.objects.get(pk=1)
        self.assertEqual(task, task_form_db)

    def test_all_user_tasks(self):
        self.task_queryset._get_all_user_tasks(CrudModelTest.user)
        tasks = self.task_queryset.queryset
        for task in tasks:
            self.assertEqual(task.user, CrudModelTest.user)

    def test_annotate_queryset_with_ticks(self):
        self.task_queryset._annotate_queryset_with_ticks()
        annotated_tasks = self.task_queryset.queryset
        for task in annotated_tasks:
            if task.number_of_ticks:
                custom_tickspers = task.done_ticks * 100 // task.number_of_ticks
                self.assertEqual(task.tickspers, custom_tickspers)
            else:
                self.assertEqual(task.tickspers, 0)

    def test_get_search_filter_queryset(self):
        self.task_queryset._get_search_filter_queryset("first")
        searched_tasks = self.task_queryset.queryset
        for task in searched_tasks:
            self.assertEqual(task.title.lower(), "first")

    def test_count_uncompleted_tasks(self):
        self.task_queryset._count_uncompleted_tasks()
        cnt_uncompleted_tasks = self.task_queryset.queryset
        cnt_db_tasks = Task.objects.filter(complete=False).count()
        self.assertEqual(cnt_uncompleted_tasks, cnt_db_tasks)

    def test_uncompleted_tasks_number_with_filter(self):
        cnt_uncompleted_tasts = self.task_queryset.get_uncompleted_tasks_number(
            CrudModelTest.user, "first"
        )
        cnt_db_tasks_with_filter = Task.objects.filter(
            complete=False, title__icontains="first"
        ).count()
        self.assertEqual(cnt_uncompleted_tasts, cnt_db_tasks_with_filter)

    def test_get_task_list_queryset(self):
        task_list = self.task_queryset.get_task_list_queryset(
            CrudModelTest.user, "first"
        )
        for task in task_list:
            self.assertEqual(task.title.lower(), "first")
            self.assertEqual(task.user, CrudModelTest.user)

    def test_get_task_object(self):
        task = self.task_queryset.get_task_object(CrudModelTest.user, 1)
        self.assertEqual(task.user, CrudModelTest.user)
        self.assertEqual(task.pk, 1)

    def test_change_task_complete(self):
        task_before = Task.objects.get(user=CrudModelTest.user, pk=1)
        self.task_queryset.change_task_complete(CrudModelTest.user, 1)
        task_after = Task.objects.get(user=CrudModelTest.user, pk=1)
        self.assertNotEqual(task_before.complete, task_after.complete)

    # Test TickQueryset methods
    def test_tick_queryset_bulk_delete_empty_ticks(self):
        ticks_queryset_before = TickList.objects.count()
        TickQueryset.bulk_delete_empty_ticks([1, 2, 3, 4, 5])
        ticks_queryset_after = TickList.objects.count()
        self.assertNotEqual(ticks_queryset_before, ticks_queryset_after)

    # Test UserQueryset methods
    def test_user_queryset_set_new_task_order(self):
        tasks_order_before = list(CrudModelTest.user.get_task_order())
        UserQueryset.set_new_task_order(CrudModelTest.user, [2, 3, 4, 5, 1])
        tasks_order_after = list(CrudModelTest.user.get_task_order())
        for task_before, task_after in zip(tasks_order_before, tasks_order_after):
            self.assertNotEqual(task_before, task_after)
