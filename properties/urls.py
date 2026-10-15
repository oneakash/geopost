from django.urls import path

from . import views


urlpatterns = [

    path(
        "",
        views.home,
        name="home"
    ),

    path(
        "properties/",
        views.property_list,
        name="property_list"
    ),

    path(
        "property/<int:pk>/",
        views.property_detail,
        name="property_detail"
    ),

    path(
        "api/locations/autocomplete/",
        views.location_autocomplete,
        name="location_autocomplete"
    ),

]