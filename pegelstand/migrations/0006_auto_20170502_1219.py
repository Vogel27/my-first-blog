# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-02 10:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pegelstand', '0005_auto_20170502_1035'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pegel_long',
            name='pegel_html_zeitstempel',
            field=models.DateTimeField(blank=True),
        ),
    ]