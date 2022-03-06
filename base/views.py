from django.db.models import F
from django.db.models.expressions import Case, When
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import JsonRequestResponseMixin

from .mixins import PostTaskFormProcessMixin
from .models import Task
from .forms import TaskForm, TickListInlineFormSet


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


class TaskDetail(LoginRequiredMixin, PostTaskFormProcessMixin, DetailView):
    template_name = "base/task_detail.html"

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        return {
            "task_form": TaskForm(instance=self.object),
            "ticklist_form": TickListInlineFormSet(instance=self.object),
            "task": self.object,
        }


class TaskCreate(LoginRequiredMixin, PostTaskFormProcessMixin, CreateView):
    template_name = "base/task_detail.html"

    def get_context_data(self, **kwargs):
        return {
            "task_form": TaskForm(),
            "ticklist_form": TickListInlineFormSet(),
        }


class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = "task"
    success_url = reverse_lazy("tasks")


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
