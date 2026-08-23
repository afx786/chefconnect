interface ApiErrorShape {
  response?: {
    status?: number;
    data?: {
      detail?: unknown;
    };
  };
  request?: unknown;
  message?: unknown;
}

const FIELD_MESSAGES: Record<string, string> = {
  booking_date: 'Please select a valid booking date.',
  chef_id: 'Please choose a chef to book.',
  meal_slot: 'Please choose a valid meal slot.',
  special_requests: 'Special requests are too long. Please shorten them.',
};

const GENERIC_MESSAGE = 'Unable to submit booking. Please try again.';

function friendlyDetail(detail: string): string {
  if (/past/i.test(detail)) {
    return 'Please select a valid booking date.';
  }
  if (/not found/i.test(detail)) {
    return 'This chef is no longer available.';
  }
  if (/unavailable/i.test(detail)) {
    return 'This chef is currently unavailable for bookings.';
  }
  return detail;
}

function detailArrayToString(detail: unknown[]): string {
  const first = detail[0] as { loc?: unknown } | undefined;
  const field = Array.isArray(first?.loc) ? (first.loc[1] as unknown) : null;
  if (typeof field === 'string' && FIELD_MESSAGES[field]) {
    return FIELD_MESSAGES[field];
  }
  return 'Please check your booking details and try again.';
}

/**
 * Converts any thrown value from an API call into a human-readable string
 * that is always safe to render inside React (never an object or array).
 */
export function normalizeApiError(error: unknown): string {
  if (typeof error === 'string' && error.trim()) {
    return error;
  }

  const err = error as ApiErrorShape | undefined;
  if (!err || typeof err !== 'object') {
    return GENERIC_MESSAGE;
  }

  const detail = err.response?.data?.detail;
  if (typeof detail === 'string' && detail.trim()) {
    return friendlyDetail(detail);
  }
  if (Array.isArray(detail) && detail.length > 0) {
    return detailArrayToString(detail);
  }

  if (err.response) {
    switch (err.response.status) {
      case 401:
        return 'Your session has expired. Please log in again.';
      case 403:
        return 'You do not have access to this action.';
      case 404:
        return 'This chef is no longer available.';
      case 429:
        return 'Too many attempts. Please wait a minute and try again.';
      default:
        if ((err.response.status ?? 0) >= 500) {
          return 'Server problem. Please try again shortly.';
        }
        return GENERIC_MESSAGE;
    }
  }

  if (
    err.request ||
    (typeof err.message === 'string' && /network/i.test(err.message))
  ) {
    return 'Cannot reach the server. Check your connection and try again.';
  }

  return GENERIC_MESSAGE;
}
