# Generated by Django 5.0 on 2023-12-11 21:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("flase_app", "0004_user_name"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="name",
        ),
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.IntegerField(
                choices=[(0, "Admin"), (1, "Editor"), (2, "Reader")]
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(max_length=128, unique=True),
        ),
    ]
