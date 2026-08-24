# ChefConnect

A mini on-demand home chef booking application. Users sign up, browse available chefs by cuisine and locality, book a chef for a home dining experience, and receive a confirmation email when the booking is confirmed.

**Core user flow:** Signup/Login → Browse Chefs → Select Chef → Create Booking → Booking Tracker → Booking Confirmed → Confirmation Email

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Mobile | React Native, Expo SDK 52, Expo Router, TypeScript |
| Backend | Python 3.13, FastAPI, Uvicorn, SQLAlchemy 2.0 |
| Database | PostgreSQL (Neon) |
| Cache | Redis |
| Auth | JWT (PyJWT), bcrypt password hashing |
| Workflow | n8n (self-hosted) |
| Email | Resend |
| Deployment | Railway (backend, Redis, n8n), Neon (database) |
| Testing | Pytest (backend), TypeScript strict mode (mobile) |

## Architecture

```
Android App (React Native / Expo)
        │ HTTPS
        ▼
Railway FastAPI Backend
        │
        ├──► Neon PostgreSQL    (persistent data)
        │
        ├──► Redis (Railway)    (caching + rate limiting)
        │
        └──► n8n Webhook        (booking.confirmed event)
                │
                ▼
            Resend API
                │
                ▼
        Confirmation Email
```

**Component responsibilities:**

- **Android App** — User-facing interface for browsing chefs, creating bookings, and tracking status. Connects to the production API over HTTPS.
- **FastAPI Backend** — REST API handling authentication, chef listing, booking CRUD, and webhook emission. Runs on Railway via `uvicorn`.
- **Neon PostgreSQL** — Persistent storage for users, chefs, dishes, and bookings. Serverless PostgreSQL with SSL connections.
- **Redis** — In-memory store used for GET `/api/chefs` response caching (60s TTL) and fixed-window rate limiting on all endpoints.
- **n8n** — Workflow automation platform. Receives `booking.confirmed` webhooks from the backend, validates the event, and calls Resend to send confirmation emails.
- **Resend** — Transactional email service. Sends styled HTML confirmation emails to users when their booking is confirmed.

## MVP 1 — Database Architecture & Core Booking Flow

MVP 1 delivers a functional end-to-end flow: browsing chefs on a mobile app, filtering by cuisine and locality, viewing chef details and menus, and submitting bookings that persist to PostgreSQL.

### Database Schema

5 tables with SQLAlchemy 2.0 ORM:

| Table | Key Columns |
|-------|-------------|
| **users** | id, name, email (unique), password_hash, created_at |
| **chefs** | id, name, cuisine, locality, rating, price_per_meal, signature_dish, experience_years, bio, is_available |
| **dishes** | id, chef_id (FK), name, description, price, is_available |
| **bookings** | id, user_id (FK), chef_id (FK), booking_date, meal_slot (enum), status (enum), special_requests, confirmed_event_emitted, created_at, updated_at |

Enums: `MealSlot` (BREAKFAST, LUNCH, DINNER), `BookingStatus` (PENDING, CONFIRMED, CHEF_EN_ROUTE)

Relationships: Users → Bookings, Chefs → Bookings, Chefs → Dishes (cascade delete)

### Seed Data

11 chefs across Indian regional cuisines (Indian, Punjabi, South Indian, Continental, Kerala, Bengali, Mughlai, Maharashtrian, Awadhi, Asian Fusion, Hyderabadi), 33 dishes (3 per chef), 11 users, and 11 bookings with varied statuses.

### Backend APIs

**GET `/api/chefs`** — Returns all available chefs with nested dishes. Optional `cuisine` and `locality` query filters (case-insensitive). Results cached in Redis.

**POST `/api/bookings`** — Creates a booking. Accepts `chef_id`, `booking_date`, `meal_slot`, optional `special_requests`. Requires JWT. User identity derived from token, not request body. Server sets initial status to PENDING.

### Mobile Application

- **Expo Router** file-based navigation with bottom tab bar (Explore, Bookings, Profile)
- **Explore screen** — Chef listing with cuisine/locality chip filters, loading skeleton, error retry, empty states
- **Chef detail screen** — Hero card, stats row, bio, signature dish, full menu, sticky "Book Chef" footer
- **Booking modal** — Bottom sheet with native date picker, meal slot selector, special requests input
- **Booking success** — Confirmation card displayed in-modal, then navigates to Booking Tracker
- **Design system** — Material Design 3-inspired tokens (warm brown/terracotta primary, 8-level surface hierarchy, HankenGrotesk typography)

### Testing

| Area | Tests | Status |
|------|-------|--------|
| Database models | 6 | Passed |
| Chef API | 6 | Passed |
| Booking API | 8 | Passed |
| **Total backend** | **20** | **All passed** |

## MVP 2 — Security, Status Tracking & Android

MVP 2 delivered authentication, security hardening, and booking state tracking across the backend and mobile app.

### JWT Authentication

- bcrypt password hashing (cost factor 12)
- `POST /api/auth/signup` — Register with name, email, password. Validates input, normalizes email, hashes password.
- `POST /api/auth/login` — Authenticate with email/password. Returns JWT access token (HS256, configurable expiry).
- `get_current_user` dependency — Extracts Bearer token, decodes JWT, looks up user. Returns 401 for missing/invalid/expired tokens.
- Environment-based `JWT_SECRET_KEY` with production validation (rejects default dev key).

### Protected Routes

- `POST /api/bookings` and `POST /api/bookings/{id}/confirm` require JWT authentication
- User identity derived exclusively from the JWT — `user_id` is not accepted in request bodies, preventing impersonation
- `GET /api/chefs`, signup, and login remain public

### Input Validation & Sanitization

- Name validation (1-100 chars, no blank), email normalization (lowercase, trimmed), password constraints (8-128 chars)
- Cuisine/locality filters (stripped, truncated to 100 chars)
- Booking date rejection (past dates), meal slot enum validation, special requests (max 500 chars, stripped)
- SQLAlchemy parameterized queries throughout

### Rate Limiting

Redis-backed fixed-window rate limiting with per-endpoint configuration:

| Scope | Limit | Window | Failure Mode |
|-------|-------|--------|-------------|
| Auth (signup/login) | 5 req | 60s | Fail-closed (503 if Redis down) |
| Chef listing | 60 req | 60s | Fail-open |
| Booking actions | 10 req | 60s | Fail-open |

Response headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, `Retry-After`

### Booking Tracker & Status Flow

- `GET /api/bookings` — JWT-protected, returns user-specific bookings with chef data, ordered by newest first
- Mobile Bookings screen with booking cards and live status chips
- Booking Tracker screen with vertical timeline (PENDING → CONFIRMED → CHEF_EN_ROUTE)
- **Simulated progression** based on `booking.created_at`:
  - 0–9 seconds: PENDING
  - 10–19 seconds: CONFIRMED
  - 20+ seconds: CHEF_EN_ROUTE
- Backend persisted status acts as a floor — simulation never regresses below it
- Status-source abstraction (`BookingStatusSource` interface) allows swapping simulation for real-time implementation later

### Android Testing

- Physical Android device testing via USB + ADB reverse tunneling
- Expo Go SDK 52 for runtime
- Full stack verified: Android Phone → React Native/Expo → FastAPI → PostgreSQL

### Testing

| Area | Tests | Status |
|------|-------|--------|
| Backend suite (final) | 92 | All passed |
| TypeScript check | — | Clean |

## MVP 3 — Cloud Infrastructure, Caching & Automation

### Production Deployment

| Component | Platform | Details |
|-----------|----------|---------|
| Backend | Railway | FastAPI + Uvicorn, auto-deploys from `main` branch |
| Database | Neon | Serverless PostgreSQL, SSL connections (`sslmode=require`) |
| Redis | Railway | Single instance, caching + rate limiting |
| n8n | Railway | Self-hosted workflow automation (pinned to v2.13.4) |
| Mobile | Android | Points to production HTTPS API |

**Production API base URL:** `https://web-production-6da3e.up.railway.app`

**Swagger/OpenAPI docs:** Available at `https://web-production-6da3e.up.railway.app/docs`

### Redis Caching

Cached endpoint: **GET `/api/chefs`**

| Property | Value |
|----------|-------|
| Key format | `cache:chefs:cuisine=<encoded>&locality=<encoded>` or `cache:chefs:all` |
| TTL | 60 seconds (configurable via `CHEFS_CACHE_TTL_SECONDS`) |
| Strategy | Cache-aside (check cache → miss → query DB → populate cache) |
| Fail-open | Redis errors silently fall through to database queries |
| Invalidation | TTL-based only (passive expiration) |

Each unique combination of cuisine/locality filters gets its own cache key. Filter values are URL-encoded and normalized (stripped, truncated to 100 chars). Setting TTL to 0 disables caching entirely.

### n8n Workflow — Booking Confirmation Email

The `booking-confirmation` workflow is a 4-node pipeline that sends confirmation emails when bookings are confirmed:

```
Webhook (POST /webhook/booking-confirmed)
        │
        ▼
Validate Event (IF node: event == "booking.confirmed")
        │
   ┌────┴────┐
   ▼         ▼
Resend     Ignore Other Events (NoOp)
```

| Node | Type | Purpose |
|------|------|---------|
| **Webhook** | Webhook (v2) | Receives POST from FastAPI. Responds immediately (`onReceived`). |
| **Validate Event** | IF (v2) | Checks `$json.body.event == "booking.confirmed"`. Routes matching events to Resend. |
| **Resend** | HTTP Request (v4) | POSTs to `https://api.resend.com/emails` with styled HTML confirmation. |
| **Ignore Other Events** | NoOp | Sink for unmatched event types. Prevents errors. |

The workflow reacts specifically to `booking.confirmed` events. All other event types are silently dropped.

### End-to-End Production Workflow

```
POST /api/bookings
    │
    ▼
Booking created as PENDING
    │
    ▼
Booking Tracker: PENDING → CONFIRMED (simulated, 10s)
    │
    ▼
POST /api/bookings/{id}/confirm
    │
    ▼
Backend sets status=CONFIRMED, confirmed_event_emitted=True
    │
    ▼
Backend POSTs booking.confirmed webhook to n8n
    │
    ▼
n8n Validate Event node checks event == "booking.confirmed"
    │
    ▼
Resend sends confirmation email to user
    │
    ▼
User receives email
```

Key design decisions:
- `confirmed_event_emitted` boolean on the Booking model prevents duplicate webhook emissions
- Webhook is fire-and-forget — failures are logged but never block the API response
- If n8n or Resend is unavailable, the booking still transitions to CONFIRMED in the database
- The webhook URL is configured via `N8N_BOOKING_CONFIRMED_WEBHOOK_URL` environment variable

### Email Template

The Resend email includes:
- User name and chef name
- Booking date and meal slot
- Booking ID and status
- Styled HTML with inline CSS

### Testing

| Area | Tests | Status |
|------|-------|--------|
| Backend suite | 121 | All passed |
| TypeScript check | — | Clean |

## API Documentation

**Base URL (Production):** `https://web-production-6da3e.up.railway.app`

**Interactive docs:** `https://web-production-6da3e.up.railway.app/docs` (Swagger UI)

### Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/auth/signup` | No | Register a new user |
| `POST` | `/api/auth/login` | No | Authenticate and receive JWT |
| `GET` | `/api/chefs` | No | List available chefs (cached, filterable) |
| `POST` | `/api/bookings` | JWT | Create a new booking |
| `GET` | `/api/bookings` | JWT | List current user's bookings |
| `POST` | `/api/bookings/{id}/confirm` | JWT | Confirm a pending booking |

#### POST `/api/auth/signup`

```
Request:  { "name": "string", "email": "string", "password": "string" }
Response: { "id": 1, "name": "string", "email": "string" }  (201)
```

#### POST `/api/auth/login`

```
Request:  { "email": "string", "password": "string" }
Response: { "access_token": "string", "token_type": "bearer" }
```

#### GET `/api/chefs`

Query params: `cuisine` (optional), `locality` (optional)

```
Response: { "chefs": [{ "id": 1, "name": "...", "cuisine": "...", "dishes": [...] }] }
```

#### POST `/api/bookings`

Headers: `Authorization: Bearer <JWT>`

```
Request:  { "chef_id": 1, "booking_date": "2026-08-25", "meal_slot": "DINNER", "special_requests": "..." }
Response: { "id": 1, "status": "PENDING", "chef": {...}, ... }  (201)
```

#### GET `/api/bookings`

Headers: `Authorization: Bearer <JWT>`

```
Response: { "bookings": [{ "id": 1, "status": "PENDING", "chef": {...}, ... }] }
```

#### POST `/api/bookings/{id}/confirm`

Headers: `Authorization: Bearer <JWT>`

```
Response: { "id": 1, "status": "CONFIRMED", ... }
```

## Security

| Measure | Implementation |
|---------|---------------|
| Password hashing | bcrypt (cost factor 12) |
| Authentication | JWT Bearer tokens (HS256) |
| Authorization | `get_current_user` dependency, user-scoped booking operations |
| Impersonation prevention | `user_id` derived from JWT only, not from request body |
| Rate limiting | Fixed-window Redis counters with per-endpoint configuration |
| Fail-closed auth | Auth rate limiting returns 503 if Redis is unavailable |
| Input validation | Pydantic schemas with validators, string normalization, length limits |
| Parameterized queries | SQLAlchemy ORM throughout (no raw SQL injection vectors) |
| Environment secrets | JWT_SECRET_KEY, DATABASE_URL, REDIS_URL, RESEND_API_KEY stored as env vars |
| Production key validation | App refuses to start if JWT_SECRET_KEY equals default dev value |
| HTTPS | Production Railway deployment with TLS |
| Database SSL | `sslmode=require` injected for PostgreSQL connections |
| Token storage | Expo SecureStore on mobile (encrypted keychain/keystore) |
| Session expiry | 401 responses clear stored token and null user state |

## Project Structure

```
chefconnect/
├── mobile/                    React Native + Expo mobile application
│   ├── app/
│   │   ├── (auth)/            Login, signup screens
│   │   ├── (tabs)/            Explore, Bookings, Profile tabs
│   │   ├── booking/[id].tsx   Booking Tracker (timeline + live status)
│   │   └── chef/[id].tsx      Chef Detail (profile, menu, book CTA)
│   ├── components/            10 reusable UI components
│   ├── constants/             Design tokens (colors, typography, spacing)
│   ├── context/               AuthContext (JWT state, login/logout)
│   ├── hooks/                 useAuth, useChefs, useBooking, useBookingStatus
│   ├── services/              API client, authService, bookingService, chefService
│   ├── types/                 TypeScript type definitions
│   └── utils/                 Formatting, error normalization, status logic
├── backend/                   FastAPI backend
│   ├── app/
│   │   ├── api/routes/        auth.py, chefs.py, bookings.py
│   │   ├── cache/             Redis client, chef list caching
│   │   ├── core/              config, rate limiting
│   │   ├── db/                SQLAlchemy engine, session, init
│   │   ├── models/            User, Chef, Dish, Booking
│   │   ├── schemas/           Pydantic request/response schemas
│   │   ├── seed/              Database seeder (11 chefs, 33 dishes)
│   │   └── services/          auth, chef, booking, webhook services
│   ├── tests/                 121 Pytest tests
│   └── requirements.txt       Python dependencies
├── n8n/
│   ├── README.md              Setup documentation
│   └── workflows/
│       └── booking-confirmation.json   4-node workflow
├── docker-compose.yml         Local PostgreSQL + Redis
├── Procfile                   Railway deployment config
└── README.md
```

## Local Development

### Prerequisites

- Python 3.13+
- Node.js 18+
- Docker (for PostgreSQL and Redis)

### Backend Setup

```bash
# Start infrastructure
docker compose up -d

# Install dependencies
cd backend
pip install -r requirements.txt

# Initialize and seed database
python -m app.db.init_db

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Mobile Setup

```bash
cd mobile
npm install
npx expo start
```

To point at local backend, update `mobile/constants/config.ts`:

```typescript
export const API_BASE_URL = 'http://10.0.2.2:8000';
```

For physical Android device via USB:

```bash
adb reverse tcp:8000 tcp:8000
adb reverse tcp:8081 tcp:8081
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | `postgresql+psycopg://postgres:changeme@localhost:5432/chefconnect` | PostgreSQL connection URL |
| `REDIS_URL` | Yes | `redis://localhost:6379/0` | Redis connection URL |
| `JWT_SECRET_KEY` | Yes | dev default (rejected in production) | JWT signing secret (min 32 chars) |
| `ENVIRONMENT` | No | `development` | Set to `production` for deployment |
| `N8N_BOOKING_CONFIRMED_WEBHOOK_URL` | No | `""` | n8n webhook URL for booking confirmations |
| `RESEND_API_KEY` | No | `""` | Resend API key (used by n8n, not backend directly) |
| `RESEND_FROM_EMAIL` | No | `onboarding@resend.dev` | Sender address for Resend emails |
| `RATE_LIMIT_ENABLED` | No | `True` | Enable/disable rate limiting |
| `CHEFS_CACHE_TTL_SECONDS` | No | `60` | Chef list cache TTL (0 to disable) |

## Production Deployment

| Component | Platform | Config |
|-----------|----------|--------|
| Backend | Railway | `Procfile` → `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Database | Neon | Serverless PostgreSQL with connection pooling |
| Redis | Railway | Single instance for caching + rate limiting |
| n8n | Railway | Self-hosted, pinned to v2.13.4 |
| Mobile | Android | API base URL points to Railway HTTPS endpoint |

**Railway services:**

| Service | URL |
|---------|-----|
| Backend API | `https://web-production-6da3e.up.railway.app` |
| n8n | `https://n8n-production-6ab1.up.railway.app` |

Backend auto-deploys from `main` branch. On startup: initializes database tables, seeds chef data, logs webhook configuration status.

## Testing / Verification

### Backend Tests

```bash
cd backend
python -m pytest
```

**121 tests** across 10 test files:

| File | Tests | Coverage |
|------|-------|----------|
| test_auth.py | 23 | Password hashing, JWT, signup/login, validation |
| test_bookings.py | 17 | Creation, validation, auth, chef checks |
| test_bookings_list.py | 11 | Listing, user isolation, ordering |
| test_booking_confirm.py | 16 | Confirmation, idempotency, webhook emission |
| test_chefs.py | 6 | Listing, filtering |
| test_chefs_cache.py | 13 | Cache hit/miss, TTL, fail-open, normalization |
| test_database.py | 6 | Schema, relationships, seed data |
| test_rate_limit.py | 12 | Per-scope limits, headers, fail-closed/open |
| test_validation.py | 17 | Input constraints, sanitization |

### TypeScript Check

```bash
cd mobile
npx tsc --noEmit
```

### Production Verification

- Backend API: `curl https://web-production-6da3e.up.railway.app/docs` returns Swagger UI
- Chef listing: `GET /api/chefs` returns 11 chefs with cached responses
- Booking creation: `POST /api/bookings` with JWT returns 201
- Booking confirmation: `POST /api/bookings/{id}/confirm` triggers n8n webhook
- n8n execution: Workflow runs and calls Resend API
- Email delivery: Confirmation email received at user's address

### Physical Android Testing

- Expo Go SDK 52 on physical Android device
- Full production stack: Android → Railway API → Neon PostgreSQL → Redis → n8n → Resend

## Delco Engineering Challenge Mapping

### MVP 1 — Database & Booking Flow

- [x] Database schema (users, chefs, dishes, bookings)
- [x] Seeded chef data (11 chefs, 33 dishes)
- [x] GET `/api/chefs` with cuisine/locality filtering
- [x] POST `/api/bookings` with validation
- [x] Explore screen with filters and chef cards
- [x] Booking modal with date picker and meal slot selection
- [x] 20 backend tests passing

### MVP 2 — Security & Tracking

- [x] JWT signup/login with bcrypt password hashing
- [x] Protected booking routes (Authorization: Bearer header)
- [x] Input validation and sanitization
- [x] Redis-backed rate limiting (fail-closed for auth)
- [x] Booking Tracker with PENDING → CONFIRMED → CHEF_EN_ROUTE status flow
- [x] Deterministic simulated status progression
- [x] Physical Android device testing
- [x] 92 backend tests passing

### MVP 3 — Cloud & Automation

- [x] Backend deployed on Railway with HTTPS
- [x] Production database on Neon (PostgreSQL)
- [x] Redis deployed on Railway
- [x] Redis caching for GET `/api/chefs` (60s TTL)
- [x] n8n self-hosted on Railway
- [x] Booking-confirmed webhook (FastAPI → n8n)
- [x] n8n validates `booking.confirmed` events
- [x] Resend email integration
- [x] Confirmation email sent after booking transitions to CONFIRMED
- [x] Mobile app connected to production HTTPS API
- [x] 121 backend tests passing

### Submission Artifacts

| Artifact | Status |
|----------|--------|
| GitHub repository | Complete |
| Live API + Swagger docs | https://web-production-6da3e.up.railway.app/docs |
| Downloadable APK | Pending (EAS Build) |
| Loom walkthrough | Pending |

## Demo Flow

Recommended walkthrough for reviewers:

1. **Open the app** on Android device or emulator
2. **Sign up** with a new account (or use a seeded user)
3. **Browse chefs** on the Explore screen — scroll through the list, note cuisine and pricing
4. **Filter** by tapping cuisine or locality chips (e.g., "Indian" + "Indirapuram")
5. **Open a chef** — view full profile, bio, menu with prices
6. **Tap "Book Chef"** — the booking modal opens (redirects to login if unauthenticated)
7. **Create a booking** — select a date, choose meal slot, add special requests, tap "Request Booking"
8. **Booking Tracker** — after creation, the app navigates to the tracker showing the PENDING status timeline
9. **Watch the status transition** — after ~10 seconds, PENDING transitions to CONFIRMED
10. **Check backend logs** — Railway logs show `POST /api/bookings/{id}/confirm` with webhook delivery
11. **Check n8n** — n8n execution log shows the webhook received and processed
12. **Check email** — confirmation email arrives with booking details
13. **My Bookings tab** — navigate to the Bookings tab to see the booking with its current status

## License

This project is part of the Delco Engineering Take-Home Challenge.
