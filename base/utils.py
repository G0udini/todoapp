class TickFormsCalc:
    @classmethod
    def _calculate_ticks_done_and_cnt(cls, formset):
        cnt_ticks, done_ticks = 0, 0
        for tick in formset:
            cnt, done = cls._check_tick_exist_and_complete(tick)
            cnt_ticks += cnt
            done_ticks += done
        return cnt_ticks, done_ticks

    @staticmethod
    def _check_tick_exist_and_complete(tick):
        if tick.cleaned_data.get("title"):
            done = tick.cleaned_data.get("completed")
            return True, done
        return False, False

    @classmethod
    def _get_ticks_for_delete_or_save(cls, task, formset):
        deletion = []
        for tick_form in formset:
            if empty_id := cls._check_empty_tick_forms(task, tick_form):
                deletion.append(empty_id)
        return deletion

    @staticmethod
    def _check_empty_tick_forms(task, tick_form):
        if tick_form.cleaned_data.get("title"):
            tick = tick_form.save(commit=False)
            tick.task = task
            tick.save()
        elif tick := tick_form.cleaned_data.get("id"):
            return tick.id
