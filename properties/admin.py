from django.contrib import admin
from django.utils.html import format_html

from .models import Location, Property, PropertyImage


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "city",
        "country",
        "is_active",
    )

    search_fields = (
        "name",
        "city",
        "country",
        "address",
    )

    list_filter = (
        "country",
        "city",
        "is_active",
    )


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "property_type",
        "listing_type",
        "price",
        "bedrooms",
        "is_featured",
        "is_active",
    )

    list_filter = (
        "property_type",
        "listing_type",
        "is_featured",
        "is_active",
    )

    search_fields = (
        "title",
        "description",
        "location__city",
    )

    inlines = [
        PropertyImageInline
    ]


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):

    list_display = (
        "property",
        "image_preview",
        "is_primary",
    )


    def image_preview(self, obj):

        if obj.image:
            return format_html(
                '<img src="{}" width="120"/>',
                obj.image.url
            )

        return "No image"