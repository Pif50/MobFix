from django.shortcuts import render, redirect
from .models import *
from .forms import *
from .utils import *
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


@login_required(login_url="login")
def auction(request):
    if request.user.is_superuser:
        messages.error(
            request, "super user can access to admin/ and new_auction page only"
        )
        return redirect("new_auction")
    auction = Auction.objects.filter(active=True)
    for data in auction:
        check = check_data(data.close_date)  # primo check data fine asta
        if check is False:
            data.active = False
            data.save()
            check_winner(
                request, data.id
            )  # funzione per aggiudicare il vincitore, creare il fileJson con i dettagli
            # dell'asta conclusa ed invia l'hash del file Jsone in una transazione sulla blockchain
    check_prof = check_profile(
        request
    )  # se il profilo utente ha il saldo negativo viene reindirizzato alla pagina
    # personale invitando di effettuare il pagamento
    if check_prof is True:
        return redirect("profile")
    auctions_open = Auction.objects.filter(active=True)
    if request.method == "POST":
        form = request.POST
        auct_ids = form["auct_id"]
        auct_id = int(auct_ids)
        request.session["selected_id"] = auct_id
        return redirect("betting")
    else:
        return render(request, "auction.html", {"auction": auctions_open})
