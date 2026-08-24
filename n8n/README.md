# ChefConnect n8n

n8n workflow automations for ChefConnect.

## Booking Confirmation Email

### Overview

When a booking transitions from PENDING to CONFIRMED, the backend emits a `booking.confirmed` event to the n8n webhook. n8n validates the event and calls Resend to send a confirmation email to the user.

```
FastAPI
   ↓ POST booking.confirmed
n8n Webhook
   ↓ validate event type
n8n IF node
   ↓ booking.confirmed matches
n8n HTTP Request → Resend API
   ↓
User receives confirmation email
```

### Setup

1. **Import the workflow** into your n8n instance:
   - Open n8n → Workflows → Import from File
   - Select `workflows/booking-confirmation.json`

2. **Configure Resend credentials** in n8n:
   - Go to Credentials → Add Credential → Header Auth
   - Name: `Resend API Key`
   - Header Name: `Authorization`
   - Header Value: `Bearer re_your_resend_api_key`
   - Save

3. **Update the workflow** to use your credential:
   - Open the imported workflow
   - Click the "Resend" HTTP Request node
   - Under Authentication, select your "Resend API Key" credential
   - Save and activate the workflow

4. **Configure the backend** environment variable:
   ```
   N8N_BOOKING_CONFIRMED_WEBHOOK_URL=https://your-n8n-instance.com/webhook/booking-confirmed
   ```

5. **Activate the workflow** in n8n.

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `N8N_BOOKING_CONFIRMED_WEBHOOK_URL` | n8n webhook URL | `https://n8n.example.com/webhook/booking-confirmed` |
| `RESEND_API_KEY` | Resend API key (used by n8n) | `re_xxxxx` |
| `RESEND_FROM_EMAIL` | Sender address | `onboarding@resend.dev` |

### Event Payload

The webhook receives:

```json
{
  "event": "booking.confirmed",
  "event_id": "booking_confirmed_23",
  "booking_id": 23,
  "user_id": 17,
  "user_email": "user@example.com",
  "user_name": "Aaqib",
  "chef_name": "Chef Ananya Rao",
  "booking_date": "2026-08-25",
  "meal_slot": "DINNER",
  "status": "CONFIRMED"
}
```

### Testing

Without n8n/Resend:
- The backend logs a warning if webhook delivery fails
- The booking still transitions to CONFIRMED in the database
- No email is sent

With n8n/Resend:
- Import the workflow, configure credentials, activate
- Create a booking and wait for the simulated CONFIRMED transition
- Check your email for the confirmation
