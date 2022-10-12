from dataclasses import fields
from socket import fromshare
from .models import category
from django.forms import ModelForm,TextInput
class categoryForm(ModelForm):
    class Meta:
        model=category
        fields=["category_name"]
        widgets = {
            'category_name': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 80%;',
                'placeholder': 'category name'
                })}