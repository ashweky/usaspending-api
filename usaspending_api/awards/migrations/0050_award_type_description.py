# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-01-10 20:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('awards', '0049_auto_20170109_1831'),
    ]

    operations = [
        migrations.AddField(
            model_name='award',
            name='type_description',
            field=models.CharField(default='Unknown Type', max_length=50, null=True, verbose_name='Award Type Description'),
        ),
    ]
