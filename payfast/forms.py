from hashlib import md5
from django import forms
from payfast.conf import LIVE_URL, SANDBOX_URL, TEST_MODE, MERCHANT_ID, MERCHANT_KEY
from payfast.models import notify_url, PayFastOrder

def signature_string(fields, value_getter=None):
    def _val(field_name):
        return fields[field_name].initial
    _val = value_getter or _val
    return "&".join(["%s=%s" % (name, _val(name),) for name in fields if _val(name)])

def siganture(fields):
    return md5(signature_string(fields)).hexdigest()

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
    merchant_id = forms.CharField(initial = MERCHANT_ID)
    merchant_key = forms.CharField(initial = MERCHANT_KEY)

    return_url = forms.URLField(verify_exists=False, required=False)
    cancel_url = forms.URLField(verify_exists=False, required=False)
    notify_url = forms.CharField(initial = notify_url())

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

        super(PayFastForm, self).__init__(*args, **kwargs)

        # new order reference number is issued each time form is instantiated
        self.order = PayFastOrder.objects.create(user=user)
        self.fields['m_payment_id'].initial = self.order.pk
        self.fields['signature'].initial = siganture(self.fields)


class NotifyForm(forms.ModelForm):

    def plain_errors(self):
        ''' plain error list (without the html) '''
        return '|'.join(["%s: %s" % (k, (v[0])) for k, v in self.errors.items()])

    class Meta:
        model = PayFastOrder
        exclude = ['created_at', 'updated_at', 'request_ip', 'debug_info',
                   'trusted', 'user']
