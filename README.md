# GeoPost

GeoPost is a Django property discovery app for Bangladesh listings. It combines normal filters with semantic location search powered by Sentence Transformers and PostgreSQL with PostGIS and pgvector.

## Features

- Homepage with featured properties.
- Property search by location, price range, and minimum bedrooms.
- Semantic search using natural language, such as `quiet family home near schools`.
- Location autocomplete API ranked by semantic similarity.
- Property detail pages with images, map coordinates, and distance information.
- Django admin with property images, filters, and previews.
- CSV import command for the sample property data.
- HNSW indexes for vector similarity search.

## Requirements

- Python 3.12 or newer.
- [`uv`](https://docs.astral.sh/uv/).
- PostgreSQL with PostGIS and the pgvector extension enabled.

The project expects a local database named `appdb` with user `appuser`. Update the database settings for your local PostgreSQL installation before running migrations if those values differ.

## Setup with uv

Install the Python environment and dependencies:

```bash
uv sync
```

Run database migrations:

```bash
uv run python manage.py migrate
```

Create an admin account if you want to use Django admin:

```bash
uv run python manage.py createsuperuser
```

Import the sample listings:

```bash
uv run python manage.py import_properties data/properties.csv
```
## Semantic search
Generate embeddings for every active location. The first run downloads `all-MiniLM-L6-v2` from Sentence Transformers and stores 384-number vectors in PostgreSQL:

```bash
uv run python manage.py generate_location_embeddings
```

To regenerate all location vectors:

```bash
uv run python manage.py generate_location_embeddings --force
```

The property listing search form accepts a natural-language description in `semantic_query`. Regular filters still work alongside semantic search. Results are ranked by the closest matching location vector, then by newest listing.

## Autocomplete API

The location autocomplete endpoint is:

```text
/api/locations/autocomplete/?q=family%20home
```

It returns up to eight active locations ranked by semantic similarity. Queries shorter than two characters return an empty result set.

## Running checks

Run the automated tests:

```bash
uv run python manage.py test
```

Check the project configuration:

```bash
uv run python manage.py check
```

## Project layout

- `config/` contains Django settings and URL configuration.
- `properties/` contains models, views, forms, templates, management commands, and tests.
- `data/properties.csv` contains sample listings.
- `properties/semantic.py` contains the shared embedding model and encoding helpers.
