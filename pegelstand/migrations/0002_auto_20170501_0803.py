# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-01 06:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pegelstand', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pegelzeit',
            name='Kommentar',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='pegelzeit',
            name='Notation',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='pegelzeit',
            name='downloadzeitpunkt',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]