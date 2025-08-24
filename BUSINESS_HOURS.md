# Business Hours Restriction

This document describes the business hours restriction feature implemented for the Monopoly Deal application.

## Overview

The Monopoly Deal application is restricted during standard business hours (9:00 AM - 5:00 PM EST, Monday-Friday only) to prevent usage during work hours. Users attempting to access the application during this time will see a friendly message explaining the restriction, with an option for admin bypass.

## Implementation Details

### Time Range
- **Restricted Hours**: 9:00 AM - 5:00 PM EST (Eastern Standard Time)
- **Restricted Days**: Monday through Friday only
- **Available Hours**: Before 9:00 AM and after 5:00 PM EST on weekdays
- **Weekend Access**: Saturdays and Sundays are available all day
- **Timezone**: Uses `US/Eastern` timezone with automatic DST handling

### Protected Routes
The following routes are protected by business hours restrictions:
- `/` (Home page)
- `/login` (GET and POST)
- `/lobby` (GET and POST) 
- `/play/*` (All game play routes)

### Admin Bypass
Administrators can bypass the business hours restriction by:
1. Entering the admin password on the restriction page
2. Once bypassed, the session will remain active until logout
3. The bypass uses the same admin password configured in environment variables

### User Experience
When accessing the application during business hours, users will see:
- Clear message about the restriction (Monday-Friday only)
- Current EST time display
- Information about when the service will be available again
- Admin bypass form for authorized access
- Consistent styling with the rest of the application

## Technical Implementation

### Core Function
```python
def is_business_hours():
    """
    Check if the current time is within business hours (9 AM - 5 PM EST, Monday-Friday).
    Returns True if within business hours, False otherwise.
    """
    est = pytz.timezone('US/Eastern')
    current_time = datetime.now(est)
    
    # Check if it's a weekday (Monday=0 to Friday=4)
    # Saturday=5, Sunday=6 should always be available
    weekday = current_time.weekday()
    if weekday >= 5:  # Weekend (Saturday=5, Sunday=6)
        return False
    
    # Check if it's between 9 AM and 5 PM EST on weekdays
    hour = current_time.hour
    return 9 <= hour < 17  # 9 AM to 4:59 PM (5 PM exclusive)
```

### Route Protection
Each protected route includes a business hours check:
```python
# Check business hours restriction
restriction_response = check_business_hours_restriction(request)
if restriction_response:
    return restriction_response
```

### Admin Bypass Implementation
The admin bypass functionality includes:
- Session-based bypass flag to avoid repeated password entry
- Admin password validation using environment variables
- Automatic redirect to originally requested page after successful bypass

## Testing

Comprehensive tests are available in `test_business_hours.py` covering:
- Business hours detection at various times and days
- Weekend access (full day availability)
- Route restrictions during weekday business hours
- Normal access outside business hours
- Edge cases (exactly 9 AM, 5 PM)
- Admin bypass functionality (correct/incorrect passwords)
- Current time display functionality

Run tests with:
```bash
python test_business_hours.py
```

## Configuration

### Business Hours
The business hours are currently configured as:
- **Hours**: 9 AM - 5 PM EST
- **Days**: Monday through Friday only
- **Weekends**: Always available

To modify:
1. Update the `is_business_hours()` function in `main.py`
2. Update the message in `templates/business_hours.html`
3. Update the tests in `test_business_hours.py`

### Admin Bypass
The admin bypass uses the `ADMIN_PASSWORD` environment variable. To configure:
1. Set `ADMIN_PASSWORD` in your environment or `.env` file
2. The same password is used for both admin login and business hours bypass

## Timezone Handling

The implementation uses `pytz` for robust timezone handling:
- Automatically handles Eastern Standard Time (EST) and Eastern Daylight Time (EDT)
- Uses `US/Eastern` timezone which handles DST transitions automatically
- All times are normalized to Eastern timezone regardless of server location

## Dependencies

- `pytz` - Added to `requirements.txt` for timezone support
- `datetime` - Standard library for time operations

## Security Considerations

- Admin bypass password is validated against environment variables
- Session-based bypass prevents password replay attacks
- No password is stored in browser or transmitted unnecessarily
- Bypass session is cleared on logout