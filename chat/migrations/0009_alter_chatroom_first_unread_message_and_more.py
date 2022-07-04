# Generated by Django 4.0.5 on 2022-07-03 19:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0008_alter_chatroommessage_is_read'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatroom',
            name='first_unread_message',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='first_unread_message', to='chat.chatroommessage'),
        ),
        migrations.AlterField(
            model_name='chatroom',
            name='last_message',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='last_message', to='chat.chatroommessage'),
        ),
    ]
