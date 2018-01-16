"""
This module can be used without django
"""
from hashlib import md5

# Python 2 compatibility:
from six import text_type as str
from six.moves.urllib.error import HTTPError
from six.moves.urllib.parse import urlencode
from six.moves.urllib.request import urlopen

from django.conf import settings


POSTBACK_URL = '/eng/query/validate'
POSTBACK_SERVER = 'https://www.payfast.co.za'


def _values_to_encode(data):
    return [
        (k, str(value).strip().encode('utf8'))
        for (k, value) in data.items()
        if k != 'signature' and value
    ]


def _signature_string(data):
    values = _values_to_encode(data)
    return urlencode(values)


# TODO: Handle field ordering as part of signature()
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
    post_str = urlencode(_values_to_encode(post_data))  # type: str
    # FIXME: No Content-Type header.
    post_bytes = post_str.encode(settings.DEFAULT_CHARSET)  # type: bytes

    postback_url = postback_server.rstrip('/') + POSTBACK_URL
    try:
        response = urlopen(postback_url, data=post_bytes)
        result = response.read().decode('utf-8')  # XXX: Assumed encoding
    except HTTPError:
        # XXX: Just re-raise for now.
        raise

    if result == 'VALID':
        return True
    elif result == 'INVALID':
        return False
    else:
        raise NotImplementedError('Unexpected result from PayFast validation: {!r}'.format(result))
