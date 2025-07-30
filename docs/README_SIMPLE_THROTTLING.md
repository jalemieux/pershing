# Simple In-Memory Throttling System

## Overview

A lightweight, in-memory throttling system that protects your Flask authentication endpoints from abuse. No database required!

## Features

- **Simple & Fast**: In-memory storage, no database needed
- **Dual Protection**: Both IP and email-based throttling
- **Smart IP Handling**: Skips throttling for private IPs (development)
- **Configurable Limits**: Easy to adjust attempt limits
- **Thread-Safe**: Uses locks for concurrent access
- **Auto-Cleanup**: Automatically removes old attempts

## Configuration

Default limits in `app/throttling_service.py`:

```python
config = {
    'initiate_auth': {
        'max_attempts': 5,      # 5 attempts per hour
        'window_minutes': 60,   # 1 hour window
        'block_minutes': 30     # 30 minute block
    },
    'verify_code': {
        'max_attempts': 10,     # 10 attempts per hour
        'window_minutes': 60,   # 1 hour window
        'block_minutes': 60     # 1 hour block
    }
}
```

## Usage

### In Auth Routes

The throttling is already integrated into your auth routes:

```python
# Check throttling before proceeding
is_throttled, message = throttling_service.check_auth_throttling(email)
if is_throttled:
    flash(message)
    return redirect(url_for('auth.initiate_auth'))

# Record the attempt
throttling_service.record_auth_attempt(email)
```

### Testing

Run the test script to verify everything works:

```bash
python test_simple_throttling.py
```

### Monitoring

Get current statistics:

```python
stats = throttling_service.get_stats()
print(f"Total attempts: {stats['total_attempts']}")
print(f"Currently blocked: {stats['blocked_count']}")
print(f"Unique identifiers: {stats['unique_identifiers']}")
```

## How It Works

1. **Attempt Tracking**: Records attempts in memory with timestamps
2. **Window-based**: Only counts attempts within the configured time window
3. **Auto-cleanup**: Removes old attempts automatically
4. **Blocking**: Blocks after exceeding the limit for the configured duration
5. **Reset**: Clears all attempts after successful authentication

## Benefits

- **No Database**: Simple in-memory storage
- **Fast**: No database queries
- **Lightweight**: Minimal memory footprint
- **Thread-Safe**: Safe for concurrent requests
- **Development Friendly**: Skips throttling for private IPs

## User Experience

- **Clear Messages**: Users see exact time remaining
- **Progressive Blocks**: Longer blocks for repeated violations
- **Automatic Reset**: Blocks expire automatically
- **Success Reset**: All attempts reset after successful login

## Security Features

- **Brute Force Protection**: Prevents systematic attacks
- **IP Rotation Protection**: Blocks abuse from multiple IPs
- **Account Enumeration Protection**: Prevents discovery of valid emails
- **Proxy Support**: Handles X-Forwarded-For headers

## Files

- `app/throttling_service.py`: Main throttling service
- `app/routes/auth.py`: Updated with throttling integration
- `test_simple_throttling.py`: Test script

## Limitations

- **Memory Only**: Data is lost on server restart
- **Single Server**: Won't work across multiple server instances
- **No Persistence**: No long-term tracking

## For Production

For production with multiple servers, consider:
- Redis for shared state
- Database-backed throttling
- Distributed rate limiting

## Quick Test

```bash
# Test the system
python test_simple_throttling.py

# Expected output:
# 🎉 All tests passed!
```

That's it! Your authentication endpoints are now protected with simple, effective throttling. 