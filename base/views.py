from multiprocessing import get_context
from django.http import HttpResponseRedirect
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import ProcessFormView
from django.views.generic.edit import DeleteView, CreateView, UpdateView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import JsonRequestResponseMixin

from .mixins import PostTaskMixin
from .models import Task
from base.services import TaskListService, TaskGetObjectService, TaskPostObjectService


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


class TaskObject(LoginRequiredMixin, TemplateView):
    template_name = "base/task_detail.html"
    success_url = reverse_lazy("tasks")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        extra_context = TaskGetObjectService(
            self.request, **kwargs
        ).execute_get_request()
        context.update(extra_context)
        return context

    def post(self, request, *args, **kwargs):
        submit_forms = TaskPostObjectService(
            self.request, **kwargs
        ).execute_post_request()
        if submit_forms:
            redirect_url = str(self.success_url)
            return HttpResponseRedirect(redirect_url)
        return self.render_to_response(self.get_context_data(**kwargs))


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
