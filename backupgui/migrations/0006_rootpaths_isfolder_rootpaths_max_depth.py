# Generated by Django 4.1 on 2022-12-24 22:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backupgui", "0005_logginglevels"),
    ]

    operations = [
        migrations.AddField(
            model_name="rootpaths",
            name="IsFolder",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="rootpaths",
            name="Max_Depth",
            field=models.SmallIntegerField(default=1),
        ),
    ]
