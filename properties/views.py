from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.gis.measure import D
from django.contrib.gis.geos import Point
from .models import Property
from .forms import PropertySearchForm
from django.contrib.gis.db.models.functions import Distance

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
        is_active=True,
        is_available=True
    ).select_related(
        "location"
    ).prefetch_related(
        "images"
    )


    form = PropertySearchForm(request.GET or None)


    if form.is_valid():

        location = form.cleaned_data.get("location")

        if location:
            properties = properties.filter(
                Q(location__city__icontains=location) |
                Q(location__address__icontains=location)
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


    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )


    return render(
        request,
        "properties/property_list.html",
        {
            "properties": page_obj,
            "form": form,
        }
    )

def property_detail(request, pk):
    property_obj = get_object_or_404(
        Property.objects.select_related("location").prefetch_related("images"),
        pk=pk
    )
    print("1. Does the property have a location?", property_obj.location)
    if property_obj.location:
        print("2. What is inside the location field?", property_obj.location.coordinates)


    distance = None # Default value

    if property_obj.point and property_obj.location.coordinates:
        # Assign the result directly to the 'distance' variable
        distance = (
            Property.objects
            .annotate(
                distance=Distance(
                    "point",
                    property_obj.location.coordinates
                )
            )
            .get(pk=pk)
            .distance
        )

    return render(
        request,
        "properties/property_detail.html",
        {
            "property": property_obj,
            "distance": distance, # This will now pass the calculated value
        }
    )


# def property_detail(request, pk):

#     property_obj = get_object_or_404(
#         Property.objects.select_related(
#             "location"
#         ).prefetch_related(
#             "images"
#         ),
#         pk=pk
#     )


#     # Distance from location center
#     distance = None


#     if (
#         property_obj.point
#         and property_obj.location.coordinates
#     ):

#         property_obj.distance = (
#             Property.objects
#             .annotate(
#                 distance=Distance(
#                     "point",
#                     property_obj.location.coordinates
#                 )
#             )
#             .get(pk=pk)
#             .distance
#         )


#     return render(
#         request,
#         "properties/property_detail.html",
#         {
#             "property": property_obj,
#             "distance": distance,
#         }
#     )