from email.policy import default
from django.db import models
from product.models import Products,Variation
from accounts.models import Account

class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id



class CartItem(models.Model):
    user=models.ForeignKey(Account,on_delete=models.CASCADE,null=True)#to assign the 
    # cart item to the logged in user we create this field
    product = models.ForeignKey(Products, on_delete=models.CASCADE) 
    variations=models.ManyToManyField(Variation,blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    def sub_total(self):
        return self.product.price*self.quantity
    def __unicode__(self):
        return self.product

class Coupon(models.Model):
    coupon_code = models.CharField(max_length=10,blank=True,unique=True)
    discount    = models.FloatField()
    is_active   =   models.BooleanField(default=True)
    # coupon_apply_once_status=models.BooleanField(default=False)
    

class UsedCoupon(models.Model):
    user        =   models.ForeignKey(Account,on_delete=models.CASCADE, null=True)
    coupon        =   models.ForeignKey(Coupon,on_delete=models.CASCADE, null=True)

class coupon_repeated_check(models.Model):
    user_name=models.ForeignKey(Account,on_delete=models.CASCADE,null=True)
    is_repeated=models.BooleanField(default=False)
    coupon_name=models.CharField(max_length=100,null=True)
 