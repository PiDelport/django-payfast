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


# Check for ITN testing configuration:
try:
    ITN_HOST = os.environ['ITN_HOST']
    ITN_PORT = int(os.environ['ITN_PORT'])
    ITN_URL = os.environ['ITN_URL']
except KeyError:
    itn_configured = False
else:
    itn_configured = True


ITN_HELP_MESSAGE = """\
Configure the following environment variables to test ITN:
    ITN_HOST: The local host to listen on
    ITN_PORT: The local port to listen on
    ITN_URL: The notify_url to pass to PayFast
"""

#: Helper pytest mark for tests than need ITN handling configured.
requires_itn_configured = pytest.mark.skipif(not itn_configured, reason=ITN_HELP_MESSAGE)


def require_itn_configured():  # type: () -> None
    """
    pytest.skip() if not itn_configured.
    """
    if not itn_configured:
        pytest.skip(ITN_HELP_MESSAGE)


def do_checkout(
        checkout_data,  # type: Dict[str, str]
        sign_checkout,  # type: bool
):  # type: (...) -> Dict[str, str]
    """
    Common test helper: do a checkout, and assert results.

    This takes unsigned checkout data, and will add a signature if `sign_checkout` is true.

    Return the checkout page's parse.
    """
    # Expected values for result assertions:
    try:
        expected_amount = '{:.2f}'.format(decimal.Decimal(checkout_data['amount']))
    except decimal.InvalidOperation:
        # We may be testing a value that isn't Decimal-parseable;
        # in that case, just expect it unmodified.
        expected_amount = checkout_data['amount']
    expected_item_name = checkout_data['item_name'].strip()  # PayFast strips this for display.
    expected_payment_summary = (
        '{} Payment total R {} ZAR'.format(expected_item_name, expected_amount)
        .strip()  # Strip to handle item names that render empty.
    )

    if sign_checkout:
        assert 'signature' not in checkout_data, checkout_data
        checkout_data['signature'] = api.checkout_signature(checkout_data)

    response = post_sandbox_checkout(checkout_data)
    parsed = parse_payfast_page(response)
    assert {
        'session_type': 'p-sb',
        'session_id': parsed.get('session_id', 'MISSING'),
        'payment_summary': expected_payment_summary,
        'payment_method': '1',
        'pay_button': 'Complete Payment',
    } == parsed

    return parsed


def do_payment(
        checkout_data,  # Dict[str, str]
        parsed_checkout,  # Dict[str, str]
        enable_itn,  # type: bool
):  # type: (...) -> Dict[str, str]
    """
    Common test helper: do a payment, and assert results.

    This takes a checkout's data and page parse (for session info and assertions).
    This will enable and verify ITN processing if `enable_itn` is true.

    Return the payment confirmation page's parse.
    """
    def _post_payment():  # type: () -> requests.Response
        return post_sandbox_payment(
            parsed_checkout['session_type'],
            parsed_checkout['session_id'],
            parsed_checkout['payment_method'],
        )

    if enable_itn:
        require_itn_configured()
        with itn_handler(ITN_HOST, ITN_PORT) as itn_queue:  # type: Queue
            response = _post_payment()
            itn_data = itn_queue.get(timeout=2)
    else:
        response = _post_payment()

    parsed_payment = parse_payfast_page(response)
    assert {
        'payment_summary': parsed_checkout['payment_summary'],
        'notice': 'Your payment was successful\n'
    } == parsed_payment

    if enable_itn:
        # Check the ITN result.

        # Expect whitespace-stripped versions of the checkout data.
        expected = {name: value.strip(api.CHECKOUT_SIGNATURE_IGNORED_WHITESPACE)
                    for (name, value) in checkout_data.items()}

        expected_amount_gross = '{:.2f}'.format(decimal.Decimal(checkout_data['amount'].strip()))

        expected_signature = api.itn_signature(itn_data)
        assert {
            'm_payment_id': expected.get('m_payment_id', ''),
            'pf_payment_id': itn_data.get('pf_payment_id', 'MISSING'),
            'payment_status': 'COMPLETE',
            'item_name': expected.get('item_name', 'MISSING'),
            'item_description': expected.get('item_description', ''),

            'amount_gross': expected_amount_gross,
            'amount_fee': itn_data.get('amount_fee', 'MISSING'),
            'amount_net': itn_data.get('amount_net', 'MISSING'),

            'custom_str1': expected.get('custom_str1', ''),
            'custom_str2': expected.get('custom_str2', ''),
            'custom_str3': expected.get('custom_str3', ''),
            'custom_str4': expected.get('custom_str4', ''),
            'custom_str5': expected.get('custom_str5', ''),
            'custom_int1': expected.get('custom_int1', ''),
            'custom_int2': expected.get('custom_int2', ''),
            'custom_int3': expected.get('custom_int3', ''),
            'custom_int4': expected.get('custom_int4', ''),
            'custom_int5': expected.get('custom_int5', ''),

            # The sandbox seems to fix these names, rather than using the checkout submission data.
            'name_first': 'Test',
            'name_last': 'User 01',

            'email_address': expected.get('email_address', 'sbtu01@payfast.co.za'),
            'merchant_id': '10000100',
            'signature': expected_signature,
        } == itn_data

    return parsed_payment


def do_complete_payment(
        partial_checkout_data,  # type: Mapping[str, str]
        sign_checkout,  # type: bool
        enable_itn,  # type: bool
):  # type: (...) -> None
    """
    Common test helper: A complete checkout + payment completion flow.

    This takes a partial checkout data, and will add sandbox merchant credentials,

     * Sandbox merchant credentials (if not supplied)
     * notify_url (if enable_itn is true)
    """
    if enable_itn:
        require_itn_configured()

    # Step 1: Prepare the checkout data:
    checkout_data = {}
    checkout_data.update(sandbox_merchant_credentials)
    checkout_data.update(partial_checkout_data)

    if enable_itn:
        assert 'notify_url' not in checkout_data, checkout_data
        checkout_data['notify_url'] = ITN_URL

    # Step 2: Checkout process.
    parsed_checkout = do_checkout(checkout_data, sign_checkout=sign_checkout)

    # Step 3: Complete payment.
    do_payment(checkout_data, parsed_checkout, enable_itn=enable_itn)


def test_minimal_successful_payment_unsigned():  # type: () -> None
    """
    A minimal process + payment flow.
    """
    checkout_data = {
        'amount': '123',
        'item_name': 'Flux capacitor',
    }
    do_complete_payment(checkout_data, sign_checkout=False, enable_itn=False)


def test_minimal_successful_payment_signed():  # type: () -> None
    """
    A minimal process + payment flow, with signature.
    """
    checkout_data = {
        'amount': '123',
        'item_name': 'Flux capacitor',
    }
    do_complete_payment(checkout_data, sign_checkout=True, enable_itn=False)


@requires_itn_configured
def test_minimal_payment_itn():  # type: () -> None
    """
    A minimal payment with ITN.
    """
    checkout_data = {
        'amount': '123',
        'item_name': 'Flux capacitor',
    }
    do_complete_payment(checkout_data, sign_checkout=True, enable_itn=True)


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

    do_complete_payment(whitespaced_data, sign_checkout=True, enable_itn=True)


@requires_itn_configured
def test_item_name_nbsp():  # type: () -> None
    """
    NBSP is a valid item name.
    """
    checkout_data = {
        'amount': '123',
        'item_name': '\N{NO-BREAK SPACE}',
    }
    do_complete_payment(checkout_data, sign_checkout=True, enable_itn=True)
