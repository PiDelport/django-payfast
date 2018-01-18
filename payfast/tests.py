# coding: utf-8
from __future__ import unicode_literals

import json
import unittest
from collections import OrderedDict

import django
from django.conf import settings
from django.test import TestCase, SimpleTestCase, override_settings

from payfast import api
from payfast import conf
from payfast.forms import notify_url, PayFastForm, is_payfast_ip_address
from payfast.models import PayFastOrder
import payfast.signals


def _test_data():
    return OrderedDict([
        ('merchant_id', '10000100'),
        ('merchant_key', '46f0cd694581a'),
        ('notify_url', "http://127.0.0.1:8000/payfast/notify/"),
        ('name_first', "Вася"),
        ('name_last', 'Пупников'),
        ('m_payment_id', '23'),
        ('amount', '234'),
        ('item_name', "Payment (Планета суши). ID:272-15"),
    ])


def _itn_data_from_checkout(checkout_data, payment_form):
    notify_data = checkout_data.copy()
    # prepare server data
    notify_data['m_payment_id'] = payment_form.order.m_payment_id
    notify_data['amount_gross'] = checkout_data['amount']
    # Fields not part of ITN submissions:
    del notify_data['notify_url']
    del notify_data['amount']
    del notify_data['merchant_key']

    # Sign:
    notify_data['signature'] = api.itn_signature(notify_data)
    return notify_data


def _order():
    return PayFastOrder.objects.all()[0]


class SignatureTest(unittest.TestCase):
    # TODO: This needs better coverage.

    def test_checkout_signature(self):
        data = _test_data()
        self.assertEqual(api.checkout_signature(data), '481366608545707be67c6514386b3fb1')

    def test_checkout_signature_blank_fields(self):
        """
        Fields with blank values should not be included in the signature.
        """
        data = _test_data()
        data['name_first'] = ''
        self.assertEqual(api.checkout_signature(data), '6551205f0fee13cf09174b0b887ec5b3')
        data['name_last'] = ''
        self.assertEqual(api.checkout_signature(data), '8f6435965cd9b00a9a965d93fc6c4c48')

    def test_known_good_itn_signature(self):
        known_good_itn_data = {
            'amount_fee': '-2.80',
            'amount_gross': '123.00',
            'amount_net': '120.20',
            'custom_int1': '',
            'custom_int2': '',
            'custom_int3': '',
            'custom_int4': '',
            'custom_int5': '',
            'custom_str1': '',
            'custom_str2': '',
            'custom_str3': '',
            'custom_str4': '',
            'custom_str5': '',
            'email_address': 'sbtu01@payfast.co.za',
            'item_description': '',
            'item_name': 'Flux capacitor',
            'm_payment_id': '',
            'merchant_id': '10000100',
            'name_first': 'Test',
            'name_last': 'User 01',
            'payment_status': 'COMPLETE',
            'pf_payment_id': '558900',
            'signature': '94b05677771813701468289ed3cabed1',
        }

        calculated_signature = api.itn_signature(known_good_itn_data)
        assert known_good_itn_data['signature'] == calculated_signature


@override_settings(PAYFAST_IP_ADDRESSES=['127.0.0.1'])
class NotifyTest(TestCase):

    def setUp(self):
        conf.USE_POSTBACK = False
        conf.MERCHANT_ID = '10000100'
        conf.REQUIRE_AMOUNT_MATCH = True

        self.notify_handler_orders = []  # type: list
        payfast.signals.notify.connect(self.notify_handler)

    def tearDown(self):
        payfast.signals.notify.disconnect(self.notify_handler)

    def notify_handler(self, sender, order, **kwargs):
        self.notify_handler_orders.append(order)

    def _create_order(self):
        """
        Create a payment order, and return the notification data for it.
        """
        checkout_data = _test_data()

        # user posts the pay request
        payment_form = PayFastForm(initial={
            'amount': checkout_data['amount'],
            'item_name': checkout_data['item_name']
        })
        self.assertEqual(_order().trusted, None)

        return _itn_data_from_checkout(checkout_data, payment_form)

    def _assertBadRequest(self, response, expected_json):
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_json = json.loads(response.content)
        self.assertEqual(response_json, expected_json)

    def test_notify(self):
        notify_data = self._create_order()
        order = _order()

        # the server sends a notification
        response = self.client.post(notify_url(), notify_data)
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(self.notify_handler_orders, [order])

        order = _order()
        self.assertEqual(order.request_ip, '127.0.0.1')
        self.assertEqual(order.debug_info, '')
        self.assertEqual(order.trusted, True)

    def test_untrusted_ip(self):
        """
        The notify handler rejects notification attempts from untrusted IP address.
        """
        notify_data = self._create_order()

        # the server sends a notification
        response = self.client.post(notify_url(), notify_data, REMOTE_ADDR='127.0.0.2')
        self._assertBadRequest(response, {
            '__all__': [{'code': '', 'message': 'untrusted ip: 127.0.0.2'}],
        })
        self.assertEqual(self.notify_handler_orders, [])

        order = _order()
        self.assertEqual(order.request_ip, '127.0.0.2')
        self.assertEqual(order.debug_info, '__all__: untrusted ip: 127.0.0.2')
        self.assertEqual(order.trusted, False)

    def test_non_existing_order(self):
        response = self.client.post(notify_url(), {})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.notify_handler_orders, [])

        self.assertQuerysetEqual(PayFastOrder.objects.all(), [])

    def test_invalid_request(self):
        form = PayFastForm(initial={'amount': 100, 'item_name': 'foo'})
        notify_data = {'m_payment_id': form.order.m_payment_id}
        notify_data['signature'] = api.itn_signature(notify_data)
        response = self.client.post(notify_url(), notify_data)
        expected_amount = ('100' if django.VERSION < (1, 8) else
                           '100.00' if django.VERSION < (2, 0) else
                           '100')
        self._assertBadRequest(response, {
            'amount_gross': [{'code': '', 'message': ('Amount is not the same: {} != None'
                                                      .format(expected_amount))}],
            'item_name': [{'code': 'required', 'message': 'This field is required.'}],
            'merchant_id': [{'code': 'required', 'message': 'This field is required.'}],
        })
        self.assertEqual(self.notify_handler_orders, [])

        order = _order()
        self.assertEqual(order.request_ip, '127.0.0.1')
        self.assertEqual(set(order.debug_info.split('|')), {
            'amount_gross: Amount is not the same: {} != None'.format(
                '100' if django.VERSION < (1, 8) else
                # Django 1.8+ returns more precise DecimalField values
                '100.00' if django.VERSION < (2, 0) else
                # Django 2.0+ returns less precise DecimalField values again.
                '100'
            ),
            'item_name: This field is required.',
            'merchant_id: This field is required.',
        })
        self.assertEqual(order.trusted, False)


class IPTest(SimpleTestCase):

    @override_settings(PAYFAST_IP_ADDRESSES=[])
    def test_no_addresses(self):
        self.assertFalse(is_payfast_ip_address('127.0.0.1'))
        self.assertFalse(is_payfast_ip_address('41.74.179.194'))

    @override_settings(PAYFAST_IP_ADDRESSES=['127.0.0.1'])
    def test_localhost(self):
        self.assertTrue(is_payfast_ip_address('127.0.0.1'))
        self.assertFalse(is_payfast_ip_address('41.74.179.194'))

    @override_settings(PAYFAST_IP_ADDRESSES=['41.74.179.194'])
    def test_one_server(self):
        self.assertFalse(is_payfast_ip_address('127.0.0.1'))
        self.assertTrue(is_payfast_ip_address('41.74.179.194'))

    @override_settings(PAYFAST_IP_ADDRESSES=['196.33.227.224', '196.33.227.225'])
    def test_more_servers(self):
        self.assertFalse(is_payfast_ip_address('127.0.0.1'))
        self.assertFalse(is_payfast_ip_address('41.74.179.194'))
        self.assertTrue(is_payfast_ip_address('196.33.227.224'))
        self.assertTrue(is_payfast_ip_address('196.33.227.225'))

    @override_settings(PAYFAST_IP_ADDRESSES=['196.33.227.224/31'])
    def test_more_servers_masked(self):
        self.assertFalse(is_payfast_ip_address('127.0.0.1'))
        self.assertFalse(is_payfast_ip_address('41.74.179.194'))

        self.assertFalse(is_payfast_ip_address('196.33.227.223'))
        self.assertTrue(is_payfast_ip_address('196.33.227.224'))
        self.assertTrue(is_payfast_ip_address('196.33.227.225'))
        self.assertFalse(is_payfast_ip_address('196.33.227.226'))

    @override_settings(PAYFAST_IP_ADDRESSES=[])
    def test_default_ip_addresses(self):
        del settings.PAYFAST_IP_ADDRESSES

        self.assertFalse(is_payfast_ip_address('127.0.0.1'))
        self.assertFalse(is_payfast_ip_address('196.33.227.224'))

        # Default PayFast range: 197.97.145.144/28
        self.assertFalse(is_payfast_ip_address('197.97.145.143'))
        self.assertTrue(all(is_payfast_ip_address('197.97.145.{}'.format(n))
                            for n in range(144, 160)))
        self.assertFalse(is_payfast_ip_address('197.97.145.160'))

        # Default PayFast range: 41.74.179.192/27
        self.assertFalse(is_payfast_ip_address('41.74.179.191'))
        self.assertTrue(all(is_payfast_ip_address('41.74.179.{}'.format(n))
                            for n in range(192, 224)))
        self.assertFalse(is_payfast_ip_address('41.74.179.225'))
