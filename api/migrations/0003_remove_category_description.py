# Generated by Django 4.1.5 on 2023-01-11 18:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_remove_userprofile_friends_alter_transaction_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='description',
        ),
    ]