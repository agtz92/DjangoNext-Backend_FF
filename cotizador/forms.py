from django import forms
from .models import Customer, Product, Order, OrderItem, Company

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'phone', 'company']  # Include the company field
        widgets = {
            'id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter customer ID'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter customer name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'company': forms.Select(attrs={'class': 'form-control'}),  
        }
        labels = {
            'id': 'Customer ID',
            'name': 'Customer Name',
            'email': 'Email Address',
            'phone': 'Phone Number',
            'company': 'Company',
        }
        
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'sku', 'base_price']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer']


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'business_line', 'state']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter company name'}),
            'business_line': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter business line'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter state'}),
        }