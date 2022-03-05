from django.db.models import F
from django.db.models.expressions import Case, When
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView, FormView
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView,
    PasswordChangeDoneView,
    PasswordChangeView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
)
from braces.views import JsonRequestResponseMixin

from .models import Task, TickList
from .forms import MyUserCreationForm, TaskForm, TickListInlineFormSet


class TaskList(LoginRequiredMixin, ListView):
    context_object_name = "tasks"
    paginate_by = 10

    def get_queryset(self):
        tasks = Task.objects.filter(user=self.request.user)

        if search_input := self.request.GET.get("search-area"):
            tasks = tasks.filter(title__icontains=search_input)

        tasks = tasks.annotate(
            tickspers=Case(
                When(number_of_ticks=0, then=0),
                default=F("done_ticks") * 100 / F("number_of_ticks"),
            )
        )
        return tasks

    def paginate_queryset(self, queryset, page_size):
        paginator = self.get_paginator(
            queryset,
            page_size,
            orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty(),
        )
        page_kwarg = self.page_kwarg
        page_number = (
            self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
        )
        page = paginator.get_page(page_number)
        return (paginator, page, page.object_list, page.has_other_pages())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["search_input"] = self.request.GET.get("search-area", "")
        context["page_number"] = context["page_obj"].number
        context["page_limit"] = context["paginator"].num_pages
        context["count"] = self.object_list.filter(complete=False).count()

        return context

    def get_template_names(self):
        if self.request.is_ajax():
            return "base/task_wrapper.html"
        return "base/task_list.html"


class TaskCreateUpdate(LoginRequiredMixin, View):
    template_name = "base/task_form.html"

    def get(self, request, *args, **kwargs):
        task = None
        if kwargs.get("pk"):
            key = kwargs.get("pk")
            task = get_object_or_404(
                Task.objects.prefetch_related("ticklist"), id=key, user=request.user
            )
        context = {
            "ticklist_form": TickListInlineFormSet(instance=task),
            "task_form": TaskForm(instance=task),
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        task_instance = None
        if kwargs.get("pk"):
            task_instance = Task.objects.get(id=kwargs.get("pk"))
        task_form = TaskForm(request.POST, instance=task_instance)
        if task_form.is_valid():
            task = task_form.save(commit=False)
            task.user = request.user
            formset = TickListInlineFormSet(request.POST, instance=task)
            if formset.is_valid():
                self.calculate_ticks_number(task, formset)
                task.save()
                self.check_formset(task, formset)

        return redirect("tasks")

    def calculate_ticks_number(self, task, formset):
        done_ticks, cnt_ticks = 0, 0
        for tick in formset:
            if tick.cleaned_data.get("title"):
                cnt_ticks += 1
                if tick.cleaned_data.get("completed"):
                    done_ticks += 1
        task.done_ticks = done_ticks
        task.number_of_ticks = cnt_ticks

    def check_formset(self, task, formset):
        deletion = []
        for tick_form in formset:
            if tick_form.cleaned_data.get("title"):
                tick = tick_form.save(commit=False)
                tick.task = task
                tick.save()
            elif tick := tick_form.cleaned_data.get("id"):
                deletion.append(tick.id)
        if deletion:
            TickList.objects.filter(id__in=deletion).delete()


class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = "task"
    success_url = reverse_lazy("tasks")


class CustomLogin(LoginView):
    template_name = "base/login.html"
    fields = "__all__"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("tasks")


class RegisterPage(FormView):
    template_name = "base/register.html"
    form_class = MyUserCreationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("tasks")

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("tasks")
        return super().get(*args, **kwargs)


class TaskReorder(JsonRequestResponseMixin, View):
    def post(self, request):
        try:
            position = self.request_json
        except KeyError:
            return self.render_bad_request_response({"status": "Canceled"})

        self.request.user.set_task_order(position)
        return self.render_json_response({"status": "OK"})


class TaskComplete(JsonRequestResponseMixin, View):
    def post(self, request):
        try:
            task_id = self.request_json
        except KeyError:
            return self.render_bad_request_response({"status": "Not saved"})
        task = Task.objects.get(id=task_id)
        task.complete = not task.complete
        task.save()
        return self.render_json_response({"status": "OK"})


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = "registration/password_change.html"
    success_url = reverse_lazy("password-change-done")


class CustomPasswordChangeDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = "registration/pass_change_done.html"


class CustomPasswordResetView(PasswordResetView):
    template_name = "registration/password_reset.html"
    email_template_name = "registration/pass_reset_email.html"
    success_url = reverse_lazy("password-reset-done")


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = "registration/pass_reset_done.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "registration/password_reset_conf.html"
    success_url = reverse_lazy("password-reset-complete")


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "registration/password_reset_compl.html"
