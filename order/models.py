from email.policy import default
from django.db import models
from accounts.models import Account
from product.models import Products, Variation

# Create your models here.
STATUS1 = (
    ("New", "New"),
    ("Placed", "Placed"),
    ("Shipped", "Shipped"),
    ("Accepted", "Accepted"),
    ("Delivered", "Delivered"),
    ("Canceled", "Canceled"),
    ("Pending", "Pending"),
)

class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100,blank=True)
    payment_method = models.CharField(max_length=100,blank=True)
    amount_paid = models.CharField(max_length=100,blank=True)
    status = models.CharField(max_length=100,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_method


class Order(models.Model):
    STATUS = (
        ("New", "New"),
        ("Accepted", "Accepted"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    )
    methods_payment = (
        ("Paypal", "Paypal"),
        ("Rasopay", "Rasopay"),
        ("Cod", "Cash on delivery"),
       
    )

    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(
        Payment, on_delete=models.SET_NULL, blank=True, null=True
    )
   
    final_discount =models.IntegerField(blank=True,null=True)
    discountnew=models.IntegerField(default=0,null=True,blank=True)
    order_number = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    pincode = models.IntegerField()
    order_note = models.CharField(max_length=100, blank=True)
    order_total = models.FloatField()
    tax = models.FloatField()
    order_cancel=models.BooleanField(default=False,blank=True)
    status = models.CharField(max_length=50, choices=STATUS, default="New")
  
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"#it is used to get the full name

    def full_address(self):
        return f"{self.address_line_1}{self.address_line_2}"


    def __str__(self):
        return self.first_name


class OrderProduct(models.Model):
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(
        Payment, on_delete=models.SET_NULL, blank=True, null=True
    )
    user = models.ForeignKey(Account, on_delete=models.CASCADE,null=True)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS1, default="New")
    variations = models.ManyToManyField(Variation, blank=True)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    orderproduct_cancel = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    return_status=models.BooleanField(default=True,blank=True,null=True)

    def __str__(self):
        return self.product.product_name