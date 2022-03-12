from django.test import TestCase

from base.models import Task, TickList


class TaskModelTest(TestCase):
    fixtures = ["user.json", "base.json"]

    # Test Task models methods
    def test_task_str_method(self):
        task = Task.objects.get(id=1)
        expected_name = task.title

        self.assertEquals(expected_name, str(task))

    # Test Task models methods
    def test_tick_str_method(self):
        tick = TickList.objects.get(id=1)
        expected_name = tick.title

        self.assertEquals(expected_name, str(tick))
