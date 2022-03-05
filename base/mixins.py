from django.shortcuts import redirect

from .forms import TaskForm, TickListInlineFormSet
from .models import TickList


class PostTaskFormProcessMixin:
    def post(self, request, *args, **kwargs):
        self.object = None
        if kwargs.get(self.pk_url_kwarg):
            self.object = self.get_object()
        task_form = TaskForm(request.POST, instance=self.object)

        if task_form.is_valid():
            task = task_form.save(commit=False)
            task.user = request.user
            formset = TickListInlineFormSet(request.POST, instance=task)
            if formset.is_valid():
                self._calculate_ticks_number(task, formset)
                task.save()
                self._check_formset(task, formset, TickList)

        return redirect("tasks")

    def _calculate_ticks_number(self, task, formset):
        done_ticks, cnt_ticks = 0, 0
        for tick in formset:
            if tick.cleaned_data.get("title"):
                cnt_ticks += 1
                if tick.cleaned_data.get("completed"):
                    done_ticks += 1
        task.done_ticks = done_ticks
        task.number_of_ticks = cnt_ticks

    def _check_formset(self, task, formset, model_formset):
        deletion = []
        for tick_form in formset:
            if tick_form.cleaned_data.get("title"):
                tick = tick_form.save(commit=False)
                tick.task = task
                tick.save()
            elif tick := tick_form.cleaned_data.get("id"):
                deletion.append(tick.id)
        if deletion:
            model_formset.objects.filter(id__in=deletion).delete()
