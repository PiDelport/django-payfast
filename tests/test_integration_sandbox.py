"""
Integration tests against the PayFast sandbox environment.
"""
from __future__ import unicode_literals

import decimal
import os
from queue import Queue  # noqa: F401
from textwrap import dedent
from typing import Dict, Iterable, Tuple, Mapping  # noqa: F401
from xml.etree.ElementTree import ElementTree  # noqa: F401

from payfast import api

import html5lib
import requests

import pytest

from etree_helpers import text_collapsed, text_lines, find_id_maybe, find_id
from itn_helpers import itn_handler


# PayFast sandbox details
sandbox_process_url = 'https://sandbox.payfast.co.za/eng/process'
sandbox_merchant_credentials = {
    'merchant_id': '10000100',
    'merchant_key': '46f0cd694581a',
}


def post_sandbox_checkout(checkout_data):  # type: (Dict[str, str]) -> requests.Response
    """
    Post data to the PayFast sandbox checkout process endpoint.
    """
    response = requests.post(sandbox_process_url, checkout_data)
    response.raise_for_status()
    return response


def post_sandbox_payment(
        session_type,  # type: str
        session_id,  # type: str
        selected_method,  # type: str
):  # type: (...) -> requests.Response
    """
    Post a PayFast sandbox wallet payment confirmation.

    The parameters should come from the checkout page.
    """
    # This call is referenced from:
    # https://sandbox.payfast.co.za/js/engine_v2.js?version=5.2.6
    # (See the #pay-with-wallet click handler.)
    url = sandbox_process_url + '/payment_method?{}={}'.format(session_type, session_id)
    response = requests.post(url, {'selected_method': selected_method})
    response.raise_for_status()
    return response


def parse_payfast_page(response):  # type: (requests.Response) -> Dict[str, str]
    """
    Scrape some data from a PayFast payment page response.
    """
    assert 'text/html; charset=UTF-8' == response.headers['Content-Type']
    html = response.text
    doc = html5lib.parse(html)  # type: ElementTree

    def _parse():  # type: () -> Iterable[Tuple[str, str]]
        # The session info:
        session_tracker = find_id(doc, 'session-tracker')
        for name in ['type', 'id']:
            value = session_tracker.attrib['data-{}'.format(name)]
            if value:
                yield ('session_{}'.format(name), value)

        # The payment summary on the left.
        left = find_id(doc, 'left-column')
        yield ('payment_summary', text_collapsed(left))

        right = find_id(doc, 'right-column')
        content_box = find_id(right, 'contentBox')

        # The error notice, if any:
        notice = find_id_maybe(content_box, 'notice')
        if notice is not None:
            yield ('notice', text_lines(notice))

        # The wallet payment completion option, if present:
        wa_tab = find_id_maybe(content_box, 'waTab')
        if wa_tab is not None:
            yield ('payment_method', (wa_tab.attrib['data-methodkey']))
            pay_button = find_id(wa_tab, 'pay-with-wallet')
            yield ('pay_button', text_collapsed(pay_button))

    return dict(_parse())


def test_process_empty():  # type: () -> None
    """
    Submitting an empty payment request fails.
    """
    response = post_sandbox_checkout({})
    assert {
        'payment_summary': 'Payment total R ZAR',
        'notice': dedent("""\
            The supplied variables are not according to specification:
            amount : amount is required
            item_name : item_name is required
            merchant_id : merchant_id is required
            merchant_key : merchant_key is required
        """),
    } == parse_payfast_page(response)


def do_complete_payment(
        data,  # type: Mapping[str, str]
        sign_checkout_process=True,  # type: bool
):  # type: (...) -> None
    """
    A payment request + completion flow.
    """
    # Expected values for result assertions:
    try:
        expected_amount = '{:.2f}'.format(decimal.Decimal(data['amount']))
    except decimal.InvalidOperation:
        # We may be testing a value that isn't Decimal-parseable;
        # in that case, just expect it unmodified.
        expected_amount = data['amount']
    expected_item_name = data['item_name'].strip()  # PayFast strips this for display.
    expected_payment_summary = (
        '{} Payment total R {} ZAR'.format(expected_item_name, expected_amount)
    )

    # Step 1: Request payment.
    process_data = {}
    process_data.update(sandbox_merchant_credentials)
    process_data.update(data)

    if sign_checkout_process:
        assert 'signature' not in process_data, process_data
        process_data['signature'] = api.checkout_signature(process_data)

    response1 = post_sandbox_checkout(process_data)
    parsed1 = parse_payfast_page(response1)
    assert {
        'session_type': 'p-sb',
        'session_id': parsed1.get('session_id', 'MISSING'),
        'payment_summary': expected_payment_summary,
        'payment_method': '1',
        'pay_button': 'Complete Payment',
    } == parsed1

    # Step 2: Complete payment.
    response2 = post_sandbox_payment(
        parsed1['session_type'],
        parsed1['session_id'],
        parsed1['payment_method'],
    )
    parsed2 = parse_payfast_page(response2)
    assert {
        'payment_summary': expected_payment_summary,
        'notice': 'Your payment was successful\n'
    } == parsed2


def test_minimal_successful_payment_unsigned():  # type: () -> None
    """
    A minimal process + payment flow.
    """
    checkout_data = {
        'amount': '123',
        'item_name': 'Flux capacitor',
    }
    do_complete_payment(checkout_data, sign_checkout_process=False)


def test_minimal_successful_payment_signed():  # type: () -> None
    """
    A minimal process + payment flow, with signature.
    """
    checkout_data = {
        'amount': '123',
        'item_name': 'Flux capacitor',
    }
    do_complete_payment(checkout_data, sign_checkout_process=True)


# Check for ITN testing configuration:
try:
    ITN_HOST = os.environ['ITN_HOST']
    ITN_PORT = int(os.environ['ITN_PORT'])
    ITN_URL = os.environ['ITN_URL']
except KeyError:
    itn_configured = False
else:
    itn_configured = True


# Helper pytest mark for tests than need ITN handling configured.
requires_itn_configured = pytest.mark.skipif(not itn_configured, reason="""\
Configure the following environment variables to test ITN:
    ITN_HOST: The local host to listen on
    ITN_PORT: The local port to listen on
    ITN_URL: The notify_url to pass to PayFast
""")


@requires_itn_configured
def test_minimal_payment_itn():  # type: () -> None
    """
    A minimal payment with ITN.
    """
    checkout_data = {
        'amount': '123',
        'item_name': 'Flux capacitor',
        # Enable ITN:
        'notify_url': ITN_URL,
    }
    with itn_handler(ITN_HOST, ITN_PORT) as itn_queue:  # type: Queue
        do_complete_payment(checkout_data)
        itn_data = itn_queue.get(timeout=2)

    calculated_signature = api.itn_signature(itn_data)

    assert itn_data == {
        'm_payment_id': '',
        'pf_payment_id': itn_data.get('pf_payment_id', 'MISSING'),
        'payment_status': 'COMPLETE',
        'item_name': 'Flux capacitor',
        'item_description': '',
        'amount_gross': '123.00',
        'amount_fee': '-2.80',
        'amount_net': '120.20',
        'custom_str1': '',
        'custom_str2': '',
        'custom_str3': '',
        'custom_str4': '',
        'custom_str5': '',
        'custom_int1': '',
        'custom_int2': '',
        'custom_int3': '',
        'custom_int4': '',
        'custom_int5': '',
        'name_first': 'Test',
        'name_last': 'User 01',
        'email_address': 'sbtu01@payfast.co.za',
        'merchant_id': '10000100',
        'signature': calculated_signature,
    }


@pytest.mark.parametrize(('leading', 'trailing'), [

    # These whitespace characters should be ignored:
    ('', ' '),
    (' ', ''),
    (' ', ' '),
    ('\t', '\t'),
    ('\n', '\n'),
    ('\r', '\r'),
    ('\x0b', '\x0b'),  # \N{LINE TABULATION} (Python 2 does not know this Unicode character name)

    # XXX: PayFast seems to refuse null-containing values, so we can't test their signatures.
    # ('\0', '\0'),

    # These whitespace characters should be included:
    ('\N{NO-BREAK SPACE}', '\N{NO-BREAK SPACE}'),  # '\xa0'

])
def test_checkout_signature_ignored_whitespace(leading, trailing):  # type: (str, str) -> None
    """
    Checkout signatures should ignore certain leading and trailing whitespace in values.
    """
    checkout_data = {
        'merchant_id': '10000100',
        'merchant_key': '46f0cd694581a',
        'amount': '123',
        'item_name': 'Flux capacitor',
        'item_description': '1.21 jigowatts',
        'name_first': 'Emmet',
        'name_last': 'Brown',
        # TODO: Cover other field values?
    }
    whitespaced_data = {
        name: (leading + value + trailing)
        for (name, value) in checkout_data.items()
    }

    # Special-case handling: these three fields accept other whitespace, but not NBSP.
    # Just revert them for testing (but let the other fields still contain NBSP).
    for name in ['merchant_id', 'merchant_key', 'amount']:
        whitespaced_data[name] = whitespaced_data[name].strip('\N{NO-BREAK SPACE}')

    do_complete_payment(whitespaced_data)
