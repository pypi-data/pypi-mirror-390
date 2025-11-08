<p align="center">
  <img src="https://tigrmail.com/logo@3x.webp" alt="Tigrmail Logo" width="200" />
</p>

<p align="center">
  <a href="https://tigrmail.com?utm_source=github&utm_medium=readme">Website</a> |
  <a href="https://docs.tigrmail.com">API Docs</a> |
  <a href="https://github.com/furionix-labs/playwright-email-verification-example">Demo</a>
</p>

# Tigrmail SDK

Tigrmail SDK is a Python library for automating email verification workflows. It allows you to generate temporary inboxes and poll for email messages with customizable filters. This library is ideal for testing email-based features or automating email verification processes.

> If you are working in a different programming language, you can still access all features by integrating directly with [our API](https://docs.tigrmail.com).

## Features

- Generate temporary inboxes.
- Poll for the next email message with advanced filtering options (e.g., by subject, sender email, or domain).
- Built-in error handling for API interactions.
- Automatic retry logic for HTTP requests.

## Installation

```bash
pip install tigrmail
```

## Usage

### Importing the Library

```python
from tigrmail import Tigrmail, TigrmailError
```

### Creating an Instance

To use the library, retrieve your API token from [our console](https://console.tigrmail.com?utm_source=github_python&utm_medium=readme) and create a `Tigrmail` instance using that token:

```python
tigrmail = Tigrmail(token="your-api-token")
```

### Generating a Temporary Inbox

```python
email_address = tigrmail.create_email_address()
print(email_address)  # <random-email-address>@den.tigrmail.com
```

### Polling for the Next Email Message

You can poll for the next email message using filters:

```python
message = tigrmail.poll_next_message(
    inbox=email_address,
    subject={"contains": "Verification"},
    from_={"email": "noreply@example.com"},
)

print(f"Received email: {message['subject']}")
```

### Playwright Integration Example

For a complete example of using Tigrmail SDK with Playwright for automated email verification testing, check out our [Playwright Email Verification Example](https://github.com/furionix-labs/playwright-python-email-verification-example).

### Context Manager Usage

The library supports Python's context manager protocol for automatic resource cleanup:

```python
from tigrmail import Tigrmail, TigrmailError

try:
    with Tigrmail(token="your-api-token") as tigrmail:
        inbox = tigrmail.create_email_address()
        message = tigrmail.poll_next_message(
            inbox=inbox,
            subject={"contains": "Verification"},
            from_={"email": "noreply@example.com"},
        )
        print(message["subject"])
except TigrmailError as error:
    print(f"Error: {error.general_message}")
```

## API Reference

### `Tigrmail.create_email_address() -> str`

Generates a temporary email address.

### `Tigrmail.poll_next_message(inbox, subject=None, from_=None) -> dict`

Polls for the next email message with optional filters:
- `inbox` (str): The email address to poll for messages
- `subject` (dict, optional): Filter by subject line
  - `{"contains": str}` - Subject contains the specified string
  - `{"equals": str}` - Subject exactly matches the specified string
- `from_` (dict, optional): Filter by sender
  - `{"email": str}` - From a specific email address
  - `{"domain": str}` - From any address at the specified domain

Returns an `EmailMessage` dictionary with message details.

## Error Handling

The library raises `TigrmailError` for API-related issues. You can catch and handle these errors as follows:

```python
try:
    inbox = tigrmail.create_email_address()
except TigrmailError as error:
    print(f"Error: {error.general_message}")
except Exception as error:
    print(f"Unexpected error: {error}")
```

## Technical Details

- Base URL: `https://api.tigrmail.com`
- Timeout: 180s
- Retries: 3 (exponential backoff) on all HTTP/transport errors
- Uses `httpx` under the hood with simple retry logic

## License

This project is licensed under the MIT License.
