# Generated by Django 4.0.5 on 2022-07-02 10:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chatroommessagebody',
            options={'verbose_name_plural': 'Chat room message bodies'},
        ),
        migrations.AddField(
            model_name='chatroom',
            name='last_message',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='chat.chatroommessage'),
        ),
    ]
