# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('emailuser', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            [("CREATE INDEX emailuser_emailuser_email_upper ON emailuser_emailuser (UPPER(email));", [])],
            [("DROP INDEX emailuser_emailuser_email_upper;", [])]
        )
    ]
