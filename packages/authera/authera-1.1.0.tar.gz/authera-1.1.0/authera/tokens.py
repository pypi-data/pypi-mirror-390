from typing import Tuple, Optional

from rest_framework_simplejwt.tokens import RefreshToken


def issue_user_tokens(user_id: str, username: Optional[str] = None) -> Tuple[str, str, int, int]:
    """
    Issue access and refresh tokens using Simple JWT.
    Returns (access_token, refresh_token, access_max_age_seconds, refresh_max_age_seconds)
    """
    # Create a refresh token and attach custom claims
    refresh = RefreshToken()
    refresh["uid"] = str(user_id)
    if username is not None:
        refresh["username"] = username

    access = refresh.access_token

    access_token = str(access)
    refresh_token = str(refresh)
    access_max_age = int(access.lifetime.total_seconds())
    refresh_max_age = int(refresh.lifetime.total_seconds())

    return access_token, refresh_token, access_max_age, refresh_max_age


