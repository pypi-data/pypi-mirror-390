# Lam

Types:

```python
from raccoonai.types import LamRunResponse
```

Methods:

- <code title="post /lam/run">client.lam.<a href="./src/raccoonai/resources/lam/lam.py">run</a>(\*\*<a href="src/raccoonai/types/lam_run_params.py">params</a>) -> <a href="./src/raccoonai/types/lam_run_response.py">LamRunResponse</a></code>

## Tasks

Types:

```python
from raccoonai.types.lam import TaskAllResponse, TaskMediaResponse
```

Methods:

- <code title="get /lam/tasks">client.lam.tasks.<a href="./src/raccoonai/resources/lam/tasks.py">all</a>(\*\*<a href="src/raccoonai/types/lam/task_all_params.py">params</a>) -> <a href="./src/raccoonai/types/lam/task_all_response.py">TaskAllResponse</a></code>
- <code title="get /lam/tasks/{taskId}/media">client.lam.tasks.<a href="./src/raccoonai/resources/lam/tasks.py">media</a>(task_id) -> <a href="./src/raccoonai/types/lam/task_media_response.py">TaskMediaResponse</a></code>

# Tail

## Users

Types:

```python
from raccoonai.types.tail import UserCreateResponse, UserAllResponse, UserStatusResponse
```

Methods:

- <code title="post /tail/users/create">client.tail.users.<a href="./src/raccoonai/resources/tail/users.py">create</a>(\*\*<a href="src/raccoonai/types/tail/user_create_params.py">params</a>) -> <a href="./src/raccoonai/types/tail/user_create_response.py">UserCreateResponse</a></code>
- <code title="get /tail/users">client.tail.users.<a href="./src/raccoonai/resources/tail/users.py">all</a>(\*\*<a href="src/raccoonai/types/tail/user_all_params.py">params</a>) -> <a href="./src/raccoonai/types/tail/user_all_response.py">UserAllResponse</a></code>
- <code title="get /tail/app/auth-status">client.tail.users.<a href="./src/raccoonai/resources/tail/users.py">status</a>(\*\*<a href="src/raccoonai/types/tail/user_status_params.py">params</a>) -> <a href="./src/raccoonai/types/tail/user_status_response.py">UserStatusResponse</a></code>

## Apps

Types:

```python
from raccoonai.types.tail import AppAllResponse, AppLinkedResponse
```

Methods:

- <code title="get /tail/apps">client.tail.apps.<a href="./src/raccoonai/resources/tail/apps.py">all</a>() -> <a href="./src/raccoonai/types/tail/app_all_response.py">AppAllResponse</a></code>
- <code title="get /tail/linked-apps">client.tail.apps.<a href="./src/raccoonai/resources/tail/apps.py">linked</a>(\*\*<a href="src/raccoonai/types/tail/app_linked_params.py">params</a>) -> <a href="./src/raccoonai/types/tail/app_linked_response.py">AppLinkedResponse</a></code>

# Fleet

## Sessions

Types:

```python
from raccoonai.types.fleet import (
    SessionCreateResponse,
    SessionAllResponse,
    SessionLogsResponse,
    SessionMediaResponse,
    SessionStatusResponse,
    SessionTerminateResponse,
)
```

Methods:

- <code title="post /sessions/create">client.fleet.sessions.<a href="./src/raccoonai/resources/fleet/sessions.py">create</a>(\*\*<a href="src/raccoonai/types/fleet/session_create_params.py">params</a>) -> <a href="./src/raccoonai/types/fleet/session_create_response.py">SessionCreateResponse</a></code>
- <code title="get /sessions">client.fleet.sessions.<a href="./src/raccoonai/resources/fleet/sessions.py">all</a>(\*\*<a href="src/raccoonai/types/fleet/session_all_params.py">params</a>) -> <a href="./src/raccoonai/types/fleet/session_all_response.py">SessionAllResponse</a></code>
- <code title="get /sessions/{session_id}/logs">client.fleet.sessions.<a href="./src/raccoonai/resources/fleet/sessions.py">logs</a>(session_id) -> <a href="./src/raccoonai/types/fleet/session_logs_response.py">SessionLogsResponse</a></code>
- <code title="get /sessions/{sessionId}/media">client.fleet.sessions.<a href="./src/raccoonai/resources/fleet/sessions.py">media</a>(session_id) -> <a href="./src/raccoonai/types/fleet/session_media_response.py">SessionMediaResponse</a></code>
- <code title="get /sessions/{session_id}/status">client.fleet.sessions.<a href="./src/raccoonai/resources/fleet/sessions.py">status</a>(session_id) -> <a href="./src/raccoonai/types/fleet/session_status_response.py">SessionStatusResponse</a></code>
- <code title="delete /sessions/{session_id}/terminate">client.fleet.sessions.<a href="./src/raccoonai/resources/fleet/sessions.py">terminate</a>(session_id) -> <a href="./src/raccoonai/types/fleet/session_terminate_response.py">SessionTerminateResponse</a></code>

## Extensions

Types:

```python
from raccoonai.types.fleet import (
    ExtensionAllResponse,
    ExtensionGetResponse,
    ExtensionUploadResponse,
)
```

Methods:

- <code title="delete /extensions/{extensionId}">client.fleet.extensions.<a href="./src/raccoonai/resources/fleet/extensions.py">delete</a>(extension_id) -> object</code>
- <code title="get /extensions">client.fleet.extensions.<a href="./src/raccoonai/resources/fleet/extensions.py">all</a>() -> <a href="./src/raccoonai/types/fleet/extension_all_response.py">ExtensionAllResponse</a></code>
- <code title="get /extensions/{extensionId}">client.fleet.extensions.<a href="./src/raccoonai/resources/fleet/extensions.py">get</a>(extension_id) -> <a href="./src/raccoonai/types/fleet/extension_get_response.py">ExtensionGetResponse</a></code>
- <code title="post /extensions">client.fleet.extensions.<a href="./src/raccoonai/resources/fleet/extensions.py">upload</a>(\*\*<a href="src/raccoonai/types/fleet/extension_upload_params.py">params</a>) -> <a href="./src/raccoonai/types/fleet/extension_upload_response.py">ExtensionUploadResponse</a></code>
