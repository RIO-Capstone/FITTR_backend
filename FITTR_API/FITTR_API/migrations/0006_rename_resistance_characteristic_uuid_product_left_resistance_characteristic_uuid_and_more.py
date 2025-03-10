# Generated by Django 5.1.3 on 2025-02-09 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("FITTR_API", "0005_alter_exercisesession_duration"),
    ]

    operations = [
        migrations.RenameField(
            model_name="product",
            old_name="resistance_characteristic_uuid",
            new_name="left_resistance_characteristic_uuid",
        ),
        migrations.AddField(
            model_name="product",
            name="exercise_initialize_uuid",
            field=models.CharField(
                default="12345678-1234-1234-1234-123456789abc", max_length=50
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="right_resistance_characteristic_uuid",
            field=models.CharField(
                default="87654321-4321-4321-4321-abcdef987654", max_length=50
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="fitness_goal",
            field=models.CharField(default="undecided", max_length=20),
        ),
    ]
