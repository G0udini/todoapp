from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import Task
from django.http import HttpResponse
import datetime


class TaskList(ListView):
    model = Task
    context_object_name = "tasks"


class TaskDetail(DetailView):
    model = Task
    context_object_name = "task"
    template_name = "base/task.html"


def current_datetime(request):
    now = datetime.datetime.now()
    some_value = "there must be sone info"
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)
