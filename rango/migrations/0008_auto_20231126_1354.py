# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2023-11-26 13:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rango', '0007_auto_20231123_1412'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='user_likes',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='liked_categories',
            field=models.ManyToManyField(blank=True, to='rango.Category'),
        ),
    ]
