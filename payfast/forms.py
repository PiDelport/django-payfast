from hashlib import md5
from urllib import urlencode
from django import forms
from django.utils.datastructures import SortedDict
from payfast.models import notify_url, PayFastOrder
from payfast.conf import LIVE_URL, SANDBOX_URL, TEST_MODE
from payfast.conf import MERCHANT_ID, MERCHANT_KEY, IP_HEADER, IP_ADDRESSES

def signature_string(data):
    values = [(k, unicode(data[k]).encode('utf8'),) for k in data if data[k]]
    return urlencode(values)

def siganture(fields):
    text = signature_string(fields)
    return md5(text).hexdigest()

class HiddenForm(forms.Form):
    """ A form with all fields hidden """
    def __init__(self, *args, **kwargs):
        super(HiddenForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget = forms.HiddenInput()

class PayFastForm(HiddenForm):
    """ PayFast helper form.
    It is not for validating data.
    It can be used to output html. """

    target = LIVE_URL if TEST_MODE else SANDBOX_URL

    # Receiver Details
    merchant_id = forms.CharField()
    merchant_key = forms.CharField()

    return_url = forms.URLField()
    cancel_url = forms.URLField()
    notify_url = forms.URLField()

    # Payer Details
    name_first = forms.CharField()
    name_last = forms.CharField()
    email_address = forms.CharField()

    # Transaction Details
    m_payment_id = forms.CharField()
    amount = forms.CharField()
    item_name = forms.CharField()
    item_description = forms.CharField()

    custom_str1 = forms.CharField()
    custom_str2 = forms.CharField()
    custom_str3 = forms.CharField()
    custom_str4 = forms.CharField()
    custom_str5 = forms.CharField()

    custom_int1 = forms.IntegerField()
    custom_int2 = forms.IntegerField()
    custom_int3 = forms.IntegerField()
    custom_int4 = forms.IntegerField()
    custom_int5 = forms.IntegerField()

    # Transaction Options
    email_confirmation = forms.IntegerField()
    confirmation_address = forms.CharField()

    # Security
    signature = forms.CharField()

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        if user:
            kwargs['initial'].setdefault('name_first', user.first_name)
            kwargs['initial'].setdefault('name_last', user.last_name)
            kwargs['initial'].setdefault('email_address', user.email)

        kwargs['initial'].setdefault('notify_url', notify_url())
        kwargs['initial'].setdefault('merchant_id', MERCHANT_ID)
        kwargs['initial'].setdefault('merchant_key', MERCHANT_KEY)

        super(PayFastForm, self).__init__(*args, **kwargs)

        # new order reference number is issued each time form is instantiated
        self.order = PayFastOrder.objects.create(
            user=user,
            amount_gross = self.initial['amount'],
        )

        self.initial['m_payment_id'] = self.order.pk

        # we need self.initial but it is unordered
        data = SortedDict()
        for key in self.fields.keys():
            data[key] = self.initial.get(key, None)
        self.fields['signature'].initial = siganture(data)


class NotifyForm(forms.ModelForm):

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(NotifyForm, self).__init__(*args, **kwargs)

    def clean(self):
        self.ip = self.request.META.get(IP_HEADER, None)
        if self.ip not in IP_ADDRESSES:
            raise forms.ValidationError('untrusted ip: %s' % self.ip)
        return self.cleaned_data

    def save(self, *args, **kwargs):
        self.instance.request_ip = self.ip
        self.instance.debug_info = self.request.raw_post_data
        self.instance.trusted = True
        return super(NotifyForm, self).save(*args, **kwargs)

    def plain_errors(self):
        ''' plain error list (without the html) '''
        return '|'.join(["%s: %s" % (k, (v[0])) for k, v in self.errors.items()])

    class Meta:
        model = PayFastOrder
        exclude = ['created_at', 'updated_at', 'request_ip', 'debug_info',
                   'trusted', 'user']

