# Generated by Django 4.0.5 on 2022-07-05 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='action_name',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
