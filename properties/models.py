
from django.db import models
from django.contrib.gis.db import models as gis_models
from pgvector.django import VectorField, HnswIndex


class Location(models.Model):
    name = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=255, blank=True, db_index=True)

    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100, db_index=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default="Bangladesh")
    postal_code = models.CharField(max_length=20, blank=True)

    coordinates = gis_models.PointField(
        geography=True, srid=4326
    )
    boundary = gis_models.MultiPolygonField(
        srid=4326, null=True, blank=True
    )

    # all-MiniLM-L6-v2 produces 384-dimensional vectors
    embedding = VectorField(
        dimensions=384, null=True, blank=True
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["city", "address"]
        indexes = [
            HnswIndex(
                name="location_embedding_hnsw",
                fields=["embedding"],
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
            ),
        ]

    def __str__(self):
        return f"{self.address}, {self.city}"


class Property(models.Model):
    class PropertyType(models.TextChoices):
        APARTMENT = "apartment", "Apartment"
        HOUSE = "house", "House"
        COMMERCIAL = "commercial", "Commercial"
        LAND = "land", "Land"

    class ListingType(models.TextChoices):
        RENT = "rent", "For Rent"
        SALE = "sale", "For Sale"

    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="properties",
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True, db_index=True)
    description = models.TextField(blank=True)

    property_type = models.CharField(
        max_length=20,
        choices=PropertyType.choices,
        default=PropertyType.APARTMENT,
        db_index=True,
    )
    listing_type = models.CharField(
        max_length=10,
        choices=ListingType.choices,
        default=ListingType.RENT,
        db_index=True,
    )

    price = models.DecimalField(
        max_digits=14, decimal_places=2, db_index=True
    )
    bedrooms = models.PositiveSmallIntegerField(default=0)
    bathrooms = models.PositiveSmallIntegerField(default=0)
    area_sqft = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True,
    )

    address = models.TextField(blank=True)
    point = gis_models.PointField(
        geography=True, srid=4326, null=True, blank=True
    )
    footprint = gis_models.PolygonField(
        srid=4326, null=True, blank=True
    )

    # Reserved for property semantic search
    embedding = VectorField(
        dimensions=1536, null=True, blank=True
    )

    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)
    is_available = models.BooleanField(default=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=[
                    "listing_type",
                    "property_type",
                    "is_available",
                ],
                name="property_filter_idx",
            ),
            HnswIndex(
                name="property_embedding_hnsw",
                fields=["embedding"],
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
            ),
        ]

    def __str__(self):
        return self.title


class PropertyImage(models.Model):
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="images",
    )

    image = models.ImageField(
        upload_to="properties/%Y/%m/",
        blank=True,
    )
    # Retain compatibility with your existing URL-based images
    image_url = models.URLField(max_length=1000, blank=True)

    alt_text = models.CharField(max_length=255, blank=True)
    caption = models.TextField(blank=True)
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)

    embedding = VectorField(
        dimensions=768, null=True, blank=True
    )

    is_primary = models.BooleanField(default=False)
    display_order = models.PositiveSmallIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self):
        return f"Image for {self.property.title}"
