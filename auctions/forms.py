from django import forms
from .models import Listing, Bid, Comment


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


class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ["amount"]

        widgets = {
            "amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Enter your bid"})
        }
        labels = {
            "amount": "Your Bid ($)"
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(attrs={"class": "form-control", "rows":8, "placeholder": "Enter a comment"}),
        }