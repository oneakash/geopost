from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator

from .models import Property
from .forms import PropertySearchForm

def home(request):

    featured = Property.objects.filter(
        is_featured=True,
        is_active=True
    )[:6]


    return render(
        request,
        "properties/home.html",
        {
            "featured": featured
        }
    )



def property_list(request):

    properties = Property.objects.filter(
        is_active=True
    )


    form = PropertySearchForm(
        request.GET
    )


    if form.is_valid():

        location = form.cleaned_data.get(
            "location"
        )

        if location:
            properties = properties.filter(
                location__city__icontains=location
            )


        min_price = form.cleaned_data.get(
            "min_price"
        )

        if min_price:
            properties = properties.filter(
                price__gte=min_price
            )


        max_price = form.cleaned_data.get(
            "max_price"
        )

        if max_price:
            properties = properties.filter(
                price__lte=max_price
            )


        bedrooms = form.cleaned_data.get(
            "bedrooms"
        )

        if bedrooms:
            properties = properties.filter(
                bedrooms__gte=bedrooms
            )


    paginator = Paginator(
        properties,
        6
    )


    page = request.GET.get(
        "page"
    )

    properties = paginator.get_page(
        page
    )


    return render(
        request,
        "properties/property_list.html",
        {
            "properties": properties,
            "form": form
        }
    )



def property_detail(request, pk):

    property_obj = get_object_or_404(
        Property,
        pk=pk
    )


    return render(
        request,
        "properties/property_detail.html",
        {
            "property": property_obj
        }
    )