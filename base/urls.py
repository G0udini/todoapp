from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import (
    TaskList,
    TaskCreateUpdate,
    TaskDelete,
    CustomLogin,
    RegisterPage,
    TaskReorder,
    TaskComplete,
    CustomPasswordChangeView,
    CustomPasswordChangeDoneView,
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView,
)

urlpatterns = [
    path("", TaskList.as_view(), name="tasks"),
    path("task-create/", TaskCreateUpdate.as_view(), name="task-create"),
    path("task-update/<int:pk>/", TaskCreateUpdate.as_view(), name="task-update"),
    path("task-delete/<int:pk>/", TaskDelete.as_view(), name="task-delete"),
    path("login/", CustomLogin.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
    path("register/", RegisterPage.as_view(), name="register"),
    path(
        "password-change/", CustomPasswordChangeView.as_view(), name="password-change"
    ),
    path(
        "password-change-done/",
        CustomPasswordChangeDoneView.as_view(),
        name="password-change-done",
    ),
    path("password-reset/", CustomPasswordResetView.as_view(), name="password-reset"),
    path(
        "password-reset-done/",
        CustomPasswordResetDoneView.as_view(),
        name="password-reset-done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>",
        CustomPasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path(
        "password-reset-complete/",
        CustomPasswordResetCompleteView.as_view(),
        name="password-reset-complete",
    ),
    path("task-reorder/", TaskReorder.as_view(), name="task-reorder"),
    path("task-complete/", TaskComplete.as_view(), name="task-complete"),
]
