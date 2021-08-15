from django.urls import path
from .views import TaskDetail, TaskList, DetailView, current_datetime

urlpatterns = [
    path("time/", current_datetime, namae="current_time"),
    # path("", TaskList.as_view(), name="tasks"),
    path("task/<int:pk>/", TaskDetail.as_view(), name="task"),
]
