from django import forms


class PropertySearchForm(forms.Form):

    location = forms.CharField(
        required=False,
        label="Location"
    )

    semantic_query = forms.CharField(
        required=False,
        label="Describe what you are looking for",
        help_text="Try: quiet family home near schools",
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