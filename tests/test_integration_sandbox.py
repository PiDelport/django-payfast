"""
Integration tests against the PayFast sandbox environment.
"""
import os
from decimal import Decimal
from queue import Queue  # noqa: F401
from textwrap import dedent
from typing import Dict, Iterable, Tuple
from xml.etree.ElementTree import ElementTree  # noqa: F401

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


def sandbox_process_post(data: Dict[str, str]) -> requests.Response:
    """
    Post data to the PayFast process endpoint.
    """
    response = requests.post(sandbox_process_url, data)
    response.raise_for_status()
    return response


def sandbox_payment_post(
        session_type: str,
        session_id: str,
        selected_method: str,
) -> requests.Response:
    """
    Post a PayFast payment confirmation.
    """
    # Referenced from:
    # https://sandbox.payfast.co.za/js/engine_v2.js?version=5.2.6
    # (See #pay-with-wallet click handler.)
    url = sandbox_process_url + '/payment_method?{}={}'.format(session_type, session_id)
    response = requests.post(url, {'selected_method': selected_method})
    response.raise_for_status()
    return response


def parse_payfast_page(response: requests.Response) -> Dict[str, str]:
    """
    Scrape some data from a PayFast payment page response.
    """
    assert 'text/html; charset=UTF-8' == response.headers['Content-Type']
    html = response.text
    doc = html5lib.parse(html)  # type: ElementTree

    def _parse() -> Iterable[Tuple[str, str]]:
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


def test_process_empty():
    """
    Submitting an empty payment request fails.
    """
    response = sandbox_process_post({})
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


def do_complete_payment(data: Dict[str, str]) -> None:
    """
    A minimal payment request + completion flow.
    """
    # Values for result assertions:
    amount = '{:.2f}'.format(Decimal(data['amount']))
    item_name = data['item_name']
    expected_payment_summary = (
        '{} Payment total R {} ZAR'.format(item_name, amount)
    )

    # Step 1: Request payment.
    process_data = {}
    process_data.update(sandbox_merchant_credentials)
    process_data.update(data)

    response1 = sandbox_process_post(process_data)
    parsed1 = parse_payfast_page(response1)
    assert {
        'session_type': 'p-sb',
        'session_id': parsed1['session_id'],
        'payment_summary': expected_payment_summary,
        'payment_method': '1',
        'pay_button': 'Complete Payment',
    } == parsed1

    # Step 2: Complete payment.
    response2 = sandbox_payment_post(
        parsed1['session_type'],
        parsed1['session_id'],
        parsed1['payment_method'],
    )
    parsed2 = parse_payfast_page(response2)
    assert {
        'payment_summary': expected_payment_summary,
        'notice': 'Your payment was successful\n'
    } == parsed2


def test_minimal_successful_payment():
    """
    A minimal process + payment flow.
    """
    do_complete_payment({
        'amount': '123',
        'item_name': 'Flux capacitor',
    })


# Check for ITN testing configuration:
try:
    ITN_HOST = os.environ['ITN_HOST']
    ITN_PORT = int(os.environ['ITN_PORT'])
    ITN_URL = os.environ['ITN_URL']
except KeyError:
    itn_configured = False
else:
    itn_configured = True


@pytest.mark.skipif(not itn_configured, reason="""\
Configure the following environment variables to test ITN:
    ITN_HOST: The local host to listen on
    ITN_PORT: The local port to listen on
    ITN_URL: The notify_url to pass to PayFast
""")
def test_minimal_payment_itn():
    """
    A minimal payment with ITN.
    """
    data = {
        'amount': '123',
        'item_name': 'Flux capacitor',
        # Enable ITN:
        'notify_url': ITN_URL,
    }
    with itn_handler(ITN_HOST, ITN_PORT) as itn_queue:  # type: Queue
        do_complete_payment(data)
        itn_data = itn_queue.get(timeout=2)

    assert {
        'm_payment_id': '',
        'pf_payment_id': itn_data['pf_payment_id'],
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
        'signature': itn_data['signature'],
    } == itn_data
    # TODO: Verify ITN signature.
