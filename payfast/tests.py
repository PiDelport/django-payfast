# coding: utf-8
from __future__ import unicode_literals

import unittest
from collections import OrderedDict

import django
from django.test import TestCase

from payfast.forms import notify_url, PayFastForm
from payfast.models import PayFastOrder
from payfast.api import signature
from payfast import conf
import payfast.signals


def _test_data():
    data = OrderedDict()
    data['merchant_id'] = '10000100'
    data['merchant_key'] = '46f0cd694581a'
    data['notify_url'] = "http://127.0.0.1:8000/payfast/notify/"
    data['name_first'] = "Вася"
    data['last_name'] = 'Пупников'
    data['m_payment_id'] = '23'
    data['amount'] = '234'
    data['item_name'] = "Payment (Планета суши). ID:272-15"
    return data


def _notify_data(data, payment_form):
    notify_data = data.copy()
    # prepare server data
    notify_data['m_payment_id'] = payment_form.order.pk
    notify_data['amount_gross'] = data['amount']
    del notify_data['amount']
    del notify_data['merchant_key']
    notify_data['signature'] = signature(notify_data)
    return notify_data


def _order():
    return PayFastOrder.objects.all()[0]


class SignatureTest(unittest.TestCase):
    def test_signature(self):
        data = _test_data()
        self.assertEqual(signature(data), 'c71d41dd5041bf28d819fe102ab0106b')


class NotifyTest(TestCase):

    def setUp(self):
        conf.IP_ADDRESSES = ['127.0.0.1']
        conf.USE_POSTBACK = False
        conf.MERCHANT_ID = '10000100'
        conf.REQUIRE_AMOUNT_MATCH = True

        def handler(sender, **kwargs):
            handler.called = True
        handler.called = False
        self.signal_handler = handler
        payfast.signals.notify.connect(self.signal_handler)

    def tearDown(self):
        payfast.signals.notify.disconnect(self.signal_handler)

    def _create_order(self):
        """
        Create a payment order, and return the notification data for it.
        """
        data = _test_data()

        # user posts the pay request
        payment_form = PayFastForm(initial={
            'amount': data['amount'],
            'item_name': data['item_name']
        })
        self.assertEqual(_order().trusted, None)

        return _notify_data(data, payment_form)

    def test_notify(self):
        notify_data = self._create_order()

        # the server sends a notification
        response = self.client.post(notify_url(), notify_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.signal_handler.called)

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
        self.assertEqual(response.status_code, 404)
        self.assertFalse(self.signal_handler.called)

        order = _order()
        self.assertEqual(order.request_ip, '127.0.0.2')
        self.assertEqual(order.debug_info, '__all__: untrusted ip: 127.0.0.2')
        self.assertEqual(order.trusted, False)

    def test_non_existing_order(self):
        response = self.client.post(notify_url(), {})
        self.assertEqual(response.status_code, 404)
        self.assertFalse(self.signal_handler.called)

        self.assertQuerysetEqual(PayFastOrder.objects.all(), [])

    def test_invalid_request(self):
        form = PayFastForm(initial={'amount': 100, 'item_name': 'foo'})
        response = self.client.post(notify_url(), {'m_payment_id': form.order.pk})
        self.assertEqual(response.status_code, 404)
        self.assertFalse(self.signal_handler.called)

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
