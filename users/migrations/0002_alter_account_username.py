# Generated by Django 4.0.5 on 2022-06-15 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='username',
            field=models.CharField(db_index=True, max_length=64, unique=True),
        ),
    ]
