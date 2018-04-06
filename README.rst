==============
django-payfast
==============

A pluggable Django application for integrating payfast.co.za payment system.

.. image:: https://img.shields.io/pypi/v/django-payfast.svg
    :target: https://pypi.python.org/pypi/django-payfast

.. image:: https://img.shields.io/badge/source-GitHub-lightgrey.svg
    :target: https://github.com/pjdelport/django-payfast

.. image:: https://img.shields.io/github/issues/pjdelport/django-payfast.svg
    :target: https://github.com/pjdelport/django-payfast/issues?q=is:open

.. image:: https://travis-ci.org/pjdelport/django-payfast.svg?branch=master
    :target: https://travis-ci.org/pjdelport/django-payfast

.. image:: https://codecov.io/github/pjdelport/django-payfast/coverage.svg?branch=master
    :target: https://codecov.io/github/pjdelport/django-payfast?branch=master

.. contents::

Install
=======

::

    $ pip install django-payfast

Then add 'payfast' to INSTALLED_APPS and execute ::

    $ python manage.py migrate


Settings
========

Specify your credentials in settings.py:

* ``PAYFAST_MERCHANT_ID``
* ``PAYFAST_MERCHANT_KEY``
* ``PAYFAST_URL_BASE``: The public-facing base URL of your site
  (used to qualify the notify URL passed to PayFast)

``PAYFAST_URL_BASE`` can either be a string, or a callable returning a string.
For example, if you use Django's sites framework to configure your domain::

    def PAYFAST_BASE_URL():
        from django.contrib.sites.models import Site
        site = Site.objects.get_current()
        return 'http://{}'.format(site.domain)


If your web server is behind reverse proxy you should also specify
``PAYFAST_IP_HEADER`` option. It's a ``request.META`` key with client ip address
(default is 'REMOTE_ADDR').

There is an option with PayFast server IP addresses (``PAYFAST_IP_ADDRESSES``).
It is a list with current PayFast servers' IP host / network addresses.
If they will change then override this option in your settings.py.

You also have to setup your PayFast account on payfast.co.za. Login into the
admin panel, go to 'My Account -> Integration', enable the Instant Transaction
Notification (ITN) and provide the Notify URL.

When passing a user to `PayFastForm`, the form will by default look for the
`first_name` and `last_name` fields on the user. If you're using a custom user
model with different field names, you can customise how the fields are looked
up by setting these callables::

    PAYFAST_GET_USER_FIRST_NAME = lambda user: user.my_first_name()
    PAYFAST_GET_USER_LAST_NAME = lambda user: user.my_last_name()

Alternatively, set these to `None` to disable initialising the PayFast
`name_first` and `name_last` fields from the user.

Usage
=====

Payment form
------------

payfast.forms.PayFastForm can be used to construct the html form. It is
a helper form for html output and it shouldn't perform any validation.

Pass all the fields to form 'initial' argument. Form also has an optional
'user' parameter: it is the User instance the order is purchased by. If
'user' is specified, 'name_first', 'name_last' and 'email_address' fields
will be filled automatically if they are not passed with 'initial'.

Example::

    # views.py

    from django.shortcuts import get_object_or_404
    from django.views.generic.simple import direct_to_template
    from django.contrib.auth.decorators import login_required

    from payfast.forms import PayFastForm

    @login_required
    def pay_with_payfast(request, order_id):

        # Order model have to be defined by user, it is not a part
        # of django-payfast
        order = get_object_or_404(Order, pk = order_id)

        form = PayFastForm(initial={
            # required params:
            'amount': order.total,
            'item_name': 'the name of the item being charged for',

            # optional params:
            # 'return_url' : 'http://my-site.com/orders/payfast/return/',
            # 'cancel_url' : 'http://my-site.com/orders/payfast/cancel/'
            # ... etc.
        }, user=order.user)

        return direct_to_template(request, 'pay_with_payfast.html', {'form': form})

Please refer to PayFast docs (http://www.payfast.co.za/c/std/website-payments-variables)
for more options. 'merchant_id', 'merchant_key', 'notify_url' and
'signature' params are handled automatically.


The template::

    {% extends 'base.html' %}

    {% block content %}
        <form action="{{ form.target }}" method="POST">
            <p>{{ form.as_p }}</p>
            <p><input type="submit" value="Buy Now"></p>
        </form>
    {% endblock %}

The {{ form.as_p }} output will be a number of ``<input type='hidden'>`` tags.

PayFastForm has a 'target' attribute with PayFast server URL.

Please note that it's up to you to implement the order processing logic.
Order handling should be performed in ``payfast.signals.data`` signal handler.

``payfast.signals.notify`` signal
---------------------------------

When PayFast posts data to the Notify URL ``payfast.signals.notify`` signal
is sent. This signal won't be sent for suspicious data (when request is
coming from untrusted ip, form validation fails or the payment is duplicate).

Signal subscribers will get an 'order' argument with ``PayFastOrder`` instance.

Example::

    import payfast.signals

    def notify_handler(sender, **kwargs):
        payfast_order = kwargs['order']

        if payfast_order.payment_status == 'COMPLETE':

            # The order is paid (merchant_id check and check for duplicate
            # payments is already handled by django-payfast)

            amount = payfast_order.amount
            # your business logic
            # ...
        else: # the order is not paid
            # your business logic
            # ...

    payfast.signals.notify.connect(notify_handler)


urls.py
-------

In order to get Notify URL up and running, include payfast.urls in your urls.py::

    urlpatterns = patterns('',
        #...
        url(r'^payfast/', include('payfast.urls')),
        #...
    )
