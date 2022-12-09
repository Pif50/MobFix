from django.shortcuts import render, redirect
from .models import Auction
from .forms import *
from .utils import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required


@login_required(login_url="login")
def new_item(request):

    """
    A function that will create a new item for te auction
    """

    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Item create")
            return redirect("homepage")
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
        return render(request, "auction/auction.html", {"auction": auctions_open})


@login_required(login_url="login")
def betting(request):
    if request.user.is_superuser:
        messages.error(
            request, "super user can access to admin/ and new_auction page only"
        )
        return redirect("new_auction")
    id_ = request.session.get("selected_id")
    auction = Auction.objects.filter(id=id_)
    last_bets = last_bet(id_)
    last_users = last_user(id_)
    last_dates = last_date(id_)
    check = check_data(
        auction[0].close_date
    )  # secondo check per la data di chiusura dell'asta
    all_bets = len_bets(id_)
    if check is True:
        if request.method == "POST":
            user = request.user
            form = request.POST
            prof_user = User.objects.get(pk=request.user.pk)
            bet_price = form["bet"]
            if all_bets < 1:  # se non ci sono ancora scommesse effettuate,
                # l'importo dovra essere maggiore dell'open price scelto alla creazione dell'asta
                if float(bet_price) >= auction[0].open_price:
                    now = datetime.now()
                    add_data_redis(
                        auction[0].id,
                        bet_price,
                        datetime.strftime(now, "%m/%d/%Y, %H:%M:%S"),
                        user,
                    )
                    prof_user.total_bet += 1
                    prof_user.save()
                    messages.success(request, "Confermed!")
                    return redirect("betting")
                else:
                    messages.error(request, "Bet lower than open price")
                    return redirect("betting")
            else:
                last_price = float(last_bets)
                if float(bet_price) > last_price:
                    now = datetime.now()
                    add_data_redis(
                        auction[0].id,
                        bet_price,
                        datetime.strftime(now, "%m/%d/%Y, %H:%M:%S"),
                        user,
                    )
                    prof_user.total_bet += 1
                    prof_user.save()
                    messages.success(request, "Confermed!")
                else:
                    messages.error(request, "Import is lower than last bet")
                return redirect("betting")
        return render(
            request,
            "auction/betting.html",
            {
                "auction": auction,
                "bets": last_bets,
                "users": last_users,
                "date": last_dates,
                "tot_bets": all_bets,
            },
        )
    messages.error(request, "Aucttion is closed!")
    return redirect("home")


@login_required(login_url="login")
def info_profile(request):
    if request.user.is_superuser:
        messages.error(
            request, "super user can access to admin/ and new_auction page only"
        )
        return redirect("new_auction")
    profile = User.objects.get(pk=request.user.pk)
    return render(request, "auction/profile.html", {"profile": profile})
