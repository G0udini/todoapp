from django.forms import ModelForm, formset_factory
from .models import TickList, Task


class TickListForm(ModelForm):
    class Meta:
        model = TickList
        fields = ["title", "completed"]


TickListFormSet = formset_factory(TickListForm, extra=1)


class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description"]
        labels = {
            "title": "Задача",
            "description": "Описание",
        }
