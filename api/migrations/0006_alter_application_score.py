# Generated by Django 4.2.6 on 2023-10-19 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_application_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='score',
            field=models.CharField(blank=True, editable=False, max_length=255),
        ),
    ]
