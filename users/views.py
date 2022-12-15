from django.contrib.auth import authenticate, login
from django.shortcuts import HttpResponseRedirect, render
from .models import Profile

from users.forms import FormRegistrazione


def registrazione_view(request):
    if request.method == "POST":
        form = FormRegistrazione(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get("username")
            new_prof = Profile.objects.create(user=user, username=user.username)
            new_prof.save()
            login(request, user)
            return HttpResponseRedirect("/")
    else:
        form = FormRegistrazione()
    context = {"form": form}
    return render(request, "users/registrazione.html", context)
