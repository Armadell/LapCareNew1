
from django.utils import timezone
from tkinter import CASCADE
from django.db import models
import uuid
from django.apps import apps
from django.urls import reverse
# Create your models here.
from django.db.models.aggregates import Sum
from unicodedata import category
from django.db import models
from brand.models import brand
from category.models import category



class Products(models.Model):
    product_name=models.CharField(max_length=200,unique=True)
    slug=models.SlugField(max_length=200,unique=True)
    price=models.FloatField()
    stock=models.IntegerField()
    available=models.BooleanField(default=True)
    offer_product = models.FloatField(max_length=None,blank=True,default=0)
    offerstatuspro=models.BooleanField(default=False)
    is_delete=models.BooleanField(default=True)
    description=models.TextField(blank=True)
    images=models.ImageField( upload_to='photos/products', height_field=None, width_field=None, max_length=None)
    
    images2=models.ImageField( upload_to='photos/products', height_field=None, width_field=None, max_length=None)
   
    images3=models.ImageField( upload_to='photos/products', height_field=None, width_field=None, max_length=None)
    
    images4=models.ImageField( upload_to='photos/products', height_field=None, width_field=None, max_length=None)
   
    newbrand=models.ForeignKey(brand,on_delete=models.CASCADE)
    category=models.ForeignKey(category,on_delete=models.CASCADE)
    
    created_date=models.DateField(auto_now_add=True)
    modified_date=models.DateField(auto_now=True)
   
    def __str__(self):
        return self.product_name 
    class Meta:
        
        verbose_name = 'product'
        verbose_name_plural = 'products'
    def get_url(self):
        return reverse("single_product_view",args=[self.category.slug,self.slug])
    def offer_price(self):

        if self.category.offerstatus == True and self.offerstatuspro == True:
            if self.offer_product:
                if self.category.offer > self.offer_product:
                    return self.price - self.price *(self.category.offer/100)

                else:
                    return self.price - self.price*(self.offer_product/100)
                
            else:
                return self.price - self.price *(self.category.offer/100)

        elif self.category.offerstatus == False and self.offerstatuspro == True:
            
            return self.price - self.price *(self.offer_product/100)

        elif self.category.offerstatus == True and self.offerstatuspro == False:
            return self.price - self.price *(self.category.offer/100)

        else:
            return self.price
    
    def discount_price(self):

        if self.category.offerstatus == True and self.offerstatuspro == True:
            if self.offer_product:
                if self.category.offer > self.offer_product:
                    return self.price *(self.category.offer/100)

                else:
                    return  self.price*(self.offer_product/100)
                
            else:
                return self.price *(self.category.offer/100)

        elif self.category.offerstatus == False and self.offerstatuspro == True:
            
            return  self.price*(self.offer_product/100)
                

        elif self.category.offerstatus == True and self.offerstatuspro == False:
            return self.price *(self.category.offer/100)
        else:
            return "No offer available"
   


        

  
class VariationManager(models.Manager):
    def RAM(self):
        return super(VariationManager,self).filter(variation_category='RAM',is_active=True)
    def Processor(self):
        return super(VariationManager,self).filter(variation_category='Processor',is_active=True)
    def generation(self):
        return super(VariationManager,self).filter(variation_category='generation',is_active=True)
    

variation_category_choice=(
    ('RAM','RAM'),
    ('Processor','Processor'),
    ('generation','generation'),
)
class Variation(models.Model):
    product=models.ForeignKey(Products,on_delete=models.CASCADE)
    variation_category=models.CharField(max_length=100,choices=variation_category_choice)
    variation_value=models.CharField(max_length=100)
    is_active=models.BooleanField(default=True)
    created_date=models.DateTimeField(auto_now=True)
    objects=VariationManager()
    def __str__(self):
        return self.variation_value
class Banner(models.Model):
    banner_image=models.ImageField(upload_to='banner/banner_image',blank=True)
