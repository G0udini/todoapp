from django.forms import ModelForm
from django.forms.models import inlineformset_factory

from .models import TickList, Task


class TickListForm(ModelForm):
    class Meta:
        model = TickList
        fields = ["id", "title", "completed"]


TickListInlineFormSet = inlineformset_factory(Task, TickList, TickListForm, extra=1)


class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description"]
        labels = {
            "title": "Задача",
            "description": "Описание",
        }
