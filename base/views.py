from django.db.models import F, ExpressionWrapper, FloatField
from django.shortcuts import redirect
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from .models import Task
from braces.views import JsonRequestResponseMixin


class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = "tasks"

    def get_context_data(self, **kwargs):
        context = {}
        page_number = self.request.GET.get("page")
        search_input = self.request.GET.get("search-area") or ""
        tasks = Task.objects.filter(user=self.request.user)
        if search_input:
            tasks = tasks.filter(title__icontains=search_input)
            context["search_input"] = search_input

        context["count"] = tasks.filter(complete=False).count()
        tasks = tasks.annotate(
            tickspers=ExpressionWrapper(
                F("done_ticks") * 1.0 / F("number_of_ticks"), output_field=FloatField()
            )
        ).values("id", "title", "complete", "tickspers")
        paginator = Paginator(tasks, 10)
        context["page_limit"] = paginator.num_pages
        try:
            context["tasks"] = paginator.page(page_number)
            context["page_number"] = page_number
        except PageNotAnInteger:
            context["tasks"] = paginator.page(1)
            context["page_number"] = 1
        except EmptyPage:
            context["tasks"] = paginator.page(paginator.num_pages)
            context["page_number"] = paginator.num_pages
        return context

    def get_template_names(self):
        if self.request.is_ajax():
            return "base/task_wrapper.html"
        return "base/task_list.html"


class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ["title", "description", "complete"]
    success_url = reverse_lazy("tasks")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ["title", "description", "complete"]
    success_url = reverse_lazy("tasks")


class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = "task"
    success_url = reverse_lazy("tasks")


class CustromLogin(LoginView):
    template_name = "base/login.html"
    fields = "__all__"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("tasks")


class RegisterPage(FormView):
    template_name = "base/register.html"
    form_class = UserCreationForm
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
