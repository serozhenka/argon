# Generated by Django 4.0.5 on 2022-07-03 11:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0006_alter_chatroom_first_unread_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatroom',
            name='first_unread_message',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='first_unread_message', to='chat.chatroommessage'),
        ),
    ]
