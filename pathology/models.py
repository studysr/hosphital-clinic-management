from django.db import models
# Create your models her


CATEGORY_CHOICES = (
	('B', 'Blood'),
	('U', 'Urine'),
	('S', 'Self')
)

class Referred(models.Model):
	name = models.CharField(max_length=200, null = True, blank = True)
	designation = models.CharField(max_length=150, null=True, blank = True)
	address = models.CharField(max_length=50, null = True, blank = True)
	mobile =models.CharField(max_length=12)
	comission_percent=models.IntegerField(default=0)

	def __str__(self):
		return self.name



class Consumer(models.Model):
	name = models.CharField(max_length=30)
	address = models.CharField(max_length=50)
	age = models.CharField(max_length=6, null=True, blank=True)
	gender = models.CharField(max_length=6, null=True, blank=True)
	mobile = models.CharField(max_length=11, null=True, blank=True)
	ReferredBy = models.ForeignKey(Referred, on_delete=models.CASCADE, blank=True, null=True)

	def __str__(self):
		return self.name


class Item(models.Model):
	title = models.CharField(max_length=100)
	description = models.TextField()
	category = models.CharField(choices=CATEGORY_CHOICES, max_length=100)
	price = models.FloatField()
	slug = models.SlugField()
	

	def __str__(self):
		return f"{self.title}-{self.description}--{self.price}"


class OrderItem(models.Model):
	name = models.ForeignKey(Consumer, on_delete=models.CASCADE)
	ordered = models.BooleanField(default=False)
	item = models.ForeignKey(Item, on_delete=models.CASCADE)
	quantity = models.IntegerField(default=1)
	value= models.FloatField()

	def __str__(self):
		return f"{self.quantity} of {self.item.title} by {self.name.name}"


	def get_total_item_price(self):
		return self.value








class Order(models.Model):
	name = models.ForeignKey(Consumer, on_delete=models.CASCADE)
	ref_code = models.CharField(max_length=20, blank=True, null=True)
	items = models.ManyToManyField(OrderItem)
	start_date = models.DateTimeField(auto_now_add=True)
	ordered_date = models.DateTimeField()
	ordered = models.BooleanField(default=False)
	payment = models.ForeignKey('Payment', on_delete=models.CASCADE, blank=True, null=True)

	def __str__(self): 
		return self.name.name


	def get_total(self):
		total = 0
		for order_item in self.items.all():
			total += order_item.value
		return total



class Payment(models.Model):
	name = models.ForeignKey(Consumer, on_delete=models.CASCADE, blank=True, null=True)
	charge_id = models.CharField(max_length=50, blank=True, null=True)
	sub_total = models.FloatField(default=0)
	others_charge= models.FloatField(default=0)
	discount_amount = models.FloatField(default=0)
	total_before_discount = models.FloatField(default=0)
	total_after_discount = models.FloatField(default=0)
	amount_paid = models.FloatField(default=0)
	balance = models.FloatField(default=0)
	ref_by = models.ForeignKey(Referred, on_delete=models.CASCADE, blank=True, null=True)
	comission = models.FloatField(default=0)
	total_after_comission = models.FloatField(default=0)
	timestamp = models.DateTimeField(auto_now_add=True)
	due_paid = models.FloatField(default=0)
	duepaytimestamp = models.DateTimeField(auto_now=True, blank=True)

	def __str__(self): 
		return f"{self.amount_paid} Tk paid by {self.name.name} balance {self.balance} Tk"
