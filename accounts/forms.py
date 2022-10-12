from django.forms import ModelForm,PasswordInput,CharField,ValidationError,ImageField,FileInput
from .models import Account,UserProfile


class RegistrationForm(ModelForm):
    password =CharField(
    widget=PasswordInput(attrs={"placeholder": "Enter Password"})
    )
    confirm_password =CharField(
        widget=PasswordInput(attrs={"placeholder": "Confirm Password"})
    )

    class Meta:
        model=Account
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "password",
        ]
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter last Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email Address'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise ValidationError(
                "password and confirm password does not match"
            )
class UserForm(ModelForm):
    
    class Meta:
        model=Account
        fields=['first_name','last_name','phone_number']
    def __init__(self,*args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
                self.fields[field].widget.attrs['class'] = 'form-control'
class UserProfileForm(ModelForm):
   profile_picture = ImageField(
        required=False,
        error_messages={"invalid": ("Image files only")},
        widget=FileInput,
       )
   class Meta:
        model=UserProfile
        fields=['address_line_1','address_line_2','city','state','country','profile_picture']
   def __init__(self,*args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
                self.fields[field].widget.attrs['class'] = 'form-control'