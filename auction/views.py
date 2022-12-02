from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import *


@login_required(login_url="login")
def item_view(request, id):
    item = Auction_item.objects.get(id=id)
    user = request.user
    in_watchlist = False
    all_items = item.watchlist.all()
    for i in all_items:
        if i.owner == user:
            in_watchlist = True
            break

    if request.method == "POST":
        if "bid_btn" in request.POST:
            bid_value = float(request.POST["bid_value"])
            max_bid = item.max_bid
            # filter + first -> returns None
            if bid_value > max_bid:
                item.max_bid = bid_value
                item.winner = request.user
                item.save()
            q = Bid.objects.filter(bidder=user, item=item).first()
            if not q:
                b = Bid(bidder=user, item=item, bid=bid_value)
                b.save()
            else:
                q.bid = bid_value
                q.save()
            text = f"{user.username} placed a bid of {bid_value}$ on item '{item.name}'"
            Notification(
                user=item.owner, text=text, item=item, type="bid", color="blue"
            ).save()

        if "comment_btn" in request.POST:
            text = request.POST["comment"]
            c = Comment(text=text, commented_by=user, item=item)
            c.save()
            text = f"{user.username} commented on item - '{item.name}'"
            Notification(user=item.owner, text=text, item=item, type="comment").save()

        if "active_btn" in request.POST:
            state = request.POST["state"]
            if state == "unactive":
                item.active = False
                item.save()
                if item.max_bid != 0:
                    text = f"You won the auction on item - '{item.name}'"
                    Notification(
                        user=item.winner,
                        text=text,
                        item=item,
                        type="win",
                        color="green",
                    ).save()

    return render(
        request,
        "auction/item.html",
        {
            "item": item,
            "in_watchlist": in_watchlist,
        },
    )


@login_required(login_url="login")
def add_watchlist(request, id):
    item = Auction_item.objects.get(id=id)
    user = request.user
    w = Watchlist.objects.get(owner=user)
    do = request.GET["do"]
    if do == "add":
        w.item.add(item)
        w.save()
    else:
        w.item.remove(item)
    return redirect(item_view, id=id)


@login_required(login_url="login")
def watchlist(request):
    user = request.user
    w_items = user.watchlist.first().item.all().order_by("-id")
    return render(request, "auction/watchlist.html", {"list": w_items})


@login_required(login_url="login")
def notification(request):
    user = request.user
    all = user.notifications.all().order_by("-id")
    n = user.notifications.filter(seen=False)
    for i in n:
        i.seen = True
        i.save()
    return render(request, "auction/notification.html", {"list": all})


def asta(request):
    return render(
        request,
        "auction/asta.html",
        {
            "list": Auction_item.objects.filter(active=True).order_by("-id"),
        },
    )
