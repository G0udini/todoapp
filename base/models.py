from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    complete = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    number_of_ticks = models.IntegerField(blank=True, default=0)
    done_ticks = models.IntegerField(blank=True, default=0)

    def __str__(self):
        return self.title

    class Meta:
        order_with_respect_to = "user"
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"


class TickList(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="ticklist")
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Подзачада"
        verbose_name_plural = "Подзадачи"
