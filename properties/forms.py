from django import forms


class PropertySearchForm(forms.Form):

    location = forms.CharField(
        required=False,
        label="Search location"
    )

    min_price = forms.IntegerField(
        required=False
    )

    max_price = forms.IntegerField(
        required=False
    )

    bedrooms = forms.IntegerField(
        required=False
    )