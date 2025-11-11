import logging
from typing import Any, Dict

import jwt
from django.contrib.auth import get_user_model, validators
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import HttpRequest
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.plumbing import build_bearer_security_scheme_object
from rest_framework import authentication

import smoothglue.authentication.defaults as app_defaults
from smoothglue.core.utils import get_setting

logger = logging.getLogger(__name__)


def decode_jwt(request: HttpRequest) -> Dict[str, Any]:
    """
    Decodes the JWT token from the HTTP request's authorization header.
    This function expects the token to be sent either as a Bearer token
    in the 'Authorization' header or directly in the 'Jwt' header.
    Verification of the token is not performed as it is handled externally
    by Istio and Keycloak before the request reaches the docker container.

    Parameters:
    request (HttpRequest): The HTTP request object containing the JWT token.

    Returns:
    Dict[str, Any]: The decoded JWT token.

    Raises:
    ValueError: If no JWT token is found in the headers.
    """
    encoded_auth_header = request.headers.get("Authorization")
    encoded_jwt_header = request.headers.get("Jwt")
    bearer_prefix = "Bearer "

    if encoded_auth_header and encoded_auth_header.startswith(bearer_prefix):
        token = encoded_auth_header[len(bearer_prefix) :]
    elif encoded_jwt_header:
        token = encoded_jwt_header
    else:
        raise ValueError("No JWT provided in header.")

    try:
        auth_header = jwt.decode(token, options={"verify_signature": False})
    except jwt.DecodeError as e:
        # pylint: disable=W0707
        raise ValueError(f"Invalid JWT token: {e}")

    return auth_header


def get_unknown_user():
    """
    For local development, a valid JWT is not present when testing the
    backend system, therefore use an UnknownUser as default user. This
    also serves as a fallbcak if a JWT is not sent from Istio.

    This fallback will allow the system to return view only data but
    not allow the user to add/update/delete anything.

    NOTE: No type specified because Django user management magic means
    specifying the type as 'User' is bad practice. Embrace magic.
    """
    user = get_user_model().objects.get_or_create(
        username="UnknownUser",
        email=get_setting("SINGLE_USER_DEFAULT_EMAIL", app_defaults),
        is_superuser=True,
        is_staff=True,
        defaults={
            "first_name": "Unknown",
            "last_name": "User",
            "data": {
                "rank": "N/A",
                "usercertificate": "N/A",
                "affiliation": "N/A",
            },
        },
    )[0]
    return user


class PlatformAuthentication(authentication.BaseAuthentication):
    """
    All authorization for Platform comes through the Authorization
    header. Therefore, the need for Django model control is not necessary
    as we can tie a user with a JWT to a Django user.
    """

    def authenticate(self, request: HttpRequest) -> tuple[Any, bool] | None:
        if get_setting("ENABLE_SINGLE_USER_MODE", app_defaults):
            return (get_unknown_user(), None)

        jwt_header = request.headers.get("Authorization") or request.headers.get("Jwt")

        if jwt_header:
            jwt_decoded = decode_jwt(request)
            email = jwt_decoded.get("email")
            preferred_username = jwt_decoded.get(
                "preferred_username", email.split("@")[0]
            )

            if not self.is_valid_email(email) or not self.is_valid_username(
                preferred_username
            ):
                return None

            user, created = get_user_model().objects.update_or_create(
                username=preferred_username.replace(" ", "."),
                defaults={
                    "first_name": jwt_decoded.get("given_name", ""),
                    "last_name": jwt_decoded.get("family_name", ""),
                    "email": email,
                    "data": {
                        "rank": jwt_decoded.get("rank", "N/A"),
                        "usercertificate": jwt_decoded.get("usercertificate", "N/A"),
                        "affiliation": jwt_decoded.get("affiliation", "N/A"),
                    },
                },
            )

            return (user, created)

        return None

    def is_valid_email(self, email):
        """
        Checks if email passes our validation rules
        """
        try:
            validate_email(email)
            return True
        except ValidationError:
            logger.info("Email failed unicode validator", stack_info=True)
            return False

    def is_valid_username(self, username):
        """
        Checks if username passes our validation rules
        """
        try:
            username_validator = validators.UnicodeUsernameValidator()
            username_validator(username)
            return True
        except ValidationError:
            logger.info("Username failed unicode validator", stack_info=True)
            return False


class PlatformAuthenticationScheme(OpenApiAuthenticationExtension):
    """
    Custom class for handling authentication and authorization beyond OpenAPI specification.
    """

    target_class = "smoothglue.authentication.auth.PlatformAuthentication"
    name = "tokenAuth"
    match_subclasses = True
    priority = -1

    def get_security_definition(self, auto_schema):
        return build_bearer_security_scheme_object(
            header_name="Authorization",
            token_prefix="Bearer",
        )


class RootAdminBackend(ModelBackend):
    """
    Django authentication backend to allow setting a superuser username and password via settings.

    Allows a user to authenticate using the username `settings.ROOT_ADMIN_USERNAME`, and
    password `settings.ROOT_ADMIN_PASSWORD`. Useful for creating a bootstrap user in situations
    where setting an environment variable may be preferable to creating a static fixture,
    or having to manually run `manage.py createsuperuser`.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        username_valid = username == get_setting("ROOT_ADMIN_USERNAME", app_defaults)
        admin_password = get_setting("ROOT_ADMIN_PASSWORD", app_defaults)
        pwd_valid = admin_password is not None and password == admin_password
        if username_valid and pwd_valid:
            user, _ = get_user_model().objects.get_or_create(username=username)
            user.email = "admin@localhost"
            user.is_staff = True
            user.is_superuser = True
            user.save()
            return user
        return None


def platform_authentication_middleware(get_response):
    """
    Middleware which acts as a wrapper for smoothglue.authentication.auth.PlatformAuthentication.

    smoothglue.authentication.auth.PlatformAuthentication is a DRF authentication backend to allow
    authentication via JWT. This middleware extends the functionality of PlatformAuthentication from
    just being a DRF authentication mechanism to be able to authenticate any view.
    """

    def middleware(request):
        authenticated_user = hasattr(request, "user") and request.user.is_authenticated
        # pylint: disable=protected-access
        cached_user = (
            hasattr(request, "_cached_user") and request._cached_user.is_authenticated
        )
        if not (authenticated_user or cached_user):
            jwt_user = PlatformAuthentication().authenticate(request)
            if jwt_user is not None:
                # pylint: disable=protected-access
                request._cached_user = jwt_user[0]
                request.user = jwt_user[0]
        return get_response(request)

    return middleware
