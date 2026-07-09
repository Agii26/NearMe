# NearMe

Local business discovery for the Philippines/SEA market — location-first search plus a lightweight social layer, positioned where Google Maps, Yelp, Facebook Pages, and Nextdoor are weakest locally.

This repo covers **Phase 1: Foundation & Search** — OSM-sourced business data, geospatial search, and read-only business profiles. See `docs/roadmap.md`-equivalent (tracked in the project's Obsidian vault) for the full 7-phase plan.

## Stack

| Layer | Choice |
|---|---|
| Backend | Django + Django REST Framework |
| Frontend | React + Vite |
| Database | PostgreSQL + PostGIS |
| Business data | OpenStreetMap via the Overpass API |
| Map rendering | Google Maps JS API (rendering/autocomplete only — no OSM/Google data mixing, no caching of Google-sourced content) |
| Testing | pytest + pytest-django (backend), Jest + React Testing Library (frontend) |

## Design system

Light and dark mode, both WCAG AA-verified. Fraunces (headings) + Work Sans (body). See `docs/screenshots/` for reference renders of the search/results and business profile screens in both modes.

## Running locally

### Option A — Docker Compose (recommended)

```bash
docker compose up
```

- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- Postgres+PostGIS: localhost:5432

The backend container runs migrations automatically on startup. Seed some demo data once it's up:

```bash
docker compose exec backend python manage.py seed_demo_data
```

### Option B — Native setup

**Backend:**

```bash
cd backend
python3 -m venv backend-venv
./backend-venv/bin/pip install -r requirements-dev.txt
# Requires PostgreSQL with the PostGIS extension enabled, and GDAL/GEOS/PROJ
# system libraries installed (see Dockerfile for the exact apt packages).
cp .env.example .env  # adjust DB credentials if needed
./backend-venv/bin/python manage.py migrate
./backend-venv/bin/python manage.py seed_demo_data
./backend-venv/bin/python manage.py runserver
```

**Frontend:**

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Environment variables

**Backend** (`backend/.env`, see `.env.example`): Django secret key, debug flag, allowed hosts, database credentials, CORS origins, and the Overpass API URL.

**Frontend** (`frontend/.env`, see `.env.example`): `VITE_API_BASE_URL` and `VITE_GOOGLE_MAPS_API_KEY`. Without a Google Maps key, the business profile page falls back to a static map placeholder rather than failing — get a key from the [Google Cloud Console](https://console.cloud.google.com/) (Maps JavaScript API) to see the real map.

## Pulling in real business data

The seed command above is hand-written demo data (6 businesses around Quezon City) so the app works immediately without any external calls. To pull real data from OpenStreetMap for a given area instead:

```bash
python manage.py sync_osm_businesses --bbox=14.60,121.00,14.78,121.12
```

`--bbox` is `south,west,north,east` in decimal degrees. The command is safe to re-run — it matches on OSM element ID, so re-running never creates duplicates, only updates.

## Testing

```bash
# Backend
cd backend && ./backend-venv/bin/python -m pytest

# Frontend
cd frontend && npm test
```

35 backend tests cover the `opening_hours` parser, OSM tag-to-category mapping, sync idempotency, geospatial search (distance ordering, radius/category/text filters), and the business detail endpoint. 10 frontend tests cover the search bar, category chips, and business card rendering.

## API

| Endpoint | Description |
|---|---|
| `GET /api/health/` | Health check |
| `GET /api/categories/` | List all business categories |
| `GET /api/businesses/search?lat=&lng=&radius=&category=&q=` | Geospatial search, nearest-first. `lat`/`lng` required; `radius` in km (default 5, capped at 50); `category` is a category slug; `q` does a case-insensitive name search |
| `GET /api/businesses/<id>/` | Full business profile, including `hours`, `is_open_now`/`closes_at`, `photos`, `average_rating`/`review_count`, and `is_owner` (request-aware) |
| `PATCH /api/businesses/<id>/` | Dashboard edits — claiming owner only |
| `POST /api/businesses/<id>/claim/` | Submit a claim on an unclaimed listing — authenticated users only |
| `POST /api/businesses/<id>/photos/` | Upload a photo (multipart) — claiming owner only |
| `GET /api/businesses/mine/` | Businesses the authenticated user owns |
| `GET /api/businesses/claims/mine/` | The authenticated user's claim history and status |
| `GET /api/businesses/<id>/reviews/` | List visible reviews for a business |
| `POST /api/businesses/<id>/reviews/` | Post a review — authenticated, one per user per business, can't review a business you own |
| `DELETE /api/reviews/<id>/` | A reviewer can delete their own review |
| `POST /api/reviews/<id>/flag/` | Report a review for moderation — one flag per user per review, doesn't hide the review by itself |
| `POST /api/auth/register/` | Create an account with a role (`consumer` or `business_owner`) |
| `POST /api/auth/login/` | Returns a JWT access + refresh token pair |
| `POST /api/auth/refresh/` | Exchange a refresh token for a new access token |
| `POST /api/auth/logout/` | Blacklists the given refresh token |
| `GET /api/auth/me/` | The authenticated user's account and role |

Claims don't have a real-world verification step (no license lookup, no mailed postcard) — they land in a pending queue and are approved or rejected by hand via the Django admin (`/admin/`, `BusinessClaim` model, bulk actions). Reviews are visible immediately on posting; a single flag doesn't hide a review, it surfaces it in the admin's moderation queue (`Review` model, "has flags" filter) for a human decision.

## What's out of scope through Phase 3

By design, not a gap: the social feed (business posts, follows) and payments. Search, claiming, and reviews all work end to end — see the API table above.
