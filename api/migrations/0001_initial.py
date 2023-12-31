# Generated by Django 4.2.6 on 2023-10-31 13:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0013_alter_user_password'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(blank=True, max_length=128, null=True, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.FloatField(blank=True, editable=False, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('accepted', models.PositiveIntegerField(default=0, editable=False)),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('name', models.CharField(blank=True)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('base64_data', models.CharField()),
            ],
        ),
        migrations.CreateModel(
            name='Opportunity',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('select_value', models.PositiveIntegerField(default=0)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('requirements', models.TextField()),
                ('benefits', models.TextField()),
                ('due_date', models.DateField()),
                ('accepted_count', models.PositiveIntegerField(default=0, editable=False)),
                ('status', models.CharField(default='Open', editable=False, max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Applicant',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('phone_number', models.CharField(max_length=255)),
                ('linkedin_profile', models.URLField(max_length=255)),
                ('city', models.CharField(max_length=255)),
                ('state', models.CharField(max_length=255)),
                ('zip_code', models.CharField(max_length=255)),
                ('document', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.document')),
            ],
            bases=('api.user',),
        ),
        migrations.CreateModel(
            name='HR',
            fields=[
                ('user_ptr', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
            bases=('api.user',),
        ),
        migrations.CreateModel(
            name='SortApplication',
            fields=[
                ('application_ptr', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='api.application')),
            ],
            bases=('api.application',),
        ),
        migrations.AddField(
            model_name='application',
            name='opportunity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications_as_opportunity', to='api.opportunity'),
        ),
        migrations.AddField(
            model_name='application',
            name='applicant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications_as_applicant', to='api.applicant'),
        ),
    ]
