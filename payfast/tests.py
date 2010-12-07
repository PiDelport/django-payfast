# coding: utf-8
import unittest
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils.datastructures import SortedDict

from payfast.forms import siganture
from django.contrib.auth.models import User

class SignatureTest(unittest.TestCase):
    def test_signature(self):
        data = SortedDict()
        data['merchant_id'] = '10000100'
        data['merchant_key'] = '46f0cd694581a'
        data['notify_url'] = "http://127.0.0.1:8000/payfast/notify/"
        data['name_first'] = u"Вася"
        data['last_name'] = u'Пупников'
        data['m_payment_id'] = '23'
        data['amount'] = '234'
        data['item_name'] = u"Payment (Планета суши). ID:272-15"
        self.assertEqual(siganture(data), 'c71d41dd5041bf28d819fe102ab0106b')
