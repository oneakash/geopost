from django.core.paginator import Paginator
from django.contrib.gis.db.models.functions import Distance
from pgvector.django import CosineDistance
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from .forms import PropertySearchForm
from .models import Location, Property
from .semantic import embed_text


def home(request):
    featured = Property.objects.filter(
        is_featured=True,
        is_active=True,
    ).prefetch_related("images")[:6]

    return render(
        request,
        "properties/home.html",
        {"featured": featured},
    )


def property_list(request):
    properties = Property.objects.filter(
        is_active=True,
        is_available=True,
    ).select_related(
        "location",
    ).prefetch_related(
        "images",
    )

    form = PropertySearchForm(request.GET or None)
    semantic_search_error = None

    if form.is_valid():
        location = form.cleaned_data.get("location")
        if location:
            properties = properties.filter(
                Q(location__city__icontains=location)
                | Q(location__address__icontains=location)
            )

        min_price = form.cleaned_data.get("min_price")
        if min_price is not None:
            properties = properties.filter(price__gte=min_price)

        max_price = form.cleaned_data.get("max_price")
        if max_price is not None:
            properties = properties.filter(price__lte=max_price)

        bedrooms = form.cleaned_data.get("bedrooms")
        if bedrooms is not None:
            properties = properties.filter(bedrooms__gte=bedrooms)

        semantic_query = form.cleaned_data.get("semantic_query")
        if semantic_query:
            try:
                query_embedding = embed_text(semantic_query)
                properties = properties.annotate(
                    semantic_distance=CosineDistance("location__embedding", query_embedding)
                ).filter(
                    location__embedding__isnull=False,
                ).order_by("semantic_distance", "-created_at")
            except Exception:
                semantic_search_error = "Please try again after semantic search is available."

    paginator = Paginator(properties, 6)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "properties/property_list.html",
        {
            "properties": page_obj,
            "form": form,
            "semantic_search_error": semantic_search_error,
        },
    )


def location_autocomplete(request):
    query = request.GET.get("q", "").strip()
    if len(query) < 2:
        return JsonResponse({"results": []})

    try:
        query_embedding = embed_text(query)
        locations = Location.objects.filter(
            is_active=True,
            embedding__isnull=False,
        ).annotate(
            semantic_distance=CosineDistance("embedding", query_embedding),
        ).order_by("semantic_distance", "city")[:8]
    except Exception:
        return JsonResponse(
            {"error": "Semantic search is temporarily unavailable."},
            status=503,
        )

    results = [
        {
            "id": location.id,
            "name": location.name or location.city,
            "city": location.city,
            "address": location.address,
            "country": location.country,
        }
        for location in locations
    ]
    return JsonResponse({"results": results})


def property_detail(request, pk):
    property_obj = get_object_or_404(
        Property.objects.select_related("location").prefetch_related("images"),
        pk=pk,
    )

    distance = None
    if property_obj.point and property_obj.location.coordinates:
        distance = (
            Property.objects.annotate(
                distance=Distance("point", property_obj.location.coordinates),
            ).get(pk=pk).distance
        )

    return render(
        request,
        "properties/property_detail.html",
        {"property": property_obj, "distance": distance},
    )
