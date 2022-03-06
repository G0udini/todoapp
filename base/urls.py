from django.urls import path

from .views import (
    TaskList,
    TaskDetail,
    TaskCreate,
    TaskDelete,
    TaskReorder,
    TaskComplete,
)


urlpatterns = [
    path("", TaskList.as_view(), name="tasks"),
    path("<int:pk>/", TaskDetail.as_view(), name="task-detail"),
    path("create/", TaskCreate.as_view(), name="task-create"),
    path("delete/<int:pk>/", TaskDelete.as_view(), name="task-delete"),
    path("reorder/", TaskReorder.as_view(), name="task-reorder"),
    path("complete/", TaskComplete.as_view(), name="task-complete"),
]
