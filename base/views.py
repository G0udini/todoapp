from django.views import View
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import JsonRequestResponseMixin

from .mixins import PostTaskFormProcessMixin
from .models import Task
from .forms import TaskForm, TickListInlineFormSet
from base.services import TaskListService


class TaskList(LoginRequiredMixin, TemplateView):
    def get_template_names(self):
        if self.request.is_ajax():
            return "base/task_wrapper.html"
        return "base/task_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        extra_context = TaskListService(self.request).execute()
        context.update(extra_context)
        return context


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
