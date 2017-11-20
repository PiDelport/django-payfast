from django.contrib import admin
from payfast.models import PayFastOrder


class PayFastOrderAdmin(admin.ModelAdmin):

    list_display = ['m_payment_id', 'pf_payment_id', 'user', 'created_at', 'amount_gross',
                    'payment_status', 'item_name', 'trusted']
    list_filter = ['trusted', 'payment_status']
    search_fields = ['m_payment_id', 'pf_payment_id', 'item_name',
                     'user__username', 'name_first', 'name_last', 'email_address']
    raw_id_fields = ['user']
    date_hierarchy = 'created_at'


admin.site.register(PayFastOrder, PayFastOrderAdmin)
