"""
This module can be used without django
"""
from hashlib import md5

# Python 2 compatibility:
from six import text_type as str
from six.moves.urllib.error import HTTPError
from six.moves.urllib.parse import urlencode
from six.moves.urllib.request import urlopen


POSTBACK_URL = '/eng/query/validate'
POSTBACK_SERVER = 'https://www.payfast.co.za'


def _values_to_encode(data):
    return [
        (k, str(data[k]).strip().encode('utf8'))
        for k in data if data[k] and k != 'signature'
    ]


def _signature_string(data):
    values = _values_to_encode(data)
    return urlencode(values)


def signature(data):
    """
    Calculates PayFast signature.
    'data' should be a OrderedDict instance.
    """
    text = _signature_string(data)
    return md5(text.encode('ascii')).hexdigest()


def data_is_valid(post_data, postback_server=POSTBACK_SERVER):
    """
    Validates data via the postback. Returns True if data is valid,
    False if data is invalid and None if the request failed.
    """
    post_str = urlencode(_values_to_encode(post_data))
    postback_url = postback_server.rstrip('/') + POSTBACK_URL
    try:
        response = urlopen(postback_url, post_str).read()
    except HTTPError:
        return None
    if response == 'VALID':
        return True
    if response == 'INVALID':
        return False
    return None
