from django.conf import settings

TEST_MODE = getattr(settings, 'PAYFAST_TEST_MODE', False)

TEST_MERCHANT_ID = '10000100'
TEST_MERCHANT_KEY = '46f0cd694581a'

MERCHANT_ID = getattr(settings, 'PAYFAST_MERCHANT_ID', TEST_MERCHANT_ID)
MERCHANT_KEY = getattr(settings, 'PAYFAST_MERCHANT_KEY', TEST_MERCHANT_KEY)

if TEST_MODE:
    # real id and key don't work in sandbox
    MERCHANT_ID = TEST_MERCHANT_ID
    MERCHANT_KEY = TEST_MERCHANT_KEY

LIVE_SERVER = 'https://www.payfast.co.za'
SANDBOX_SERVER = 'https://sandbox.payfast.co.za'
SERVER = SANDBOX_SERVER if TEST_MODE else LIVE_SERVER

PROCESS_URL = SERVER + '/eng/process'

REQUIRE_AMOUNT_MATCH = getattr(settings, 'PAYFAST_REQUIRE_AMOUNT_MATCH', True)
USE_POSTBACK = getattr(settings, 'PAYFAST_USE_POSTBACK', True)

IP_HEADER = getattr(settings, 'PAYFAST_IP_HEADER', 'REMOTE_ADDR') # request.META key with client ip address
IP_ADDRESSES = getattr(settings, 'PAYFAST_IP_ADDRESSES', ['196.33.227.224', '196.33.227.225'])

