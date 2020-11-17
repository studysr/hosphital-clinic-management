from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.views import generic
from django.utils import timezone
from .models import *
from django.http import JsonResponse,HttpResponseRedirect
from django.urls import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.contrib import messages
from django.db.models import Sum
import json

import random
import string

def create_ref_code():
	return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))



def Dashboard(request):
	pay=Payment.objects.all()
	count_pay=len(pay)		#to get sum of data row or quantity

	total_after_di=Payment.objects.all().aggregate(s=Sum('total_after_discount'))['s']
	if total_after_di==None:
		total_after_di=0

	total_after_disc=round(float(total_after_di),2)


	amount_pa=Payment.objects.all().aggregate(s=Sum('amount_paid'))['s']
	if amount_pa==None:
		amount_pa=0

	amount_paids=round(float(amount_pa),2)


	second_paids=Payment.objects.all().aggregate(s=Sum('due_paid'))['s']
	if second_paids==None:
		second_paids=0
	
	total_paid= amount_paids + second_paids

	balance = total_after_disc - amount_paids - second_paids


	return render(request, "pathology/dashboard.html", {
		'count_pay':count_pay, 
		'pay':pay, 
		'total_paids':total_paid, 
		'total_after_disc':total_after_disc, 
		'balance':balance 
		})



def TestBill(request):

	consumers=Consumer.objects.all()[:20]
	product=Item.objects.all()
	Refer=Referred.objects.all()

	obj= Consumer.objects.filter().order_by('-id')[0]


	if request.method == "POST":
		name= request.POST.get('name')
		address = request.POST.get('address')

		consums = Consumer.objects.filter(name=name, address = address).first()
		if consums is None:
			consums = Consumer.objects.create(name=name, address = address)
			return redirect('testbill')
		else:
			return render(request, 'pathology/test_bill.html', {'msg':"Already This name exists"})
	else:
		return render(request, 'pathology/test_bill.html', {'obj':obj, 'consumers':consumers,'product':product, 'Refer':Refer})
		

def OrderItemSave(request):
	#get data from json field
	saledata=request.GET['saledata']
	consumer=request.GET['consumer']
	address=request.GET['address']
	age=request.GET['age']
	mobile=request.GET['mobile']
	gender=request.GET['gender']
	referredby=request.GET['referredby']


	#load data from json file
	sale_data=json.loads(saledata)
	consumer_name=json.loads(consumer)['name']
	consumer_address=json.loads(address)['address']
	consumer_age=json.loads(age)['age']
	consumer_mobile=json.loads(mobile)['mobile']
	consumer_gender=json.loads(gender)['gender']
	consumer_referredby=json.loads(referredby)['referredby']


	refe=Referred.objects.get(name=consumer_referredby)

	#Get Consumer data from input or save if not exists.
	try:
		Consumer.objects.get(name=consumer_name)
	except:
		consum_table=Consumer()
		consum_table.name=consumer_name
		consum_table.address=consumer_address
		consum_table.age=consumer_age
		consum_table.mobile=consumer_mobile
		consum_table.gender=consumer_gender
		consum_table.ReferredBy=refe
		consum_table.save()

	#OrderItem Tabele Save:
	sel_consumer=Consumer.objects.get(name=consumer_name)
	for data in sale_data:
		product_name=data['product']
		product_quantity=int(data['quantity'])

		productname=Item.objects.get(title=product_name)
		productvalue=product_quantity*(float(productname.price))

		itm=OrderItem()
		itm.name=sel_consumer
		itm.quantity=product_quantity
		itm.item=productname
		itm.value=productvalue
		itm.save()

	#Order Table save
	ordered_date = timezone.now()
	order_name2 = OrderItem.objects.filter(name=sel_consumer)
	order_ids = []
	for x in order_name2:
		order_ids.append(x.id)
	
	order = Order.objects.create(name=sel_consumer, ordered_date=ordered_date)
	for x in order_ids:
		order.items.add(OrderItem.objects.get(id=x))

	return JsonResponse({'status':'ok'})
	



def remove_last_orderitem(request):
	obj= Consumer.objects.filter().order_by('-id')[0]
	odel=OrderItem.objects.filter(name=obj.id, ordered=False).delete()
	
	Consumer.objects.filter().order_by('-id')[0].delete()

	return redirect("testbill")




# show summary of orderitem
class OrderSummary(View):
	def get(self, *args, **kwargs):
		try:
			obj= Consumer.objects.filter().order_by('-id')[0]
			order = Order.objects.get(name=obj.id, ordered=False)
			ref = Referred.objects.all()
			context = {
			'object':order,
			'obj':obj,
			'ref': ref,
			}
			return render(self.request, "pathology/order_summary.html", context)

		except ObjectDoesNotExist:
			return render(self.request,'pathology/order_summary.html', {'msg':"কোন অর্ডার নেই।"})




# ----payment submit-----
class PaymentView(View):
	def get(self, *args, **kwargs):
		pass
	def post(self, *args, **kwargs):
		try:
			nam_id= self.request.POST.get('serial_id')
			obj= Consumer.objects.get(id=nam_id)
			order = Order.objects.get(name=obj.id, ordered=False)
			if self.request.method == "POST":
				#get from templete form
				name = obj
				ref_by = self.request.POST.get("ref_by")
				refer = Referred.objects.get(id=ref_by) # যেহেতু এটি ForigenKey তাই মডেল কল।
				sub_total = self.request.POST.get("sub_total")
				others_charge = self.request.POST.get("other_charge")
				discount_percent = self.request.POST.get("discount_percent")
				discount_amount = (float(discount_percent) * (float(sub_total)+float(others_charge)))/(100)
				total_amount = self.request.POST.get("sub_total")
				amount_paid = self.request.POST.get("amount_paid")
				balance = self.request.POST.get("total")

				#Create the payment
				pay = Payment()
				pay.name = name
				pay.charge_id = create_ref_code()
				pay.ref_by = refer
				pay.sub_total = sub_total
				pay.others_charge = others_charge
				pay.discount_amount = discount_amount
				pay.total_before_discount = (float(balance) + float(amount_paid)) + discount_amount
				pay.total_after_discount = (float(balance) + float(amount_paid))
				pay.amount_paid = amount_paid
				pay.balance = balance
				pay.comission = (float(refer.comission_percent) * float(pay.total_after_discount)/(100))
				pay.total_after_comission = pay.total_after_discount - pay.comission
				pay.save()

				#assign the payment to the order
				order_items = order.items.all()
				order_items.update(ordered=True)
				for item in order_items:
					item.save()

				order.ordered = True
				order.payment = pay
				order.ref_code = create_ref_code()
				order.save()
				return redirect("test_bill_print", pay.id) #pay.id is pk argument after saving payment data.
			else:
				return redirect("testbill")

		except ObjectDoesNotExist:
			return render(self.request,'pathology/order_summary.html', {'msg':"পূর্বে এই বিল পরিশোধ করা হয়েছে।"})



#----test bill print view----
def test_bill_print(request, pk):
	try:
		paypdf=Payment.objects.get(id=pk)
		obj= Consumer.objects.filter().order_by('-id')[0]
		order = Order.objects.get(name=obj.id, ordered=True)
		dict={
				'object':order,
				'pk':paypdf.id,
				'name': obj.name,
				'age': obj.age,
				'mobile': obj.mobile,
				'ReferredBy':obj.ReferredBy,
				'charge_id': paypdf.charge_id,
				'sub_total': paypdf.sub_total,
				'others_charge': paypdf.others_charge,
				'discount_amount': paypdf.discount_amount,
				'total_before_discount': paypdf.total_before_discount,
				'total_after_discount': paypdf.total_after_discount,
				'amount_paid': paypdf.amount_paid,
				'balance': paypdf.balance,
				'due_paid': paypdf.due_paid,
				'timestamp': paypdf.timestamp,
				'obj':obj
		    }
		return render(request, 'pathology/show_bill.html', dict)

	except MultipleObjectsReturned:
		return render(request, 'pathology/order_summary.html', {'msg':"এই নামে একাধিক বিল পরিশোধ করা হয়নি।"})



#--------------for bill (pdf) download and printing-----------
import io
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return



def download_testbill_pdf_view(request, pk):
    paypdf=Payment.objects.get(id=pk)
    con=Consumer.objects.all().filter().order_by('-id')[0]
 
    dict={
		'name': con.name,
		'charge_id': paypdf.charge_id,
		'sub_total': paypdf.sub_total,
		'others_charge': paypdf.others_charge,
		'discount_amount': paypdf.discount_amount,
		'total_before_discount': paypdf.total_before_discount,
		'total_after_discount': paypdf.total_after_discount,
		'amount_paid': paypdf.amount_paid,
		'balance': paypdf.balance,
		'timestamp': paypdf.timestamp
    }
    return render_to_pdf('pathology/download_testbill_pdf.html',dict)
#--------------end bill (pdf) download and printing-----------



def payment_list_search(request):
	if request.method=="GET":
		fromdate=request.GET['fromdate_payment']
		todate=request.GET['todate_payment']
		pay=Payment.objects.filter(timestamp__range=[fromdate,todate])

		count_pay=len(pay)		#to get sum of data row or quantity

		total_after_di=pay.aggregate(s=Sum('total_after_discount'))['s']
		if total_after_di==None:
			total_after_di=0

		total_after_disc=round(float(total_after_di),2)

		amount_pa=pay.aggregate(s=Sum('amount_paid'))['s']
		if amount_pa==None:
			amount_pa=0

		amount_paids=round(float(amount_pa),2)
		balance = total_after_disc - amount_paids

		context={
			'count_pay':count_pay, 
			'pay':pay, 
			'amount_paids':amount_paids, 
			'total_after_disc':total_after_disc, 
			'balance':balance,
			'fromdate':fromdate,
			'todate':todate,

			}

		if 'list' in request.GET:
			return render(request, "pathology/lazer_report.html", context)
		elif 'search' in request.GET:
			return render(request, "pathology/dashboard.html", context)



def update(request):
	if request.method=="GET":
		search_id = request.GET.get('search_id')
		updatepay=Payment.objects.filter(id=search_id)

	return render(request, 'pathology/update.html', {'updatepay':updatepay})


def due_payment(request, pk):
	if request.method == "POST":
		payf=Payment.objects.get(id=pk)
		due=request.POST.get('due_bal')
		add_pay=request.POST.get('add_pay')
		new_blance=float(due)-float(add_pay)
		total_due_pay= float(add_pay) + float(payf.due_paid)

		Payment.objects.filter(id=payf.id).update(balance=new_blance, due_paid=total_due_pay)

		return redirect("test_bill_print", payf.id)

	try:
		paypdf=Payment.objects.get(id=pk)
		obj= Consumer.objects.get(name=paypdf.name)
		order = Order.objects.get(name=obj.id, ordered=True)
		dict={
				'object':order,
				'pk':paypdf.id,
				'name': obj.name,
				'charge_id': paypdf.charge_id,
				'sub_total': paypdf.sub_total,
				'others_charge': paypdf.others_charge,
				'discount_amount': paypdf.discount_amount,
				'total_before_discount': paypdf.total_before_discount,
				'total_after_discount': paypdf.total_after_discount,
				'amount_paid': paypdf.amount_paid,
				'balance': paypdf.balance,
				'due_paid': paypdf.due_paid,
				'timestamp': paypdf.timestamp,
				'obj':obj
		    }
	
		return render(request, 'pathology/due_payment.html', dict)

	except MultipleObjectsReturned:
		return render(request, 'pathology/order_summary.html', {'msg':"এই নামে একাধিক বিল পরিশোধ করা হয়নি।"})





def overview(request):
	pay=Payment.objects.all()
	count_pay=len(pay)

	total_after_di=pay.aggregate(s=Sum('total_after_discount'))['s']
	if total_after_di==None:
		total_after_di=0

	total_after_disc=round(float(total_after_di),2)

	return render(request, 'pathology/overview.html', {'count_pay':count_pay, 'total_after_disc':total_after_disc})