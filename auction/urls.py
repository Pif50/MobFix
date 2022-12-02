from django.urls import path
from . import views

urlpatterns = [
    path("asta", views.asta, name="asta"),
    path("item/<int:id>", views.item_view, name="item"),
    path("item/add_watchlist/<int:id>", views.add_watchlist, name="add_watchlist"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("notification", views.notification, name="notification"),
]
