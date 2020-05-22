from django.shortcuts import render


def handle_500_view(request):
    return render(request, "error/500.html", status=500)
