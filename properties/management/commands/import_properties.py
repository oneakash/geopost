
import math
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pandas as pd

from django.core.management.base import BaseCommand, CommandError
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.contrib.gis.geos import Point
from django.db import transaction

from properties.models import Location, Property, PropertyImage


class Command(BaseCommand):
    help = "Import properties and locations from a CSV file using Pandas."

    REQUIRED_COLUMNS = {
        "title",
        "description",
        "property_type",
        "listing_type",
        "price",
        "bedrooms",
        "bathrooms",
        "area_sqft",
        "address",
        "city",
        "state",
        "country",
        "latitude",
        "longitude",
        "image_url",
    }

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str)

    def handle(self, *args, **options):
        csv_path = Path(options["csv_file"])

        if not csv_path.is_file():
            raise CommandError(f"CSV file not found: {csv_path}")

        try:
            df = pd.read_csv(csv_path)
        except Exception as exc:
            raise CommandError(f"Could not read CSV: {exc}") from exc

        # Normalize column names and check the CSV schema.
        df.columns = df.columns.str.strip().str.lower()

        missing = self.REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise CommandError(
                f"Missing required columns: {', '.join(sorted(missing))}"
            )

        imported = 0
        failed = 0
        images_created = 0

        for row_number, row in enumerate(
            df.to_dict(orient="records"), start=2
        ):
            try:
                with transaction.atomic():
                    result = self.import_row(row)

                if result["created"]:
                    imported += 1
                else:
                    imported += 1
                    self.stdout.write(
                        f"Updated existing property: {result['title']}"
                    )

                images_created += result["images_created"]

            except Exception as exc:
                failed += 1
                self.stderr.write(
                    self.style.ERROR(
                        f"Row {row_number} skipped: {exc}"
                    )
                )

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Import finished"))
        self.stdout.write(f"Rows processed: {len(df)}")
        self.stdout.write(f"Properties imported/updated: {imported}")
        self.stdout.write(f"Images created: {images_created}")
        self.stdout.write(f"Rows failed: {failed}")

    @staticmethod
    def value(row, field, default=""):
        value = row.get(field, default)

        if pd.isna(value):
            return default

        if isinstance(value, str):
            return value.strip()

        return value

    def import_row(self, row):
        title = str(self.value(row, "title"))
        address = str(self.value(row, "address"))
        city = str(self.value(row, "city"))
        state = str(self.value(row, "state"))
        country = str(self.value(row, "country", "Bangladesh"))

        if not title or not address or not city or not country:
            raise ValueError("title, address, city, and country are required")

        property_type = str(self.value(row, "property_type")).lower()
        listing_type = str(self.value(row, "listing_type")).lower()

        valid_types = dict(Property.PropertyType.choices)
        valid_listing_types = dict(Property.ListingType.choices)

        if property_type not in valid_types:
            raise ValueError(f"Invalid property_type: {property_type}")

        if listing_type not in valid_listing_types:
            raise ValueError(f"Invalid listing_type: {listing_type}")

        try:
            price = Decimal(str(self.value(row, "price")))
            bedrooms = int(self.value(row, "bedrooms"))
            bathrooms = int(self.value(row, "bathrooms"))
            latitude = float(self.value(row, "latitude"))
            longitude = float(self.value(row, "longitude"))
        except (ValueError, TypeError, InvalidOperation) as exc:
            raise ValueError("Invalid price, bedroom, bathroom, or coordinate value") from exc

        if not price.is_finite() or price < 0:
            raise ValueError("price must be a finite, non-negative number")

        if bedrooms < 0 or bathrooms < 0:
            raise ValueError("bedrooms and bathrooms cannot be negative")

        if not math.isfinite(latitude) or not -90 <= latitude <= 90:
            raise ValueError("latitude must be between -90 and 90")

        if not math.isfinite(longitude) or not -180 <= longitude <= 180:
            raise ValueError("longitude must be between -180 and 180")

        point = Point(longitude, latitude, srid=4326)

        # Reuse a location with the same address and administrative area.
        location, _ = Location.objects.get_or_create(
            address=address,
            city=city,
            state=state,
            country=country,
            defaults={
                "coordinates": point,
                "name": city,
            },
        )

        area_value = self.value(row, "area_sqft", None)
        area_sqft = None

        if area_value not in (None, ""):
            try:
                area_sqft = Decimal(str(area_value))
            except (ValueError, TypeError, InvalidOperation) as exc:
                raise ValueError("area_sqft must be a valid number") from exc

            if not area_sqft.is_finite() or area_sqft < 0:
                raise ValueError("area_sqft must be non-negative")

        # This natural key makes repeated imports update the same listing.
        prop, created = Property.objects.update_or_create(
            title=title,
            location=location,
            listing_type=listing_type,
            defaults={
                "description": str(self.value(row, "description")),
                "property_type": property_type,
                "price": price,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "area_sqft": area_sqft,
                "address": address,
                "point": point,
                "is_active": True,
                "is_available": True,
            },
        )

        image_url = str(self.value(row, "image_url"))

        if image_url:
            try:
                URLValidator()(image_url)
            except ValidationError:
                self.stderr.write(
                    f"Invalid image URL for '{title}'; image skipped."
                )
            else:
                _, image_created = PropertyImage.objects.get_or_create(
                    property=prop,
                    image_url=image_url,
                    defaults={
                        "caption": title,
                        "alt_text": title,
                    },
                )
                if image_created:
                    images_created = 1
                else:
                    images_created = 0
        else:
            images_created = 0

        self.stdout.write(
            f"{'Created' if created else 'Processed'}: {title} ({city})"
        )

        return {
            "created": created,
            "title": title,
            "images_created": images_created,
        }
