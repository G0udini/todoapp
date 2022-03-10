from django.http import HttpResponseRedirect
from django.views import View
from braces.views import JsonRequestResponseMixin
from django.views.generic import TemplateView
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from base.models import Task
from base.services import (
    TaskListService,
    TaskGetObjectService,
    TaskPostObjectService,
    TaskReorderService,
    TaskCompleteService,
)


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
    def post(self, request, *args, **kwargs):
        context = TaskReorderService(self).execute_task_reorder()
        if context["status"] == "200":
            return self.render_json_response(context)
        return self.render_bad_request_response(context)


class TaskComplete(JsonRequestResponseMixin, View):
    def post(self, request, *args, **kwargs):
        context = TaskCompleteService(self).execute_task_complete()
        if context["status"] == "200":
            return self.render_json_response(context)
        return self.render_bad_request_response(context)
