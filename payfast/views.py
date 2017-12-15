from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from payfast.forms import NotifyForm
from payfast.models import PayFastOrder
from payfast import signals


@csrf_exempt
def notify_handler(request):
    """
    Notify URL handler.

    On successful access 'payfast.signals.notify' signal is sent.
    Orders should be processed in signal handler.
    """
    m_payment_id = request.POST.get('m_payment_id', None)
    order = get_object_or_404(PayFastOrder, m_payment_id=m_payment_id)

    form = NotifyForm(request, request.POST, instance=order)
    if not form.is_valid():
        errors = form.plain_errors()[:255]
        order.request_ip = form.ip
        order.debug_info = errors
        order.trusted = False
        order.save()

        # XXX: Any possible data leakage here?
        return HttpResponseBadRequest(
            content_type='application/json',
            content=form.errors.as_json(),
        )

    order = form.save()
    signals.notify.send(sender=notify_handler, order=order)
    return HttpResponse()
