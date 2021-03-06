# Generated by Django 4.0.5 on 2022-07-05 21:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_notification_action_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='message',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='is_read',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='notification',
            name='redirect_url',
            field=models.URLField(blank=True, max_length=255, null=True),
        ),
    ]
