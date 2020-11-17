from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
	path('dashboard/',views.Dashboard, name='dashboard'),
    path('',views.TestBill, name='testbill'),
    path('order_summary', views.OrderSummary.as_view(), name='order_summary'),
    path('payment', views.PaymentView.as_view(), name='payment'),
    path('orderitem_save',views.OrderItemSave,name='orderitem_save'),
    path('download-testbill-pdf/<int:pk>', views.download_testbill_pdf_view,name='download-testbill-pdf'),
    path('test_bill_print/<int:pk>', views.test_bill_print,name='test_bill_print'),
    path('remove_last_orderitem', views.remove_last_orderitem,name='remove_last_orderitem'),
	path('payment_list_search', views.payment_list_search,name='payment_list_search'),
	path('update', views.update,name='update'),
	path('due_payment/<int:pk>', views.due_payment,name='due_payment'),
    path('overview/', views.overview,name='overview'),
]