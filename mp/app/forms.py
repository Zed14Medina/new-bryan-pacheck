from django import forms
from .models import Product, Category, Order
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

class CheckoutForm(forms.ModelForm):
    shipping_address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your complete shipping address'}),
        required=True
    )
    payment_method = forms.ChoiceField(
        choices=[('COD', 'Cash on Delivery'), ('GCASH', 'GCASH')],
        required=True,
        widget=forms.RadioSelect
    )

    class Meta:
        model = Order
        fields = ['shipping_address', 'payment_method']

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=[('Buyer', 'Buyer'), ('Seller', 'Seller')], required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user