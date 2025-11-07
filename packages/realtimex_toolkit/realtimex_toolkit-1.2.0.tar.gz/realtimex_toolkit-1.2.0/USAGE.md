# Toolkit Usage Guide

## Overview

The toolkit provides utilities for accessing flow variables within Code Interpreter steps. Variables are passed via a JSON file, and the toolkit handles both simple keys and nested dotted paths.

## Installation

Copy `toolkit/__init__.py` to your `realtimex_toolkit` package.

## Usage in Code Interpreter

### Basic Usage

```python
from realtimex_toolkit import get_flow_variable

# Get a simple variable
time = get_flow_variable('time')
# Returns: "3:42:58 PM"

# Get a nested variable using dotted path
user_email = get_flow_variable('user.email')
# Returns: "taicaidev@rta.vn"

user_name = get_flow_variable('user.name')
# Returns: "taicaidev_rta_vn"
```

### With Default Values

```python
# Provide a default value if variable doesn't exist
theme = get_flow_variable('user.theme', 'light')
# Returns: 'light' if user.theme is not set

bio = get_flow_variable('user.bio', '[No bio provided]')
```

### Get All Variables

```python
# Get all variables as a dictionary
all_vars = get_flow_variable()
# Returns: {'time': '...', 'user': {'email': '...', 'name': '...'}, ...}
```

## Variable Context Structure

When your flow executes, variables are structured as:

```json
{
  "time": "3:42:58 PM",
  "date": "November 7, 2025",
  "datetime": "Friday, November 7, 2025 3:42 PM",
  "user": {
    "name": "taicaidev_rta_vn",
    "email": "taicaidev@rta.vn",
    "bio": "[User bio is empty]"
  },
  "custom_var": "value",
  "api_response": {...}
}
```

## Access Patterns

### ✅ Recommended: Dotted Notation

```python
get_flow_variable('user.email')        # Nested access
get_flow_variable('user.name')         # Nested access
get_flow_variable('time')              # Top-level access
```

### ⚠️ Legacy: Direct Dictionary Access

For backwards compatibility, flat keys still work:

```python
get_flow_variable('flat_key')  # Works for non-nested variables
```

## Examples

### Example 1: Personalized Greeting

```python
from realtimex_toolkit import get_flow_variable

user_name = get_flow_variable('user.name', 'User')
user_email = get_flow_variable('user.email')

print(f"<output>Hello, {user_name}!")
print(f"Your email is: {user_email}</output>")
```

### Example 2: Conditional Logic

```python
from realtimex_toolkit import get_flow_variable

user_bio = get_flow_variable('user.bio')

if user_bio == "[User bio is empty]":
    print("<output>Please update your profile bio</output>")
else:
    print(f"<output>Your bio: {user_bio}</output>")
```

### Example 3: Working with API Responses

```python
from realtimex_toolkit import get_flow_variable

# Assuming api_response is a nested object
api_data = get_flow_variable('api_response', {})

if api_data:
    status = api_data.get('status')
    print(f"<output>API Status: {status}</output>")
else:
    print("<output>No API response available</output>")
```

## Error Handling

The function is designed to be safe and never raises exceptions:

```python
# Non-existent variable returns None
value = get_flow_variable('does.not.exist')
# Returns: None

# Non-existent with default
value = get_flow_variable('does.not.exist', 'default')
# Returns: 'default'

# Invalid payload file returns default
value = get_flow_variable('any.var', 'fallback')
# Returns: 'fallback' if payload can't be loaded
```

## Implementation Notes

- **Nested Resolution**: Dotted paths like `'user.email'` are resolved by traversing the nested dictionary structure
- **Backwards Compatible**: Flat keys are supported for legacy flows
- **Safe**: Always returns a value (either found value, default_value, or None)
- **No Exceptions**: All errors are caught and handled gracefully