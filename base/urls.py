from django.urls import path
from .views import (
    TaskList,
    TaskCreate,
    TaskUpdate,
    TaskDelete,
    CustromLogin,
    RegisterPage,
    TaskReorder,
    TaskComplete,
)
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("", TaskList.as_view(), name="tasks"),
    path("task-create/", TaskCreate.as_view(), name="task-create"),
    path("task-update/<int:pk>/", TaskUpdate.as_view(), name="task-update"),
    path("task-delete/<int:pk>/", TaskDelete.as_view(), name="task-delete"),
    path("login/", CustromLogin.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
    path("register/", RegisterPage.as_view(), name="register"),
    path("task-reorder/", TaskReorder.as_view(), name="task-reorder"),
    path("task-complete/", TaskComplete.as_view(), name="task-complete"),
]
