# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils import timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PayFastOrder',
            fields=[
                ('m_payment_id', models.AutoField(help_text="Unique transaction ID on the receiver's system.", serialize=False, primary_key=True)),
                ('pf_payment_id', models.CharField(help_text='Unique transaction ID on PayFast.', max_length=40, unique=True, null=True, blank=True)),
                ('payment_status', models.CharField(help_text='The status of the payment.', max_length=20, null=True, blank=True)),
                ('item_name', models.CharField(help_text='The name of the item being charged for.', max_length=100)),
                ('item_description', models.CharField(help_text='The description of the item being charged for.', max_length=255, null=True, blank=True)),
                ('amount_gross', models.DecimalField(help_text='The total amount which the payer paid.', null=True, max_digits=15, decimal_places=2, blank=True)),
                ('amount_fee', models.DecimalField(help_text='The total in fees which was deducated from the amount.', null=True, max_digits=15, decimal_places=2, blank=True)),
                ('amount_net', models.DecimalField(help_text="The net amount credited to the receiver's account.", null=True, max_digits=15, decimal_places=2, blank=True)),
                ('custom_str1', models.CharField(max_length=255, null=True, blank=True)),
                ('custom_str2', models.CharField(max_length=255, null=True, blank=True)),
                ('custom_str3', models.CharField(max_length=255, null=True, blank=True)),
                ('custom_str4', models.CharField(max_length=255, null=True, blank=True)),
                ('custom_str5', models.CharField(max_length=255, null=True, blank=True)),
                ('custom_int1', models.IntegerField(null=True, blank=True)),
                ('custom_int2', models.IntegerField(null=True, blank=True)),
                ('custom_int3', models.IntegerField(null=True, blank=True)),
                ('custom_int4', models.IntegerField(null=True, blank=True)),
                ('custom_int5', models.IntegerField(null=True, blank=True)),
                ('name_first', models.CharField(help_text='First name of the payer.', max_length=100, null=True, blank=True)),
                ('name_last', models.CharField(help_text='Last name of the payer.', max_length=100, null=True, blank=True)),
                ('email_address', models.CharField(help_text='Email address of the payer.', max_length=100, null=True, blank=True)),
                ('merchant_id', models.CharField(help_text='The Merchant ID as given by the PayFast system.', max_length=15)),
                ('signature', models.CharField(help_text='A security signature of the transmitted data', max_length=32, null=True, blank=True)),
                ('created_at', models.DateTimeField(default=timezone.now)),
                ('updated_at', models.DateTimeField(default=timezone.now)),
                ('request_ip', models.GenericIPAddressField(null=True, blank=True)),
                ('debug_info', models.CharField(max_length=255, null=True, blank=True)),
                ('trusted', models.NullBooleanField(default=None)),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'PayFast order',
                'verbose_name_plural': 'PayFast orders',
            },
        ),
    ]
