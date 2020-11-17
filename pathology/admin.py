from django.contrib import admin

# Register your models here.

from .models import * 

class PaymentAdmin(admin.ModelAdmin):
	list_display = [
					'name',
					'total_after_discount',
					'amount_paid',
					'balance',
					'ref_by',
					'comission',
					'total_after_comission'
					]

	list_filter = ['ref_by']

	search_fields = ['name']

	"""

    fieldsets = [('Receipt', {'fields':['receipt_amount']}),]
 

    def receipt_amount(self, request):
        current_receipt_purchase_amounts = Purchase.objects.filter(receipt__id = request.id).values_list('price', flat = True)
        total_amount = sum(current_receipt_purchase_amounts)
        return total_amount
    receipt_amount.short_description = 'Receipt Amount'
"""


admin.site.register(Consumer)
admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Referred)