# Business Hours Restriction

This document describes the business hours restriction feature implemented for the Monopoly Deal application.

## Overview

The Monopoly Deal application is restricted during standard business hours (9:00 AM - 5:00 PM EST) to prevent usage during work hours. Users attempting to access the application during this time will see a friendly message explaining the restriction.

## Implementation Details

### Time Range
- **Restricted Hours**: 9:00 AM - 5:00 PM EST (Eastern Standard Time)
- **Available Hours**: Before 9:00 AM and after 5:00 PM EST
- **Timezone**: Uses `US/Eastern` timezone with automatic DST handling

### Protected Routes
The following routes are protected by business hours restrictions:
- `/` (Home page)
- `/login` (GET and POST)
- `/lobby` (GET and POST) 
- `/play/*` (All game play routes)

### User Experience
When accessing the application during business hours, users will see:
- Clear message about the restriction
- Current EST time display
- Information about when the service will be available again
- Consistent styling with the rest of the application

## Technical Implementation

### Core Function
```python
def is_business_hours():
    """
    Check if the current time is within business hours (9 AM - 5 PM EST).
    Returns True if within business hours, False otherwise.
    """
    est = pytz.timezone('US/Eastern')
    current_time = datetime.now(est)
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

## Testing

Comprehensive tests are available in `test_business_hours.py` covering:
- Business hours detection at various times
- Route restrictions during business hours
- Normal access outside business hours
- Edge cases (exactly 9 AM, 5 PM)
- Current time display functionality

Run tests with:
```bash
python test_business_hours.py
```

## Configuration

The business hours are currently hardcoded as 9 AM - 5 PM EST. To modify:
1. Update the `is_business_hours()` function in `main.py`
2. Update the message in `templates/business_hours.html`
3. Update the tests in `test_business_hours.py`

## Timezone Handling

The implementation uses `pytz` for robust timezone handling:
- Automatically handles Eastern Standard Time (EST) and Eastern Daylight Time (EDT)
- Uses `US/Eastern` timezone which handles DST transitions automatically
- All times are normalized to Eastern timezone regardless of server location

## Dependencies

- `pytz` - Added to `requirements.txt` for timezone support
- `datetime` - Standard library for time operations