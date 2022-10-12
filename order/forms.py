from socket import fromshare
from . models import Order
from django import forms


class OrderForm(forms.ModelForm):
    class Meta:
       model=Order
       fields=['first_name','last_name','phone_number','email','address_line_1','address_line_2','country','state','city','pincode','order_note',]