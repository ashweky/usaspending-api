# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-08-23 12:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('references', '0028_drop_legalentityofficers'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='toptieragency',
            name='fpds_code',
        ),
    ]
