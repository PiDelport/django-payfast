#coding: utf-8
from django.http import HttpResponse, Http404
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404

try:
    from django.views.decorators.csrf import csrf_exempt
except ImportError: # django < 1.2
    from django.contrib.csrf.middleware import csrf_exempt

from payfast.forms import NotifyForm
from payfast.models import PayFastOrder
from payfast import signals
from payfast.conf import IP_HEADER, IP_ADDRESSES

@csrf_exempt
def notify_handler(request):
    """
    Notify URL handler.

    On successful access 'payfast.signals.notify' signal is sent.
    Orders should be processed in signal handler.
    """
    id = request.POST.get('m_payment_id', None)
    order = get_object_or_404(PayFastOrder, pk=id)

    form = NotifyForm(request, request.POST, instance = order)
    if not form.is_valid():
        errors = form.plain_errors()[:255]
        order.request_ip = form.ip
        order.debug_info = errors
        order.trusted = False
        order.save()
        raise Http404

    order = form.save(commit=False)
    order.request_ip = ip
    order.debug_info = request.raw_post_data
    order.trusted = True
    order.save()
    signals.data.send(sender = notify_handler, order=order)
    return HttpResponse()
