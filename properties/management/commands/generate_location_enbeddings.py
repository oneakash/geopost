from django.core.management.base import BaseCommand, CommandError

from properties.models import Location
from properties.semantic import embed_texts


class Command(BaseCommand):
    help = "Generate all-MiniLM-L6-v2 embeddings for locations."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Regenerate embeddings that already exist.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=32,
        )

    def handle(self, *args, **options):
        queryset = Location.objects.filter(is_active=True).order_by("id")
        if not options["force"]:
            queryset = queryset.filter(embedding__isnull=True)

        locations = list(queryset)
        if not locations:
            self.stdout.write("No locations need embeddings.")
            return

        batch_size = options["batch_size"]
        if batch_size < 1:
            raise CommandError("batch-size must be at least 1")

        updated = 0
        for start in range(0, len(locations), batch_size):
            batch = locations[start:start + batch_size]
            texts = [self.location_text(location) for location in batch]
            vectors = embed_texts(texts)

            for location, vector in zip(batch, vectors):
                location.embedding = vector
                location.save(update_fields=["embedding", "updated_at"])
                updated += 1

            self.stdout.write(f"Embedded {updated}/{len(locations)} locations")

        self.stdout.write(self.style.SUCCESS("Location embeddings generated."))

    @staticmethod
    def location_text(location: Location) -> str:
        parts = [
            location.name,
            location.address,
            location.city,
            location.state,
            location.country,
        ]
        return ", ".join(part.strip() for part in parts if part and part.strip())
