from django import forms
from .models import Product, Category
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock_quantity', 'category', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'stock_quantity': forms.NumberInput(attrs={'min': '0'}),
        }

class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True)
    payment_method = forms.ChoiceField(choices=[
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('cash_on_delivery', 'Cash on Delivery')
    ])

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email', 'id': 'email'}))
    role = forms.ChoiceField(
        choices=[('Buyer', 'Buyer'), ('Seller', 'Seller')],
        widget=forms.Select(attrs={'id': 'role'})
    )
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username', 'id': 'username'}),
            'password1': forms.PasswordInput(attrs={'placeholder': 'Password', 'id': 'password1'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'id': 'password2'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the default help text from UserCreationForm
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None