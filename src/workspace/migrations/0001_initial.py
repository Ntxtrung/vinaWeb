# Generated by Django 5.1.1 on 2024-09-23 13:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shots', '0014_alter_shot_annotations'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Workspace',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('#0', 'working'), ('#1', 'done'), ('#2', 'help'), ('#3', 'feedback'), ('#4', 'hold'), ('#5', 'cancelled')], max_length=20)),
                ('work_start_date', models.DateTimeField(blank=True, null=True)),
                ('work_end_date', models.DateTimeField(blank=True, null=True)),
                ('working_time', models.DurationField(blank=True, null=True)),
                ('is_closed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('artist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('shot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shots.shot')),
            ],
        ),
    ]
