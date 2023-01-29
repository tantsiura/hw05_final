# Generated by Django 2.2.16 on 2023-01-29 09:15

from django.db import migrations, models
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0009_auto_20230128_1118'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='dont subsctibe ypurself',
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.CheckConstraint(check=models.Q(('author__lt', django.db.models.expressions.F('user')), ('author__gt', django.db.models.expressions.F('user')), _connector='OR'), name='dont subsctibe yself'),
        ),
    ]
