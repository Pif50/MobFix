from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=256, default="")
    wallet = models.FloatField(default=1000)
    total_bet = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.object


# Create your models here.
