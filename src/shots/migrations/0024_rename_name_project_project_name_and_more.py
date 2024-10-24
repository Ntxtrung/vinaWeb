# Generated by Django 5.1.1 on 2024-10-09 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shots', '0023_remove_package_earliest_delivery_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='name',
            new_name='project_name',
        ),
        migrations.RenameField(
            model_name='shot',
            old_name='name',
            new_name='shot_name',
        ),
        migrations.RemoveField(
            model_name='package',
            name='name',
        ),
        migrations.AddField(
            model_name='package',
            name='package_name',
            field=models.CharField(default='Unnamed Package', max_length=255),
        ),
    ]
