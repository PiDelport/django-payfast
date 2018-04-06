from __future__ import unicode_literals

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

if hasattr(settings, 'PAYFAST_URL_BASE'):
    URL_BASE = settings.PAYFAST_URL_BASE
else:
    raise ImproperlyConfigured(
        'Please configure settings.PAYFAST_URL_BASE with the base URL of your site'
        ' (as a string, or a callable returning a string)')

TEST_MODE = getattr(settings, 'PAYFAST_TEST_MODE', False)

TEST_MERCHANT_ID = '10000100'
TEST_MERCHANT_KEY = '46f0cd694581a'

if TEST_MODE:
    # real id and key don't work in sandbox
    MERCHANT_ID = TEST_MERCHANT_ID
    MERCHANT_KEY = TEST_MERCHANT_KEY
else:
    MERCHANT_ID = getattr(settings, 'PAYFAST_MERCHANT_ID')
    MERCHANT_KEY = getattr(settings, 'PAYFAST_MERCHANT_KEY')

LIVE_SERVER = 'https://www.payfast.co.za'
SANDBOX_SERVER = 'https://sandbox.payfast.co.za'
SERVER = SANDBOX_SERVER if TEST_MODE else LIVE_SERVER

PROCESS_URL = SERVER + '/eng/process'

REQUIRE_AMOUNT_MATCH = getattr(settings, 'PAYFAST_REQUIRE_AMOUNT_MATCH', True)
USE_POSTBACK = getattr(settings, 'PAYFAST_USE_POSTBACK', True)

# request.META key with client ip address
IP_HEADER = getattr(settings, 'PAYFAST_IP_HEADER', 'REMOTE_ADDR')

# Reference: https://developers.payfast.co.za/documentation/#ip-addresses
# The values below are current as of 2017 December.
DEFAULT_PAYFAST_IP_ADDRESSES = [
    '197.97.145.144/28',
    '41.74.179.192/27',
]
