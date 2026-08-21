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

## Future Milestones

### MVP 2 — Planned

- User authentication (login/signup)
- User-specific booking experience (view own bookings)
- Booking management (cancel, reschedule)
- Profile editing
- Push notifications

### MVP 3 — Planned

- Redis caching layer
- n8n workflow automations
- Payment processing
- Chef availability scheduling
- Production deployment
- CI/CD pipeline
