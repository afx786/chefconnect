# ChefConnect

ChefConnect is a platform for booking private chefs. Users can browse available chefs, view menus and pricing, filter by cuisine and locality, and submit bookings for home dining experiences.

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Mobile | React Native + Expo SDK 52, Expo Router, TypeScript |
| Backend | Python, FastAPI, Uvicorn |
| Database | PostgreSQL 18 |
| ORM | SQLAlchemy 2.0 (async), Alembic |

## Project Structure

```
chefconnect/
├── mobile/          React Native + Expo mobile application
│   ├── app/             Expo Router screens and layouts
│   ├── components/      Reusable UI components
│   ├── constants/       Design tokens (colors, typography, spacing)
│   ├── context/         React context (auth placeholder)
│   ├── hooks/           Custom hooks (useChefs, useBooking)
│   ├── services/        API client and service functions
│   ├── types/           TypeScript type definitions
│   └── utils/           Utility functions (formatDate, formatCurrency)
├── backend/         FastAPI backend
│   ├── app/
│   │   ├── api/routes/  API route handlers
│   │   ├── models/      SQLAlchemy models
│   │   ├── schemas/     Pydantic request/response schemas
│   │   └── services/    Business logic
│   ├── alembic/         Database migrations
│   └── tests/           Pytest test suite
└── n8n/             n8n workflow automations (deferred)
```

## MVP 1 — Completed

MVP 1 delivers a functional end-to-end flow: browsing chefs on a mobile app, filtering by cuisine and locality, viewing chef details and menus, and submitting bookings that persist to PostgreSQL.

### Database

- PostgreSQL 18 with SQLAlchemy 2.0 async ORM
- **Users** — id, name, email, phone, location
- **Chefs** — id, name, cuisine, locality, experience, bio, rating, pricing, availability
- **Dishes** — id, name, description, price, signature flag, linked to chefs
- **Bookings** — id, user, chef, date, meal slot, special requests, status (PENDING)
- Relationships: Users → Bookings, Chefs → Bookings, Chefs → Dishes
- Seed data: 11 chefs, 33 dishes, 11 users, 11 bookings

### Backend APIs

**GET `/api/chefs`**
- Returns all available chefs with dishes and menu data
- Optional `cuisine` filter (case-insensitive)
- Optional `locality` filter (case-insensitive)
- Eager-loads dishes for each chef
- Returns paginated chef list with full details

**POST `/api/bookings`**
- Accepts: chef_id, user_id, booking_date, meal_slot, optional special_requests
- Validates user existence, chef existence, and chef availability
- Validates meal slot (BREAKFAST, LUNCH, DINNER)
- Server-controlled initial status: PENDING
- Persists to PostgreSQL and returns the created booking

### Mobile Application

- **Expo Router** file-based navigation
- **Explore screen** — chef listing with loading skeleton, error retry, and empty-results states
- **Chef detail screen** — hero image, stats, bio, signature dish, full menu, pricing
- **Filter bar** — cuisine and locality chip filters
- **Booking modal** — bottom sheet with date picker, meal slot selection, special requests
- **Booking success/error states** — confirmation display with booking details
- **Bottom navigation** — Explore, Bookings, Profile tabs
- **Animations** — card staggered entrance, button press feedback, modal slide transition
- **Design system** — Material Design 3-inspired tokens (colors, typography, spacing, shadows)

### Testing

| Area | Tests | Status |
|------|-------|--------|
| Database models | 6 | Passed |
| Chef API | 6 | Passed |
| Booking API | 8 | Passed |
| **Total backend** | **20** | **All passed** |
| TypeScript check | — | Clean |
| Metro Android bundle | — | Successful |

### Physical Device Verification

The mobile application was tested on a real Android device connected via USB using ADB.

- Expo Go SDK 52 used for runtime
- ADB reverse tunneling for development server connection
- Full stack verified: **Android Phone → React Native/Expo → FastAPI → PostgreSQL**
- A booking was submitted from the physical device and confirmed persisted in PostgreSQL

### MVP 1 Status

**COMPLETED**

---

## MVP 2 — Completed

MVP 2 delivered authentication, security hardening, and booking state/status tracking across the backend and mobile app.

### Step A — JWT Authentication Foundation

- bcrypt password hashing
- Signup endpoint (`POST /api/auth/signup`)
- Login endpoint (`POST /api/auth/login`)
- JWT access-token generation and verification
- Configurable JWT expiration
- Environment-based JWT secret
- Authentication schemas and service
- `get_current_user` dependency

Commit: `ac979e9` — JWT auth foundation setup

### Step B — Securing API Routes

- `POST /api/bookings` requires JWT authentication (`Authorization: Bearer <JWT>`)
- `user_id` removed from booking creation requests; identity derived exclusively from the JWT
- Protection against user impersonation
- `GET /api/chefs`, signup, and login remain public

Commit: `8b77df5` — securing api routes and setting up auth headers

### Step C — Mobile Authentication

- React Native authentication flow (signup UI, login UI)
- Expo SecureStore for JWT storage
- AuthContext with authentication state restoration and logout
- Axios Authorization interceptor
- 401 session-expiration handling
- Public Explore experience; authentication required when attempting to book
- Unauthenticated Book Chef → Login → return-to-booking flow

Commits:
- `7ef55da` — integrating auth in mobile ui
- `d051b98` — fix mobile auth state and public explore
- `7f6e884` — fix unauthenticated booking navigation

Physical-device testing was performed during this phase.

### Step D — Security Hardening

Input validation and normalization:

- Name validation, email normalization, password constraints
- Cuisine/locality, chef_id, booking date, meal slot, and special-request validation
- SQLAlchemy parameterized queries

Redis-backed rate limiting:

- Authentication, booking, and chef-listing endpoints
- Fixed-window Redis counters with `Retry-After` and rate-limit headers
- Fail-closed behavior for authentication endpoints; fail-open for non-critical endpoints

Environment/security hardening:

- Environment-based configuration
- JWT production secret validation
- Redis and rate-limit configuration
- `.env` protection
- Docker Compose Redis/PostgreSQL infrastructure

Commit: `a42b884` — sanitizing input and adding rate limiting capabilities

Verification: **81/81 tests passed** after Step D.

### State & Status Tracking

- `GET /api/bookings` — JWT-protected retrieval with user-specific booking isolation
- Booking response includes chef information via efficient relationship loading
- Mobile Bookings screen with booking cards
- Booking Tracker screen with status timeline
- Simulated progression: PENDING → CONFIRMED → CHEF_EN_ROUTE
- Deterministic simulation based on `booking.created_at`; persisted backend status acts as the floor
- Shared status-resolution architecture; status stays consistent between the Booking Card and the Booking Tracker
- Animation/transition support and loading/error/empty states

Architecture notes:

- The backend remains the authority for persisted booking status.
- The current mobile simulation is presentation/demo state.
- The tracker uses a status-source abstraction so the simulated implementation can later be replaced by a real-time implementation.
- Real-time infrastructure has NOT been implemented yet.

Commits:

- `5a350b7` — booking tracker and status simulation added
- `54ad534` — fix booking validation error rendering
- `0f28e4b` — sync booking card status with tracker

Additional physical-device debugging/fixes included:

- Local-date handling for booking dates
- Centralized API error normalization
- Unauthenticated booking navigation fixes
- Stale JWT/session handling
- Bookings endpoint verification after restarting stale Uvicorn process

Booking creation and the tracker flow were manually verified on the physical Android device.

### MVP 2 Verification

| Area | Tests | Status |
|------|-------|--------|
| Backend suite (final) | 92 | All passed |
| TypeScript check | — | Clean |
| Metro Android bundle | — | Successful |

### Release Artifact Note

Release APK / production distribution remains part of the MVP 3 completion flow after the backend is deployed.

### MVP 2 Status

**COMPLETED**

---

## Roadmap

```
MVP 1
Database + Backend APIs + Mobile UI
        ↓
     COMPLETED

MVP 2
Authentication + Security + Booking Tracking
        ↓
     COMPLETED

MVP 3
Redis Caching
        ↓
n8n + Resend
        ↓
Cloud Deployment + HTTPS
        ↓
Mobile → Production API
        ↓
Final Android APK
        ↓
  MVP 3 COMPLETE
```

---

## MVP 3 — Cloud Infrastructure, Caching & Workflow Automation (Planned)

All items below are planned future work. None of them are implemented yet.

### MVP 3 — Step 1: Redis Performance Caching

Implement Redis caching for `GET /api/chefs` to reduce repeated PostgreSQL reads for the high-frequency chef discovery endpoint. This builds on the Redis infrastructure already introduced for rate limiting — Redis rate limiting already exists; MVP 3 adds application caching on top of it.

### MVP 3 — Step 2: Workflow Automation / Notifications

Set up booking confirmation automation using n8n + Resend.

Planned flow:

```
Booking status transition
        ↓
     Confirmed
        ↓
Trigger webhook/workflow
        ↓
       n8n
        ↓
      Resend
        ↓
Email/notification confirmation
```

The notification should be triggered by an actual transition to CONFIRMED rather than repeatedly sending notifications whenever the booking is read.

### MVP 3 — Step 3: Cloud Deployment & Security

Deploy the FastAPI backend, PostgreSQL database, and Redis to a live cloud environment such as Render, Railway, or AWS. Production configuration will include secure environment variables, a production JWT secret, DATABASE_URL, REDIS_URL, rate-limit configuration, notification service credentials, and HTTPS.

### MVP 3 — Step 4: Connect Mobile App to Production Backend

After the backend is deployed, change the mobile API base URL from the local development backend (current USB/local testing configuration) to the production HTTPS backend URL.

Planned production flow:

```
HTTPS production API
        ↓
      FastAPI
        ↓
PostgreSQL + Redis
        ↓
n8n / Resend workflow
```

### MVP 3 — Step 5: Final Android Release APK

Only AFTER the production backend is deployed and the mobile API URL points to the production HTTPS backend:

- Generate the final Android APK and install it on a physical Android device
- Test the complete production-backed flow: authentication, chef discovery, booking, booking retrieval, status tracker, caching behavior, booking confirmation workflow, and notification flow

Generating the final APK at this point avoids creating a temporary APK pointing to localhost. The final APK will be the distributable release artifact.
