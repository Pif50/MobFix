# Generated by Django 4.1.3 on 2022-12-09 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Auction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("object", models.CharField(max_length=50)),
                ("description", models.CharField(default="", max_length=256)),
                ("image", models.ImageField(blank=True, null=True, upload_to="imgs/")),
                ("open_date", models.DateTimeField(auto_now_add=True)),
                ("close_date", models.DateTimeField()),
                ("total_bet", models.IntegerField(default=0)),
                ("open_price", models.FloatField(default=0)),
                ("close_price", models.FloatField(default=0)),
                ("winner", models.CharField(default="", max_length=256)),
                ("active", models.BooleanField(default=True)),
                ("json_details_file", models.TextField(default="")),
                ("tx", models.CharField(default="", max_length=256)),
            ],
        ),
    ]
