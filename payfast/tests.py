# coding: utf-8
import unittest
from django.test import TestCase
from django.utils.datastructures import SortedDict

from payfast.forms import notify_url, PayFastForm
from payfast.models import PayFastOrder
from payfast.api import siganture
from payfast import conf
import payfast.signals

def _test_data():
    data = SortedDict()
    data['merchant_id'] = '10000100'
    data['merchant_key'] = '46f0cd694581a'
    data['notify_url'] = "http://127.0.0.1:8000/payfast/notify/"
    data['name_first'] = u"Вася"
    data['last_name'] = u'Пупников'
    data['m_payment_id'] = '23'
    data['amount'] = '234'
    data['item_name'] = u"Payment (Планета суши). ID:272-15"
    return data

def _notify_data(data, payment_form):
    notify_data = data.copy()
    # prepare server data
    notify_data['m_payment_id'] = payment_form.order.pk
    notify_data['amount_gross'] = data['amount']
    del notify_data['amount']
    del notify_data['merchant_key']
    notify_data['signature'] = payment_form._signature
    return notify_data

def _order():
    return PayFastOrder.objects.all()[0]

class SignatureTest(unittest.TestCase):
    def test_signature(self):
        data = _test_data()
        self.assertEqual(siganture(data), 'c71d41dd5041bf28d819fe102ab0106b')

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

    def test_notify(self):
        data = _test_data()

        # user posts the pay request
        payment_form = PayFastForm(initial={
            'amount': data['amount'],
            'item_name': data['item_name']
        })
        self.assertEqual(_order().trusted, None)

        notify_data = _notify_data(data, payment_form)

        # the server sends a notification
        response = self.client.post(notify_url(), notify_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(_order().trusted, True)
        self.assertTrue(self.signal_handler.called)

    def test_non_existing_order(self):
        response = self.client.post(notify_url(), {})
        self.assertEqual(response.status_code, 404)
        self.assertFalse(self.signal_handler.called)

    def test_invalid_request(self):
        form = PayFastForm(initial={'amount': 100, 'item_name': 'foo'})
        response = self.client.post(notify_url(), {'m_payment_id': form.order.pk})
        self.assertEqual(response.status_code, 404)
        order = _order()
        self.assertEqual(order.trusted, False)
        self.assertFalse(self.signal_handler.called)
