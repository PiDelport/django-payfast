"""
This module can be used without django
"""
from __future__ import unicode_literals

import sys
from typing import Mapping, Tuple, Sequence  # noqa: F401

from hashlib import md5

# Python 2 compatibility:
from six import text_type as str
from six.moves.urllib.error import HTTPError
from six.moves.urllib.parse import urlencode
from six.moves.urllib.request import urlopen

from django.conf import settings


POSTBACK_URL = '/eng/query/validate'
POSTBACK_SERVER = 'https://www.payfast.co.za'


#: Field order for checkout process submission signatures.
#: See: https://developers.payfast.co.za/documentation/#checkout-page
checkout_signature_field_order = [

    # Merchant Details
    'merchant_id',
    'merchant_key',
    'return_url',
    'cancel_url',
    'notify_url',

    # Buyer Detail
    'name_first',
    'name_last',
    'email_address',
    'cell_number',

    # Transaction Details
    'm_payment_id',
    'amount',
    'item_name',
    'item_description',
    'custom_int1',
    'custom_int2',
    'custom_int3',
    'custom_int4',
    'custom_int5',
    'custom_str1',
    'custom_str2',
    'custom_str3',
    'custom_str4',
    'custom_str5',

    # Transaction Options
    'email_confirmation',
    'confirmation_address',

    # Set Payment Method
    'payment_method',

    # Recurring Billing Details
    'subscription_type',
    'billing_date',
    'recurring_amount',
    'frequency',
    'cycles',

]


#: Field order for ITN submission signatures.
#: https://developers.payfast.co.za/documentation/#notify-page-itn
itn_signature_field_order = [

    # Transaction details
    'm_payment_id',
    'pf_payment_id',
    'payment_status',
    'item_name',
    'item_description',
    'amount_gross',
    'amount_fee',
    'amount_net',
    'custom_str1',
    'custom_str2',
    'custom_str3',
    'custom_str4',
    'custom_str5',
    'custom_int1',
    'custom_int2',
    'custom_int3',
    'custom_int4',
    'custom_int5',

    # Buyer details
    'name_first',
    'name_last',
    'email_address',

    # Merchant details
    'merchant_id',

    # Recurring billing details
    'token',

]


#: A sequence of ordered (key, value) variables that can be signed for PayFast.
SignableFields = Sequence[Tuple[str, str]]


def _prepare_signable_fields(
        valid_field_order,  # type: Sequence[str]
        data_fields,  # type: Mapping[str, str]
):  # type: (...) -> SignableFields
    """
    Prepare PayFast submission variables for signing, using the given field order.

    :raise ValueError:
        If `data_fields` contains any unexpected field names not in `valid_field_order`.
    """
    present_fields = (set(data_fields.keys()) if sys.version_info < (3,) else
                      data_fields.keys())
    extra_fields = present_fields - set(valid_field_order)
    if extra_fields:
        raise ValueError('Data contains unexpected fields: {!r}'.format(extra_fields))

    return [
        (name, data_fields[name]) for name in valid_field_order
        if name in data_fields
    ]


def _drop_non_signature_fields(
        data_fields,  # type: Mapping[str, str]
        include_empty,  # type: bool
):  # type: (...) -> Mapping[str, str]
    """
    Drop fields that should not be included in signatures.

    These are:

        * `signature`, as a convenience for verifying already-signed data.
        * Fields with empty values, if `include_empty` is false.

    """
    return {
        k: v for (k, v) in data_fields.items()
        if k != 'signature'
        if include_empty or v
    }


def _sign_fields(signable_fields):  # type: (SignableFields) -> str
    """
    Common signing code.
    """
    for (k, v) in signable_fields:
        assert isinstance(k, str), repr(k)
        assert isinstance(v, str), repr(v)

    if sys.version_info < (3,):
        # Python 2 doesn't do IRI encoding.
        text = urlencode([
            (k.encode('utf-8'), v.encode('utf-8'))
            for (k, v) in signable_fields
        ])
    else:
        text = urlencode(signable_fields, encoding='utf-8', errors='strict')

    return md5(text.encode('ascii')).hexdigest()


#: The checkout signature should ignore these leading and trailing whitespace characters.
#:
#: This list is an educated guess based on the PHP trim() function.
#:
CHECKOUT_SIGNATURE_IGNORED_WHITESPACE = ''.join([
    ' ',
    '\t',
    '\n',
    '\r',
    '\x0b',  # \N{LINE TABULATION} (Python 2 does not know this Unicode character name)

    # XXX: trim() strips '\0', but it's not clear whether to actually strip it here.
    # We can't really test it, since the endpoint seems to refuse any requests with null values.
    # '\0',
])


def checkout_signature(checkout_data):  # type: (Mapping[str, str]) -> str
    """
    Calculate the signature of a checkout process submission.
    """
    # Omits fields with empty values.
    included_fields = _drop_non_signature_fields(checkout_data, include_empty=False)
    # Strip ignored whitespace from values.
    stripped_fields = {
        name: value.strip(CHECKOUT_SIGNATURE_IGNORED_WHITESPACE)
        for (name, value) in included_fields.items()
    }

    signable_fields = _prepare_signable_fields(checkout_signature_field_order, stripped_fields)
    return _sign_fields(signable_fields)


def itn_signature(itn_data):  # type: (Mapping[str, str]) -> str
    """
    Calculate the signature of an ITN submission.
    """
    # ITN signatures include fields with empty values.
    included_fields = _drop_non_signature_fields(itn_data, include_empty=True)
    signable_fields = _prepare_signable_fields(itn_signature_field_order, included_fields)
    return _sign_fields(signable_fields)


# TODO: Rework this and data_is_valid.
def _values_to_encode(data):
    return [
        (k, str(value).strip().encode('utf8'))
        for (k, value) in data.items()
        if k != 'signature'
    ]


def data_is_valid(post_data, postback_server=POSTBACK_SERVER):
    """
    Validates data via the postback. Returns True if data is valid,
    False if data is invalid and None if the request failed.
    """
    post_str = urlencode(_values_to_encode(post_data))  # type: str
    # FIXME: No Content-Type header.
    post_bytes = post_str.encode(settings.DEFAULT_CHARSET)  # type: bytes

    postback_url = postback_server.rstrip('/') + POSTBACK_URL
    try:
        response = urlopen(postback_url, data=post_bytes)
        result = response.read().decode('utf-8')  # XXX: Assumed encoding
    except HTTPError:
        # XXX: Just re-raise for now.
        raise

    if result == 'VALID':
        return True
    elif result == 'INVALID':
        return False
    else:
        raise NotImplementedError('Unexpected result from PayFast validation: {!r}'.format(result))
