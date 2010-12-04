from django.conf import settings

LIVE_URL = 'https://www.payfast.co.za/eng/process'
SANDBOX_URL = 'https://sandbox.payfast.co.za/eng/process'

MERCHANT_ID = settings.PAYFAST_MERCHANT_ID
MERCHANT_KEY = settings.PAYFAST_MERCHANT_KEY
TEST_MODE = getattr(settings, 'PAYFAST_TEST_MODE', False)

# request.META key with client ip address
IP_HEADER = getattr(settings, 'PAYFAST_IP_HEADER', 'REMOTE_ADDR')

IP_ADDRESSES = getattr(settings, 'PAYFAST_IP_ADDRESSES', ['196.33.227.224', '196.33.227.225'])
