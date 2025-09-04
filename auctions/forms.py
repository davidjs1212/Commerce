from django import forms
from .models import Listing


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "description", "starting_bid", "photo", "category"]

        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter a title"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows":8, "placeholder": "Enter a description"}),
            "starting_bid": forms.NumberInput(attrs={"class": "form-control", "step": "0.01","placeholder": "$0.00"}),
            "photo": forms.URLInput(attrs={"class": "form-control", "placeholder": "Optional"}),
            "category": forms.TextInput(attrs={"class": "form-control", "placeholder": "Optional"}),
        }