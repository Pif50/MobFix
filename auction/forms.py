from django import forms
from django.forms import DateTimeInput
from django.contrib.auth.forms import UserCreationForm
from .models import Auction


class ItemForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ["object", "description", "image", "close_date", "open_price"]
        widgets = {
            "close_date": DateTimeInput(attrs={"placeholder": "YYYY-MM-DD HH:MM"})
        }
