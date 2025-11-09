import uuid
from contextlib import suppress

from fastapi import FastAPI, Request
from fastapi_another_jwt_auth import AuthJWT as JWT
from pydantic import Field
from starlette.middleware.sessions import SessionMiddleware as StarletteSessionMiddleware
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from apppy.auth.errors.service import (
    ServiceKeyAlgorithmMissingError,
)
from apppy.auth.jwks import JwkInfo, JwkPemFile, JwksAuthStorage
from apppy.auth.jwt import JwtAuthContext, JwtAuthSettings
from apppy.env import Env, EnvSettings
from apppy.fastql.errors import GraphQLError
from apppy.logger import WithLogger
from apppy.logger.storage import LoggingStorage


class JwtAuthMiddleware(WithLogger):
    """
    A middleware instance which analyzes the request headers,
    creates a JwtAuthContext, and set it in thread local storage
    """

    def __init__(
        self,
        app: ASGIApp,
        jwt_auth_settings: JwtAuthSettings,
        jwks_auth_storage: JwksAuthStorage,
        exclude_paths: list[str] | None = None,
    ):
        self._app = app
        self._jwks_auth_storage = jwks_auth_storage
        self._exclude_paths = exclude_paths or ["/health", "/version"]

        # Load the global JWT configuration JWT.
        # This is used for processing user requests below.
        @JWT.load_config
        def load_config_jwtauth_global():
            return jwt_auth_settings

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        request_path = scope.get("path") or scope.get("raw_path", b"").decode("latin1")
        if any(request_path.startswith(p) for p in self._exclude_paths):
            await self._app(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        jwt_headers: dict | None = JwtAuthContext.peek(request)

        try:
            service_name: str | None = None
            if jwt_headers is not None:
                self._logger.debug("JWT headers", extra=jwt_headers)
                service_name, _ = JwkPemFile.parse_kid(jwt_headers.get("kid"))

            if jwt_headers is not None and service_name is not None:
                # CASE: A Service is making the request
                jwk_info: JwkInfo = self._jwks_auth_storage.get_jwk(jwt_headers["kid"])

                if "alg" not in jwt_headers:
                    raise ServiceKeyAlgorithmMissingError()

                public_key = jwk_info.jwk.get_op_key("verify")
                auth_ctx = JwtAuthContext.from_service_request(
                    request, jwt_headers["alg"], public_key
                )
            else:
                # CASE: A User is making the request
                # Instead of using the JWKS storage, we'll
                # use the global configuration loaded in __init__
                auth_ctx = JwtAuthContext.from_user_request(request)
        except GraphQLError as e:
            # If we encounter an error while preprocessing the
            # auth context, we'll capture the error and keep going. The
            # authentication and authorization permission are designed
            # to handle this and raise the appropriate error.
            auth_ctx = JwtAuthContext(preprocessing_error=e)

        JwtAuthContext.set_current_auth_context(auth_ctx)
        await self._app(scope, receive, send)


class RequestIdMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        header_name: str = "X-Request-ID",
    ):
        self._app = app
        self.header_name = header_name

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        request_id = str(uuid.uuid4())

        # Store in LoggingStorage (thread-local)
        with suppress(RuntimeError):
            LoggingStorage.get_global().add_request_id(request_id)

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((self.header_name.encode("latin-1"), request_id.encode("latin-1")))
                message = {**message, "headers": headers}
            elif message["type"] == "http.response.body" and message.get("more_body") is False:
                # Cleanup after final chunk
                with suppress(RuntimeError):
                    LoggingStorage.get_global().reset()

            await send(message)

        try:
            await self._app(scope, receive, send_wrapper)
        finally:
            # If an exception short-circuited before body end, still cleanup
            with suppress(RuntimeError):
                LoggingStorage.get_global().reset()


class SessionMiddlewareSettings(EnvSettings):
    # SESSION_MIDDLEWARE_SECRET_KEY
    secret_key: str = Field(exclude=True)

    def __init__(self, env: Env) -> None:
        super().__init__(env=env, domain_prefix="SESSION_MIDDLEWARE")


class SessionMiddleware(StarletteSessionMiddleware):
    """
    Simple wrapper around Starlette's SessionMiddleware to allow for
    injected settings via EnvSettings
    """

    def __init__(self, fastapi: FastAPI, settings: SessionMiddlewareSettings):
        super().__init__(app=fastapi, secret_key=settings.secret_key)
