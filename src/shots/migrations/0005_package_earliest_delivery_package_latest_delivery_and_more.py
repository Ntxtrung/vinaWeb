# Generated by Django 5.1.1 on 2024-09-20 07:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shots', '0004_alter_package_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='earliest_delivery',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='package',
            name='latest_delivery',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='shot',
            name='delivery_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='package',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='packages', to='shots.project'),
        ),
    ]
