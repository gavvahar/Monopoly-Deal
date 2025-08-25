# Business Hours Restriction

This document describes the business hours restriction feature implemented for the Monopoly Deal application.

## Overview

The Monopoly Deal application implements selective restrictions during standard business hours (9:00 AM - 5:00 PM EST, Monday-Friday only). The system distinguishes between hosting new game sessions and joining existing ones:

- **Hosting/Creating Sessions**: Restricted during business hours (requires admin bypass)
- **Joining Existing Sessions**: Allowed during business hours
- **Weekend Access**: All actions available on weekends

## Implementation Details

### Time Range
- **Restricted Hours**: 9:00 AM - 5:00 PM EST (Eastern Standard Time)
- **Restricted Days**: Monday through Friday only
- **Available Hours**: Before 9:00 AM and after 5:00 PM EST on weekdays
- **Weekend Access**: Saturdays and Sundays are available all day
- **Timezone**: Uses `US/Eastern` timezone with automatic DST handling

### Action-Based Restrictions

The system implements selective restrictions based on the type of action:

#### Hosting Actions (Restricted during business hours)
- **Login**: Required to create new sessions
- **Creating Game Sessions**: Starting new multiplayer games  
- **Starting Games**: Initiating gameplay for created sessions

#### Joining Actions (Allowed during business hours)
- **Joining Existing Sessions**: Participating in ongoing games
- **Game Play**: Drawing cards, playing cards, taking turns
- **Leaving Sessions**: Exiting from game sessions

### Protected Routes
The following routes have selective business hours restrictions:

#### Hosting Routes (Restricted during business hours)
- `/` (Home page - redirects to login)
- `/login` (GET and POST - needed for session creation)
- `/lobby` (GET - shows create game options)
- `/lobby` (POST with `action=create_game` or `action=start_game`)

#### Joining Routes (Allowed during business hours)
- `/lobby` (POST with `action=join_game` or `action=leave_game`)
- `/play/{session_code}` (GET and POST - joining existing games)

### Admin Bypass

Administrators can bypass the business hours restriction for hosting actions by:
1. Using the admin bypass form on the restriction page
2. Entering both the admin password and 6-digit 2FA code
3. Once bypassed, the session remains active for all actions until logout

The bypass uses Enhanced 2FA security with TOTP (Time-Based One-Time Password) authentication.

### User Experience

**During business hours:**
- **Hosting attempts**: Users see restriction page with clear messaging
- **Joining attempts**: Users can join existing sessions normally
- Clear distinction between "hosting" and "joining" in messaging
- Current EST time display for awareness
- Admin bypass form available for authorized hosting access

**Outside business hours:**
- All actions available normally
- No restrictions on hosting or joining
- Weekend access: All functionality available

## Technical Implementation

### Core Function
```python
def check_business_hours_restriction(request: Request, action_type="host"):
    """
    Check if the current time is within business hours and return response.
    
    Args:
        action_type: "host" for hosting/creating sessions (restricted), 
                    "join" for joining existing sessions (allowed)
    """
    # Check if admin bypass is active in session
    if request.session.get("admin_bypass"):
        return None

    # During business hours, only restrict hosting actions
    if is_business_hours():
        if action_type == "join":
            # Allow joining existing sessions during business hours
            return None
            
        # Restrict hosting/creating new sessions during business hours
        # ... show restriction page
```
    
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