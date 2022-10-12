from turtle import textinput
from . models import brand
from django.forms import ModelForm,TextInput,ClearableFileInput
 


class brandForm(ModelForm):
    class Meta:
        model=brand
        fields=['brand_name','brand_image']
        widgets={
            'brand_name':TextInput(attrs={
             "class":"form-control",
             
             "style":"width:80%",
             "placeholder":"brand name",
            }),
            'brand_image':ClearableFileInput(attrs={
                "class":"form-control-file",
                "style":"width:80%",
                
                
            })
            
        }