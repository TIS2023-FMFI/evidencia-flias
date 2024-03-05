# Generated by Django 4.2.10 on 2024-03-05 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flase_app', '0016_cylinderlife_manometer_max_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cylinderlife',
            name='is_latest',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.RunSQL("UPDATE flase_app_cylinderlife SET is_latest = 1 WHERE is_current = 1;"),
    ]
