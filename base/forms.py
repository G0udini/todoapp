from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.forms.models import inlineformset_factory

from django.contrib.auth.forms import UserCreationForm
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


class MyUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email")

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "Пользователь с таким email-адресом уже существует."
            )
        return email
