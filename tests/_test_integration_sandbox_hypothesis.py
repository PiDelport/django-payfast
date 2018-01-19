"""
Hypothesis-driven integration testing against the PayFast sandbox environment.

Handle and run with care!

This should probably only be run interactively, and not as part of the normal test suite.
"""
from __future__ import unicode_literals

import string
import time
from typing import Dict, Mapping, Callable, List  # noqa: F401

from hypothesis import given, assume, settings
from hypothesis import strategies as st

from test_integration_sandbox import (
    sandbox_merchant_credentials,
    requires_itn_configured,
    do_complete_payment,
)


# The minimum set of checkout fields that are required by PayFast.
required_checkout_fields = {
    'merchant_id',
    'merchant_key',
    'amount',
    'item_name',
}


def valid_text(
        min_size=None,  # type: int
        average_size=None,  # type: int
        max_size=None,  # type: int
):  # type: (...) -> st.S
    """
    Helper strategy for valid PayFast field value strings.
    """
    return (st.text(min_size=min_size, average_size=average_size, max_size=max_size)
            # PayFast seems to categorically refuse (with a low-level HTTP 403 Forbidden)
            # requests with values that contain nulls, so avoid generating these.
            .filter(lambda s: '\0' not in s))


@st.composite
def st_checkout_data(draw):  # type: (Callable) -> Mapping[str, str]
    """
    Strategy for generating valid checkout data.
    """
    # Requesting large amounts drains the sandbox wallet balance quickly, before it can be refilled.
    # When this happens, requesting amounts over the wallet balance
    # seems to result in a redirect loop, instead of a clean error.
    max_amount = 1000

    # Valid checkout amounts:
    st_amount = (st.decimals(min_value=0, max_value=max_amount,
                             allow_nan=False, allow_infinity=False)
                 .filter(lambda amount: amount != 0)  # The amount can't be exactly zero.
                 .map(str))

    # The required keys:
    checkout_data = dict(sandbox_merchant_credentials)
    checkout_data.update({
        'amount': draw(st_amount),
        'item_name': draw(valid_text(min_size=1, max_size=100)),
    })

    # The m_payment_id field has a specific limited character repertoire.
    m_payment_id_alphabet = string.ascii_letters + string.digits + '_-/'

    # Optional keys
    optional_fields_spec = {

        # Merchant Details
        # Already required: 'merchant_id',
        # Already required: 'merchant_key',
        # 'return_url',
        # 'cancel_url',
        # 'notify_url',

        # Buyer Detail
        'name_first': valid_text(max_size=100),
        'name_last': valid_text(max_size=100),
        # 'email_address',
        # 'cell_number',

        # Transaction Details
        'm_payment_id': st.text(alphabet=m_payment_id_alphabet, max_size=100),
        # Already required: 'amount',
        # Already required: 'item_name',
        'item_description': valid_text(max_size=255),
        'custom_int1': st.text(alphabet=string.digits, max_size=255),
        'custom_int2': st.text(alphabet=string.digits, max_size=255),
        'custom_int3': st.text(alphabet=string.digits, max_size=255),
        'custom_int4': st.text(alphabet=string.digits, max_size=255),
        'custom_int5': st.text(alphabet=string.digits, max_size=255),
        'custom_str1': valid_text(max_size=255),
        'custom_str2': valid_text(max_size=255),
        'custom_str3': valid_text(max_size=255),
        'custom_str4': valid_text(max_size=255),
        'custom_str5': valid_text(max_size=255),

        # Transaction Options
        # 'email_confirmation',
        # 'confirmation_address',

        # Set Payment Method
        # 'payment_method',

        # Recurring Billing Details
        # 'subscription_type',
        # 'billing_date',
        # 'recurring_amount',
        # 'frequency',
        # 'cycles',

    }

    # Make the fields optional by wrapping the values in singleton lists (simulating a Maybe type),
    # and flattening and skipping empty ones.
    optional_fields_intermediate = draw(st.fixed_dictionaries({
        k: st.lists(s, max_size=1)
        for (k, s) in optional_fields_spec.items()
    }))  # type: Dict[str, List[str]]
    # Flatten
    optional_fields = {
        k: v[0]
        for (k, v) in optional_fields_intermediate.items()
        if v
    }  # type: Dict[str, str]

    checkout_data.update(optional_fields)

    return checkout_data


@requires_itn_configured
@settings(
    # Attempt a vaguely API-friendly configuration:
    max_examples=10,
    max_iterations=1,
    max_shrinks=10,
    deadline=5000,
)
@given(st_checkout_data())
def test_complete_payment(checkout_data):  # type: (Mapping[str, str]) -> None
    assert required_checkout_fields <= checkout_data.keys()

    # XXX: PayFast treats '0' this as empty?
    assume(checkout_data['item_name'] != '0')

    # XXX: PayFast seems to normalise '\r' -> '\n' ?
    assume('\r' not in checkout_data['item_name'])

    try:
        print('XXX Starting payment...', checkout_data)
        do_complete_payment(checkout_data, sign_checkout=True, enable_itn=True)
        print('XXX Successful!')
    except AssertionError:
        print('XXX Got assertion failure.')
        raise
    except Exception as e:
        print('XXX Got error:', e)
        raise
    finally:
        # XXX: Hacky rate limiting: one second between requests.
        time.sleep(1)
