from django.urls import path
from . import views

urlpatterns = [
    path("new_item", views.new_item, name="new_item"),
    path("auction", views.auction, name="auction"),
    path("betting", views.betting, name="betting"),
]
