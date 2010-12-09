"""
This module can be used without django
"""
from hashlib import md5
import urllib2
from urllib import urlencode

POSTBACK_URL = 'https://www.payfast.co.za/eng/query/validate'

def _signature_string(data):
    values = [(k, unicode(data[k]).encode('utf8'),) for k in data if data[k]]
    return urlencode(values)

def siganture(data):
    """
    Calculates PayFast signature.
    'data' should be a SortedDict or an OrderedDict instance.
    """
    text = _signature_string(data)
    return md5(text).hexdigest()

def data_is_valid(raw_post_data, postback_url=POSTBACK_URL):
    """
    Validates data via the postback. Returns True if data is valid,
    False if data is invalid and None if the request failed.
    """
    import ipdb; ipdb.set_trace()
    try:
        response = urllib2.urlopen(postback_url, raw_post_data).read()
    except urllib2.HTTPError:
        return None
    if response == 'VALID':
        return True
    if response == 'INVALID':
        return False
    return None
