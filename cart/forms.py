from django import forms

class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1, 
        max_value=20,
        label='Quantity',
        widget=forms.NumberInput(attrs={'class': 'quantity-input'})
    )
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)