from django.shortcuts import render, redirect
from .models import *
from .forms import *

# from .utils import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required


@login_required(login_url="login")
def new_item(request):
    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Item create"
            )  # nuova asta creata con i parametri scelti
            return redirect("new_item")
    else:
        form = ItemForm()
    return render(request, "auction/new_item.html", {"form": form})
