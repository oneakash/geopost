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

## 1. Start PostgreSQL with Docker

Open a terminal in the project root directory, where `compose.yaml` is located.

Start the database:

```bash
docker compose up -d
````

Check the running containers:

```
docker compose ps
```

View the database logs if needed:

```
docker compose logs -f
```

Verify that the PostgreSQL container is healthy before proceeding.

The Compose configuration should publish PostgreSQL's port to the host, for example:

```
ports:
  - "127.0.0.1:5432:5432"
```

This allows Django running directly on your Ubuntu machine to connect to PostgreSQL inside Docker through `127.0.0.1:5432`.

Note: The example above shows the port configuration only. Keep your existing database image, volumes, credentials, health check, and other Compose settings.

## 2. Configure the Database Connection

GeoPost expects the following database configuration by default:

| Setting       | Value                             |
| ------------- | --------------------------------- |
| Database name | `appdb`                           |
| Database user | `appuser`                         |
| Host          | `127.0.0.1`                       |
| Port          | `5432`                            |
| Password      | Your configured database password |

Ensure the database settings in `config/settings.py` match the credentials and port configured in `compose.yaml`.

Example Django configuration:

```
DATABASES = {    
    "default": {        
        "ENGINE": "django.contrib.gis.db.backends.postgis",        
        "NAME": "appdb",        
        "USER": "appuser",        
        "PASSWORD": "your_database_password",        
        "HOST": "127.0.0.1",        
        "PORT": "5432",    
    }
}
```

Replace `your_database_password` with your actual configured password. If your project already loads database settings from environment variables, keep using that approach instead of hardcoding credentials.

Because Django runs on the host machine, use `127.0.0.1` when PostgreSQL is published on the host's port 5432. The Docker service name, such as `db`, is generally used when Django runs inside the same Docker network.

## 3. Verify PostgreSQL Extensions

GeoPost requires both PostGIS and pgvector.

Connect to the database using the PostgreSQL service defined in your Compose configuration. If the service is named `db`, run:

```
docker compose exec db psql -U appuser -d appdb
```

Inside the PostgreSQL shell, check the installed extensions:

```
SELECT extname
FROM pg_extension
WHERE extname IN ('postgis', 'vector');
```

If the extensions are installed in the PostgreSQL image but have not been enabled in the database, run:

```
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS vector;
```

Then exit the PostgreSQL shell:

```
\q
```

The PostgreSQL image must include both extensions. If either extension is unavailable, use a compatible image or build an image that includes it before continuing.

```

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

Run:
```bash
uv run python manage.py runserver
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
