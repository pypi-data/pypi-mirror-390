# Authera — Django Authentication (Clerk‑style)

Authera is a modern authentication and user management package for Django that enables Clerk‑style, step‑based auth flows using Django REST Framework and SimpleJWT.

## Key features

- Pluggable, multi‑step authentication scenarios
- First‑class Django REST Framework endpoints
- JWT issuance and refresh via djangorestframework‑simplejwt
- Stateless step tracking using Django cache
- Minimal, extensible building blocks for custom auth UX

## Requirements

- Python >= 3.9
- Django >= 4.2
- djangorestframework >= 3.15
- djangorestframework-simplejwt >= 5.3.0

## Installation

```bash
pip install authera
```

Or install from source in editable mode:

```bash
pip install -e .
```

## Quickstart

1. Add apps to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "rest_framework",
    "rest_framework_simplejwt",
    "authera",
]
```

2. Configure DRF + SimpleJWT (recommended):

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}
```

3. Define your user step scenarios:

Authera ships with a simple username/password scenario you can start with. You can add more scenarios or implement your own later.

```python
# settings.py
from authera.scenario import UsernamePasswordScenario

USER_STEP_SCENARIO = [
    # name, key, and TTL (seconds) for the next‑step state per user
    UsernamePasswordScenario(
        name="Username & Password",
        key="username-password",
        each_user_TTL=300,
    ),
]
```

4. Wire up URLs:

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    path("auth/", include("authera.urls")),
]
```

## Available endpoints

Base path assumes `auth/` as shown above.

- GET `auth/options/`
  - Returns the available scenarios and their JSON Schemas for client‑side validation and rendering.
- POST `auth/validate/<scenario_key>`
  - Validates user input for the given scenario step. If it is the final step, returns tokens and user info. Otherwise returns a signed payload and `user_id`, and advances the user to the next step.
- POST `auth/refresh/`
  - Exchanges a valid refresh token for new access and refresh tokens.

## Request/response examples

1. Get available options (schemas):

```bash
curl -X GET http://localhost:8000/auth/options/
```

Example response:

```json
{
  "username-password": {
    "type": "object",
    "properties": {
      "username": { "type": "string", "minLength": 3, "maxLength": 255 },
      "password": { "type": "string", "minLength": 8, "maxLength": 255 }
    },
    "required": ["username", "password"]
  }
}
```

2. Validate a step (username‑password):

```bash
curl -X POST http://localhost:8000/auth/validate/username-password \
  -H "Content-Type: application/json" \
  -d '{
    "options": { "username": "alice", "password": "S3cretPass!" }
  }'
```

If this is the final step, you’ll receive tokens and user info:

```json
{
  "access_token": "<jwt>",
  "refresh_token": "<jwt>",
  "token_type": "Bearer",
  "expires_in": 900,
  "user": {
    "id": 1,
    "username": "alice",
    "permits": ["staff", "editor"]
  }
}
```

3. Refresh tokens:

```bash
curl -X POST http://localhost:8000/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<jwt>"
  }'
```

Response:

```json
{
  "access_token": "<new_access_jwt>",
  "refresh_token": "<new_refresh_jwt>",
  "token_type": "Bearer",
  "expires_in": 900
}
```

## Extending: create a custom scenario

Implement your own step by subclassing `BaseScenario` and adding it to `USER_STEP_SCENARIO`.

```python
from rest_framework.response import Response
from authera.utils import BaseScenario

class EmailOtpScenario(BaseScenario):
    schema = {
        "type": "object",
        "properties": { "email": { "type": "string", "format": "email" }, "otp": { "type": "string" } },
        "required": ["email", "otp"]
    }

    def __init__(self):
        super().__init__(name="Email OTP", key="email-otp", each_user_TTL=300)

    def validate(self, user_payload, scenario_options) -> Response:
        # Validate OTP for the provided email; return 200 to advance, otherwise non‑200
        return Response()

    def get_user(self, user_id, options):
        # Return a Django user instance when this is the last step
        ...
```

## Security notes

- Always use HTTPS in production.
- Configure reasonable lifetimes for access and refresh tokens.
- Consider rotating refresh tokens and revocation strategies depending on risk profile.
- Ensure cache backend is correctly configured for step‑state tracking.

## Development

Run a local Django project that includes `authera`, then exercise the endpoints with the examples above.

## Contributing

Issues and PRs are welcome. Please open an issue to discuss substantial changes first.

## License

MIT © Algonouir
