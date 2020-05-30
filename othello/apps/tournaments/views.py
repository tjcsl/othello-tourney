from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from .forms import TournamentForm
from .models import Tournament


class TournamentListView(ListView):
    model = Tournament
    template_name = "tournaments/previous.html"
    paginate_by = 10
    ordering = ["-start_time"]

    def get_queryset(self):
        return Tournament.objects.finished().order_by(*self.ordering)


class TournamentCreateView(FormView):
    form_class, template_name = TournamentForm, "tournaments/create.html"
    success_url = reverse_lazy("tournaments:management")

    def form_valid(self, form):
        t = form.save()
        messages.success(
            self.request,
            f"Successfully created tournament! Tournament is scheduled to run at {t.start_time}",
            extra_tags="success",
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        for errors in form.errors.get_json_data().values():
            for error in errors:
                messages.error(self.request, error["message"], extra_tags="danger")
        return super().form_invalid(form)


def detail(request, tournament_id=None):
    if tournament_id:
        return HttpResponse(get_object_or_404(Tournament, id=tournament_id))
    return HttpResponse("current")
