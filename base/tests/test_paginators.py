from django.test import TestCase

from base.models import Task
from base.paginators import TaskPaginator


class PaginatorTest(TestCase):
    fixtures = ["user.json", "base.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.object_list = Task.objects.all()
        cls.task_paginator = TaskPaginator(cls.object_list, per_page=1)

    def test_get_paginated_context(self):
        db_page_limit = PaginatorTest.object_list.count()
        db_page = PaginatorTest.object_list[:1]
        (
            page_limit,
            page_number,
            page,
        ) = PaginatorTest.task_paginator.get_paginated_context(1)

        self.assertEqual(page_limit, db_page_limit)
        self.assertEqual(page_number, 1)
        for task, task_db in zip(page, db_page):
            self.assertEqual(task, task_db)
