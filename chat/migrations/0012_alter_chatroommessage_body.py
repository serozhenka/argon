# Generated by Django 4.0.5 on 2022-07-08 11:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0011_alter_chatroom_last_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatroommessage',
            name='body',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='message', to='chat.chatroommessagebody'),
        ),
    ]
