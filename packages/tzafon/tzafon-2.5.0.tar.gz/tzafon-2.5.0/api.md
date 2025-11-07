# Computers

Types:

```python
from tzafon.types import (
    ActionResult,
    ComputerResponse,
    ComputerListResponse,
    ComputerExecuteBatchResponse,
    ComputerKeepAliveResponse,
)
```

Methods:

- <code title="post /computers">client.computers.<a href="./src/tzafon/resources/computers.py">create</a>(\*\*<a href="src/tzafon/types/computer_create_params.py">params</a>) -> <a href="./src/tzafon/types/computer_response.py">ComputerResponse</a></code>
- <code title="get /computers/{id}">client.computers.<a href="./src/tzafon/resources/computers.py">retrieve</a>(id) -> <a href="./src/tzafon/types/computer_response.py">ComputerResponse</a></code>
- <code title="get /computers">client.computers.<a href="./src/tzafon/resources/computers.py">list</a>() -> <a href="./src/tzafon/types/computer_list_response.py">ComputerListResponse</a></code>
- <code title="post /computers/{id}/screenshot">client.computers.<a href="./src/tzafon/resources/computers.py">capture_screenshot</a>(id, \*\*<a href="src/tzafon/types/computer_capture_screenshot_params.py">params</a>) -> <a href="./src/tzafon/types/action_result.py">ActionResult</a></code>
- <code title="post /computers/{id}/click">client.computers.<a href="./src/tzafon/resources/computers.py">click</a>(id, \*\*<a href="src/tzafon/types/computer_click_params.py">params</a>) -> <a href="./src/tzafon/types/action_result.py">ActionResult</a></code>
- <code title="get /computers/{id}/ws">client.computers.<a href="./src/tzafon/resources/computers.py">connect_websocket</a>(id) -> None</code>
- <code title="post /computers/{id}/debug">client.computers.<a href="./src/tzafon/resources/computers.py">debug</a>(id, \*\*<a href="src/tzafon/types/computer_debug_params.py">params</a>) -> <a href="./src/tzafon/types/action_result.py">ActionResult</a></code>
- <code title="post /computers/{id}/double-click">client.computers.<a href="./src/tzafon/resources/computers.py">double_click</a>(id, \*\*<a href="src/tzafon/types/computer_double_click_params.py">params</a>) -> <a href="./src/tzafon/types/action_result.py">ActionResult</a></code>
- <code title="post /computers/{id}/drag">client.computers.<a href="./src/tzafon/resources/computers.py">drag</a>(id, \*\*<a href="src/tzafon/types/computer_drag_params.py">params</a>) -> <a href="./src/tzafon/types/action_result.py">ActionResult</a></code>
- <code title="post /computers/{id}/execute">client.computers.<a href="./src/tzafon/resources/computers.py">execute_action</a>(id, \*\*<a href="src/tzafon/types/computer_execute_action_params.py">params</a>) -> <a href="./src/tzafon/types/action_result.py">ActionResult</a></code>
- <code title="post /computers/{id}/batch">client.computers.<a href="./src/tzafon/resources/computers.py">execute_batch</a>(id, \*\*<a href="src/tzafon/types/computer_execute_batch_params.py">params</a>) -> <a href="./src/tzafon/types/computer_execute_batch_response.py">ComputerExecuteBatchResponse</a></code>
- <code title="post /computers/{id}/html">client.computers.<a href="./src/tzafon/resources/computers.py">get_html</a>(id, \*\*<a href="src/tzafon/types/computer_get_html_params.py">params</a>) -> <a href="./src/tzafon/types/action_result.py">ActionResult</a></code>
- <code title="post /computers/{id}/keepalive">client.computers.<a href="./src/tzafon/resources/computers.py">keep_alive</a>(id) -> <a href="./src/tzafon/types/computer_keep_alive_response.py">ComputerKeepAliveResponse</a></code>
- <code title="post /computers/{id}/navigate">client.computers.<a href="./src/tzafon/resources/computers.py">navigate</a>(id, \*\*<a href="src/tzafon/types/computer_navigate_params.py">params</a>) -> <a href="./src/tzafon/types/action_result.py">ActionResult</a></code>
- <code title="post /computers/{id}/hotkey">client.computers.<a href="./src/tzafon/resources/computers.py">press_hotkey</a>(id, \*\*<a href="src/tzafon/types/computer_press_hotkey_params.py">params</a>) -> <a href="./src/tzafon/types/action_result.py">ActionResult</a></code>
- <code title="post /computers/{id}/right-click">client.computers.<a href="./src/tzafon/resources/computers.py">right_click</a>(id, \*\*<a href="src/tzafon/types/computer_right_click_params.py">params</a>) -> <a href="./src/tzafon/types/action_result.py">ActionResult</a></code>
- <code title="post /computers/{id}/scroll">client.computers.<a href="./src/tzafon/resources/computers.py">scroll_viewport</a>(id, \*\*<a href="src/tzafon/types/computer_scroll_viewport_params.py">params</a>) -> <a href="./src/tzafon/types/action_result.py">ActionResult</a></code>
- <code title="post /computers/{id}/viewport">client.computers.<a href="./src/tzafon/resources/computers.py">set_viewport</a>(id, \*\*<a href="src/tzafon/types/computer_set_viewport_params.py">params</a>) -> <a href="./src/tzafon/types/action_result.py">ActionResult</a></code>
- <code title="get /computers/{id}/events">client.computers.<a href="./src/tzafon/resources/computers.py">stream_events</a>(id) -> None</code>
- <code title="get /computers/{id}/screencast">client.computers.<a href="./src/tzafon/resources/computers.py">stream_screencast</a>(id) -> None</code>
- <code title="delete /computers/{id}">client.computers.<a href="./src/tzafon/resources/computers.py">terminate</a>(id) -> None</code>
- <code title="post /computers/{id}/type">client.computers.<a href="./src/tzafon/resources/computers.py">type_text</a>(id, \*\*<a href="src/tzafon/types/computer_type_text_params.py">params</a>) -> <a href="./src/tzafon/types/action_result.py">ActionResult</a></code>
