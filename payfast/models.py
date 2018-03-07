from __future__ import unicode_literals

import six
from django.db import models
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible

from payfast import readable_models


@python_2_unicode_compatible
# see http://djangosnippets.org/snippets/2180/
class PayFastOrder(six.with_metaclass(readable_models.ModelBase, models.Model)):

    # Transaction Details
    m_payment_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    pf_payment_id = models.CharField(max_length=40, unique=True, null=True, blank=True)
    payment_status = models.CharField(max_length=20, null=True, blank=True)
    item_name = models.CharField(max_length=100)
    item_description = models.CharField(max_length=255, null=True, blank=True)
    amount_gross = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    amount_fee = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    amount_net = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    # The series of 5 custom string variables (custom_str1, custom_str2...)
    # originally passed by the receiver during the payment request.
    custom_str1 = models.CharField(max_length=255, null=True, blank=True)
    custom_str2 = models.CharField(max_length=255, null=True, blank=True)
    custom_str3 = models.CharField(max_length=255, null=True, blank=True)
    custom_str4 = models.CharField(max_length=255, null=True, blank=True)
    custom_str5 = models.CharField(max_length=255, null=True, blank=True)

    # The series of 5 custom integer variables (custom_int1, custom_int2...)
    # originally passed by the receiver during the payment request.
    custom_int1 = models.IntegerField(null=True, blank=True)
    custom_int2 = models.IntegerField(null=True, blank=True)
    custom_int3 = models.IntegerField(null=True, blank=True)
    custom_int4 = models.IntegerField(null=True, blank=True)
    custom_int5 = models.IntegerField(null=True, blank=True)

    # Payer Information
    name_first = models.CharField(max_length=100, null=True, blank=True)
    name_last = models.CharField(max_length=100, null=True, blank=True)
    email_address = models.CharField(max_length=100, null=True, blank=True)

    # Receiver Information
    merchant_id = models.CharField(max_length=15)

    # Security Information
    signature = models.CharField(max_length=32, null=True, blank=True)

    # Utility fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    request_ip = models.GenericIPAddressField(null=True, blank=True)
    debug_info = models.CharField(max_length=255, null=True, blank=True)
    trusted = models.NullBooleanField(default=None)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             on_delete=models.CASCADE)

    class HelpText:
        m_payment_id = "Unique transaction ID on the receiver's system."
        pf_payment_id = "Unique transaction ID on PayFast."
        payment_status = "The status of the payment."
        item_name = "The name of the item being charged for."
        item_description = "The description of the item being charged for."
        amount_gross = "The total amount which the payer paid."
        amount_fee = "The total in fees which was deducted from the amount."
        amount_net = "The net amount credited to the receiver's account."

        name_first = "First name of the payer."
        name_last = "Last name of the payer."
        email_address = "Email address of the payer."

        merchant_id = "The Merchant ID as given by the PayFast system."
        signature = "A security signature of the transmitted data"

    def __str__(self):
        return 'PayFastOrder {id} ({created_at})'.format(
            # Transitional code: Show the pk if m_payment_id is missing.
            id=('pk={}'.format(self.pk) if self.m_payment_id is None else
                self.m_payment_id),
            created_at=self.created_at,
        )

    class Meta:
        verbose_name = 'PayFast order'
