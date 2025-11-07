# Tzafon Python SDK

[![PyPI version](https://img.shields.io/pypi/v/tzafon.svg)](https://pypi.org/project/tzafon/)

Remote browser and desktop automation. Control browsers and desktops programmatically through a simple Python API.

## Installation

```bash
pip install tzafon
```

## Quick Start

```python
from tzafon import Computer

client = Computer()  # Reads TZAFON_API_KEY from environment

# Create and control a browser instance
with client.create(kind="browser") as computer:
    computer.navigate("https://wikipedia.com")

    result = computer.screenshot()
    url = computer.get_screenshot_url(result)
    print(f"Screenshot: {url}")

    computer.click(100, 200)
    computer.type("Hello, world!")

    # Automatically terminates when exiting context
```

Set your API key:
```bash
export TZAFON_API_KEY="your-api-key"
```

Or use a `.env` file with [python-dotenv](https://pypi.org/project/python-dotenv/).

## Features

**Session Management**
- Context manager support for automatic cleanup
- Manual session control when needed
- Browser, desktop, and code environments

**Browser Actions**
- Navigation: `navigate(url)`
- Mouse: `click()`, `double_click()`, `right_click()`, `drag()`
- Keyboard: `type()`, `hotkey()`
- Viewport: `scroll()`, `set_viewport()`
- Capture: `screenshot()`, `html()`
- Debug: Execute shell commands with `debug()`

**Type Safety**
- Full type annotations for IDE autocomplete
- Pydantic models for responses
- TypedDict for request parameters
- Helper methods for result extraction

## Examples

### Browser Automation

```python
with client.create(kind="browser") as computer:
    # Navigate and interact
    computer.navigate("https://github.com/login")
    computer.click(300, 400)
    computer.type("username")
    computer.hotkey("Control", "a")  # Select all

    # Capture state
    html_result = computer.html()
    html = computer.get_html_content(html_result)

    # Execute commands
    debug_result = computer.debug("ls -la")
    output = computer.get_debug_response(debug_result)
```

### Manual Session Management

```python
computer = client.create(kind="browser")
try:
    computer.navigate("https://example.com")
    screenshot = computer.screenshot()
finally:
    computer.terminate()
```

### Async Support

```python
from tzafon import AsyncComputer

async with AsyncComputer() as client:
    computer = await client.computers.create(kind="browser")
    await client.computers.navigate(computer.id, url="https://example.com")
    await client.computers.terminate(computer.id)
```

## Advanced Usage

### Raw SDK Access

The simplified wrapper uses the generated SDK under the hood. You can access it directly:

```python
# Low-level API
response = client.computers.create(kind="browser")
client.computers.navigate(response.id, url="https://example.com")
result = client.computers.capture_screenshot(response.id)
client.computers.terminate(response.id)
```

### Error Handling

```python
import tzafon

try:
    with client.create(kind="browser") as computer:
        computer.navigate("https://example.com")
except tzafon.RateLimitError:
    print("Rate limit exceeded, back off")
except tzafon.AuthenticationError:
    print("Invalid API key")
except tzafon.APIError as e:
    print(f"API error: {e}")
```

### Configuration

```python
from tzafon import Computer

client = Computer(
    api_key="your-api-key",       # Or use TZAFON_API_KEY env var
    base_url="https://...",        # Optional: custom endpoint
    timeout=120.0,                 # Request timeout in seconds
    max_retries=2,                 # Retry failed requests
)
```

## API Reference

**Session Methods**
- `navigate(url)` - Navigate to URL
- `click(x, y)` - Click at coordinates
- `double_click(x, y)` - Double-click
- `right_click(x, y)` - Right-click
- `drag(x1, y1, x2, y2)` - Click and drag
- `type(text)` - Type text
- `hotkey(*keys)` - Press key combination
- `scroll(dx, dy)` - Scroll viewport
- `screenshot(base64=False)` - Capture screenshot
- `html(auto_detect_encoding=False)` - Get page HTML
- `debug(command, timeout_seconds=120, max_output_length=65536)` - Run shell command
- `set_viewport(width, height, scale_factor=1.0)` - Set viewport size
- `terminate()` - End session

**Helper Methods**
- `get_screenshot_url(result)` - Extract screenshot URL from result
- `get_html_content(result)` - Extract HTML from result
- `get_debug_response(result)` - Extract command output from result

## Error Codes

| Status | Error Type |
|--------|------------|
| 400 | `BadRequestError` |
| 401 | `AuthenticationError` |
| 403 | `PermissionDeniedError` |
| 404 | `NotFoundError` |
| 422 | `UnprocessableEntityError` |
| 429 | `RateLimitError` |
| ≥500 | `InternalServerError` |

## Documentation

- REST API: [docs.tzafon.ai](https://docs.tzafon.ai)
- Full API Reference: [api.md](api.md)
- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)

## Requirements

Python 3.8+

## License

See [LICENSE](LICENSE)
