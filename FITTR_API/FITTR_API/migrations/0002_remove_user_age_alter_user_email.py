# Generated by Django 5.1.3 on 2024-12-16 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("FITTR_API", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="age",
        ),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
