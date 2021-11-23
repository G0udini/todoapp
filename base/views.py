from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView, FormView
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from .models import Task, TickList
from .forms import TaskForm, TickListInlineFormSet
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
            tickspers=F("done_ticks") * 100 / F("number_of_ticks")
        ).values(
            "id", "title", "complete", "tickspers", "done_ticks", "number_of_ticks"
        )

        paginator = Paginator(tasks, 10)
        context["page_limit"] = paginator.num_pages
        self.validate_page(context, paginator, page_number)
        return context

    def get_template_names(self):
        if self.request.is_ajax():
            return "base/task_wrapper.html"
        return "base/task_list.html"

    def validate_page(self, context, paginator, page_number):
        try:
            context["tasks"] = paginator.page(page_number)
            context["page_number"] = page_number
        except PageNotAnInteger:
            context["tasks"] = paginator.page(1)
            context["page_number"] = 1
        except EmptyPage:
            context["tasks"] = paginator.page(paginator.num_pages)
            context["page_number"] = paginator.num_pages


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
            else:
                tick = tick_form.cleaned_data.get("id")
                if tick:
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
