# Generated by Django 4.2.6 on 2023-10-31 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0013_alter_user_password'),
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, to='auth.group'),
        ),
    ]