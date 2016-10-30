# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-30 20:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('references', '0032_merge_20161027_1431'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cfdaprogram',
            name='archived_date',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cfdaprogram',
            name='published_date',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='legalentity',
            unique_together=set([('recipient_name',)]),
        ),
    ]
