from email.policy import default
from wsgiref.util import request_uri
from django.db import models
from django.urls import reverse

import uuid
# Create your models here.
class category(models.Model):
    category_name=models.CharField(max_length=200,unique=True)
    slug=models.CharField(max_length=200,unique=True)#adding default value
    is_delete=models.BooleanField(default=True,blank=True)
    offer = models.IntegerField(max_length=None,default=0,null=True)
    offerstatus=models.BooleanField(default=False)
    #to remove integrity error
   
    
    class Meta:
        
        verbose_name = 'category'
        verbose_name_plural = 'categories'
    def get_url(self):
          return reverse("market_by_category",args=[self.slug])
    def __str__(self):
        return self.category_name
