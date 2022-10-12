from tkinter.tix import Select
from .models import Products
from django.forms import ModelForm,Select, Textarea,TextInput,CheckboxInput, NumberInput,ClearableFileInput,ModelChoiceField


class ProductsForm(ModelForm):
    class Meta:
        model = Products
        fields = ['product_name','price','stock','description','available','images','images2','images3','images4','newbrand','category']
        widgets = {
            "product_name": TextInput(
                attrs={
                    "class": "form-control",
                    "style": "width:80%",
                    "placeholder": "Product name",
                }
            ),
            "price": NumberInput(attrs={"class": "form-control","style":"color:white;width:80%;"}),
            "stock": NumberInput(attrs={"class": "form-control","style":"color:white;width:80%;"}),
            "description":Textarea(attrs={"class": "form-control","style":"color:white;width:80%;height:40%;"}),
            "available": CheckboxInput(attrs={"class": "form-check","style":"color:white;"}),
            "images": ClearableFileInput(
                attrs={
                    "class": "form-control-file",
                    "style": "width:80%"
                }
            ),
             "images2": ClearableFileInput(
                attrs={
                    "class": "form-control-file",
                    "style": "width:80%"
                }
            ),
             "images3": ClearableFileInput(
                attrs={
                    "class": "form-control-file",
                    "style": "width:80%"
                }
            ),
             "images4": ClearableFileInput(
                attrs={
                    "class": "form-control-file",
                    "style": "width:80%"
                }
            ),
            
            "newbrand":Select(
                
                 attrs={
                    "class": "form-control",
                    "style":"color:white;width:80%"
                 }
            ),
              "category":Select(
                
                 attrs={
                    "class": "form-control",
                    "style":"color:white;width:80%;"
                 }
            )
        }
