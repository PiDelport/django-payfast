"""
This module can be used without django
"""
from hashlib import md5
import urllib2
import logging
from urllib import urlencode

POSTBACK_URL = '/eng/query/validate'
POSTBACK_SERVER = 'https://www.payfast.co.za'

def _values_to_encode(data):
    return [
        (k, unicode(data[k]).strip().encode('utf8'),)
        for k in data if data[k] and k != 'signature'
    ]

def _signature_string(data):
    values = _values_to_encode(data)
    return urlencode(values)

def signature(data):
    """
    Calculates PayFast signature.
    'data' should be a SortedDict or an OrderedDict instance.
    """
    text = _signature_string(data)
    return md5(text).hexdigest()

def data_is_valid(post_data, postback_server=POSTBACK_SERVER):
    """
    Validates data via the postback. Returns True if data is valid,
    False if data is invalid and None if the request failed.
    """
    post_str = urlencode(_values_to_encode(post_data))
    postback_url = postback_server.rstrip('/') + POSTBACK_URL
    try:
        response = urllib2.urlopen(postback_url, post_str).read()
    except urllib2.HTTPError:
        return None
    if response == 'VALID':
        return True
    if response == 'INVALID':
        return False
    return None
