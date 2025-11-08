from django import forms
from prefixed_textinput import PrefixedTextInput


class BookAdminForm(forms.ModelForm):
    class Meta:
        widgets = {
            'product_code':
                PrefixedTextInput(prefix='SKU'),
            'isbn_code':
                PrefixedTextInput(prefix='ISBN'),
        }
        fields = '__all__'
