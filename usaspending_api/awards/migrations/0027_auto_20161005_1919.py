# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-05 19:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('awards', '0026_auto_20161005_0933'),
    ]

    operations = [
        migrations.AlterField(
            model_name='financialaccountsbyawards',
            name='object_class',
            field=models.ForeignKey(db_column='object_class', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='references.RefObjectClassCode'),
        ),
    ]
