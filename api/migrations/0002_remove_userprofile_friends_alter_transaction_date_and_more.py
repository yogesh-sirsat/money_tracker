# Generated by Django 4.1.5 on 2023-01-11 06:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='friends',
        ),
        migrations.AlterField(
            model_name='transaction',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='transactionpaid',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.CreateModel(
            name='Friendship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('accepted', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accepted_friendship', to=settings.AUTH_USER_MODEL)),
                ('requested', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requested_friendship', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('requested', 'accepted')},
            },
        ),
    ]