from django.forms import ModelForm,TextInput,CheckboxInput,NumberInput

from .models import Coupon, UsedCoupon



class CouponForm(ModelForm):
    class Meta:
        model = Coupon
        fields = [
            'coupon_code', 'discount', 'is_active']
        widgets = {
            "coupon_code": TextInput(
                attrs={
                    "class": "form-control",
                    "style": "width:80%",
                    "placeholder": "Product name",
                }
            ),
            "is_active":CheckboxInput(
              attrs={
                "class":"form-check"
              }
            ),
              "discount":NumberInput(
              attrs={
                "class":"form-control"
              }
            )}

            
class UsedCouponForm(ModelForm):
    class Meta:
        model = UsedCoupon
        fields = [
            'user', 'coupon']



