from datetime import datetime
from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.contrib.auth.models import User

from payfast import readable_models

def full_url(link):
    current_site = Site.objects.get_current()
    url = current_site.domain + link
    if not url.startswith('http'):
        url = 'http://' + url
    return url

def notify_url():
    return full_url(reverse('payfast_notify'))


class PayFastOrder(models.Model):

    # see http://djangosnippets.org/snippets/2180/
    __metaclass__ = readable_models.ModelBase

    # Transaction Details
    m_payment_id = models.AutoField(primary_key=True)
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
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(default=datetime.now)
    request_ip = models.IPAddressField(null=True, blank=True)
    debug_info = models.CharField(max_length=255, null=True, blank=True)
    trusted = models.NullBooleanField(default=None)
    user = models.ForeignKey(User, null=True, blank=True)

    class HelpText:
        m_payment_id = "Unique transaction ID on the receiver's system."
        pf_payment_id = "Unique transaction ID on PayFast."
        payment_status = "The status of the payment."
        item_name = "The name of the item being charged for."
        item_description = "The description of the item being charged for."
        amount_gross = "The total amount which the payer paid."
        amount_fee = "The total in fees which was deducated from the amount."
        amount_net = "The net amount credited to the receiver's account."

        name_first = "First name of the payer."
        name_last = "Last name of the payer."
        email_address = "Email address of the payer."

        merchant_id = "The Merchant ID as given by the PayFast system."
        signature = "A security signature of the transmitted data"

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(PayFastOrder, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'PayFastOrder #%s (%s)' % (self.pk, self.created_at)

    class Meta:
        verbose_name = 'PayFastOrder order'
        verbose_name_plural = 'PayFastOrder orders'
