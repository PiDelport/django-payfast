from django import forms
from django.utils.datastructures import SortedDict
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site

from payfast.models import PayFastOrder
from payfast.api import signature, data_is_valid
from payfast import conf

def full_url(link):
    current_site = Site.objects.get_current()
    url = current_site.domain + link
    if not url.startswith('http'):
        url = 'http://' + url
    return url

def notify_url():
    return full_url(reverse('payfast_notify'))

class HiddenForm(forms.Form):
    """ A form with all fields hidden """
    def __init__(self, *args, **kwargs):
        super(HiddenForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget = forms.HiddenInput()

class PayFastForm(HiddenForm):
    """ PayFast helper form.
    It is not for validating data.
    It can be used to output html.

    Pass all the fields to form 'initial' argument. Form also has an optional
    'user' parameter: it is the User instance the order is purchased by. If
    'user' is specified, 'name_first', 'name_last' and 'email_address' fields
    will be filled automatically if they are not passed with 'initial'.
    """

    target = conf.PROCESS_URL

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
        kwargs['initial'].setdefault('merchant_id', conf.MERCHANT_ID)
        kwargs['initial'].setdefault('merchant_key', conf.MERCHANT_KEY)

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
        self._signature = self.fields['signature'].initial = signature(data)


class NotifyForm(forms.ModelForm):

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(NotifyForm, self).__init__(*args, **kwargs)
        # the form must be used with order instance provided
        assert self.instance.pk

    def clean(self):
        self.ip = self.request.META.get(conf.IP_HEADER, None)
        if self.ip not in conf.IP_ADDRESSES:
            raise forms.ValidationError('untrusted ip: %s' % self.ip)

        if conf.USE_POSTBACK:
            is_valid = data_is_valid(self.request.POST, conf.SERVER)
            if is_valid is None:
                raise forms.ValidationError('Postback fails')
            if not is_valid:
                raise forms.ValidationError('Postback validation fails')


        return self.cleaned_data

    def clean_merchant_id(self):
        merchant_id = self.cleaned_data['merchant_id']
        if merchant_id != conf.MERCHANT_ID:
            raise forms.ValidationError('Invalid merchant id (%s).' % merchant_id)
        return merchant_id

    def clean_amount_gross(self):
        received = self.cleaned_data['amount_gross']
        if conf.REQUIRE_AMOUNT_MATCH:
            requested = self.instance.amount_gross
            if requested != received:
                raise forms.ValidationError('Amount is not the same: %s != %s' % (
                                            requested, received,))
        return received

    def clean_signature(self):
        return self.cleaned_data['signature']

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

