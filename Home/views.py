from urllib import request
from django.shortcuts import render

from product.models import Products 
from brand.models import brand
# Create your views here.
from django.contrib.auth.decorators import user_passes_test
from product.models import Banner




def home(request):
    banner_image=Banner.objects.all()
    data=Products.objects.all().filter(available=True)[:6]
    for i in data:
        if i.offer_product or i.category.offer:
            get=i.offer_price()
            print('get',get)
    brandnew=brand.objects.all()[:6]
    context={
        "data":data,
        "banner_image":banner_image,
        'brand':brandnew,
        "offer":get
    }
    return render(request,"User\home.html",context)