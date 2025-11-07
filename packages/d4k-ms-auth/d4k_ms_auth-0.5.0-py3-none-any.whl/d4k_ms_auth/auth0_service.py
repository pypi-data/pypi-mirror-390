from fastapi import Request, HTTPException, status
from authlib.integrations.starlette_client import OAuth
from d4k_ms_auth.auth0_management import Auth0Management
from d4k_ms_base.service_environment import ServiceEnvironment
from d4k_ms_base.logger import application_logger
from urllib.parse import quote_plus, urlencode


class Auth0Service:
    def __init__(self) -> None:
        se = ServiceEnvironment()
        self.oauth = None
        self.audience = se.get("AUTH0_AUDIENCE")
        self.domain = se.get("AUTH0_DOMAIN")
        self.client_id = se.get("AUTH0_CLIENT_ID")
        self.client_secret = se.get("AUTH0_CLIENT_SECRET")
        url = se.get("ROOT_URL")
        self.base_url = url if url else None
        application_logger.info(f"Base URL: {self.base_url}")

    def register(self) -> None:
        """
        Since you have a WebApp you need OAuth client registration so you can perform
        authorization flows with the authorization server
        """
        self.oauth = OAuth()
        self.oauth.register(
            "auth0",
            client_id=self.client_id,
            client_secret=self.client_secret,
            client_kwargs={"scope": "openid profile email"},
            server_metadata_url=f"https://{self.domain}/.well-known/openid-configuration",
        )
        self.management = Auth0Management()

    def management_token(self):
        self.management.token()

    async def save_token(self, request: Request):
        token = await self.oauth.auth0.authorize_access_token(request)
        # Store `access_token`, `id_token`, and `userinfo` in session
        request.session["access_token"] = token["access_token"]
        request.session["id_token"] = token["id_token"]
        request.session["userinfo"] = token["userinfo"]
        request.session["userinfo"]["roles"] = self._get_roles(token["userinfo"])
        application_logger.info(f"User {request.session['userinfo']}")

    async def login(self, request: Request, route_method: str) -> None:
        self._update_url(request)
        url = self._get_abs_path(route_method)
        application_logger.info(f"Login attempt '{url}")
        return await self.oauth.auth0.authorize_redirect(
            request, redirect_uri=url, audience=self.audience
        )

    def logout(self, request: Request, route_method: str) -> str:
        self._update_url(request)
        request.session.clear()
        url = self._get_abs_path(route_method)
        application_logger.info(f"Logout attempt '{url}")
        data = {"returnTo": url, "client_id": self.client_id}
        url = f"https://{self.domain}/v2/logout?{urlencode(data, quote_via=quote_plus)}"
        application_logger.info(f"Logout URL '{url}'")
        return url

    def protect_route(self, request: Request, location: str = "/login") -> None:
        """
        This Dependency protects an endpoint and it can only be accessed if the user has an active session
        """
        self._update_url(request)
        if "id_token" not in request.session:
            # it could be userinfo instead of id_token
            # this will redirect people to the login after if they are not logged in
            raise HTTPException(
                status_code=status.HTTP_307_TEMPORARY_REDIRECT,
                detail="Not authorized",
                headers={"Location": location},
            )

    def _get_abs_path(self, route: str) -> str:
        if self.base_url:
            application_logger.debug(f"Using base URL '{self.base_url}'")
            app_domain = (
                self.base_url[:-1] if self.base_url.endswith("/") else self.base_url
            )
            route = route if route.startswith("/") else f"/{route}"
            application_logger.info(
                f"Forming absolute path using '{app_domain}' and '{route}'"
            )
            return f"{app_domain}{route}"
        else:
            application_logger.error("The base URL is not set")
            return ""

    def _update_url(self, request: Request):
        if not self.base_url:
            self.base_url = str(request.base_url)
            application_logger.info(f"Updated base URL '{self.base_url}'")

    def _get_roles(self, user_info):
        result = []
        try:
            user_id = user_info["sub"]
            if user_id:
                roles = self.management.user_roles(user_id)
                if roles:
                    result = roles["roles"]
        except Exception as e:
            application_logger.exception("Exception obtaining user role information", e)
        return result
