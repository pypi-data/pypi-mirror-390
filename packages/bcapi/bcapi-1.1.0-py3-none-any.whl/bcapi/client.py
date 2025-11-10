"""Client module for interacting with the Basecamp 3 API.

This module provides the core Client class for authenticating and making requests
to the Basecamp 3 API. It handles OAuth2 authentication flow, token management,
request caching, and pagination.

The Client class provides methods to:
- Handle initial OAuth2 authorization and token retrieval
- Refresh expired access tokens
- Make authenticated API requests with caching
- Handle paginated responses
"""

import requests
import os
from bcapi.cache import ResponseCache

class AuthorizationRequiredError(Exception):
    """Raised when Basecamp authorization is required and no refresh token exists."""


class BasecampAPIError(Exception):
    """Base exception for Basecamp API errors including failed requests."""


class Client:
    def __init__(self, verification_code=None):
        """
        Initialize a Basecamp API client with authentication.

        Loads configuration from environment variables and handles the OAuth2 
        authentication flow. If no refresh token exists, either uses the provided
        verification code to obtain one, or raises an error with authorization instructions.

        Parameters:
            verification_code (str, optional): The OAuth2 verification code obtained from 
                the Basecamp authorization process. Required for initial authorization.

        Raises:
            AuthorizationRequiredError: When no refresh token exists and no verification
                code is provided.
            BasecampAPIError: When API requests for tokens fail.
        """

        self.app_name = os.environ.get("BASECAMP_APP_NAME")
        self.account_id = os.environ.get("BASECAMP_ACCOUNT_ID")
        self.client_id = os.environ.get("BASECAMP_CLIENT_ID")
        self.client_secret = os.environ.get("BASECAMP_CLIENT_SECRET")
        self.redirect_uri = os.environ.get("BASECAMP_REDIRECT_URI")
        self.refresh_token = os.environ.get("BASECAMP_REFRESH_TOKEN")
        self.api_url = os.environ.get("BASECAMP_API_URL")
        self.auth_url = os.environ.get("BASECAMP_AUTH_URL")
        self.token_url = os.environ.get("BASECAMP_TOKEN_URL")
        self.user_agent = os.environ.get("BASECAMP_USER_AGENT")

        if not self.refresh_token:
            if not verification_code:
                self.verification_link = f"{self.auth_url}?type=web_server&client_id={self.client_id}&redirect_uri={self.redirect_uri}"
                raise AuthorizationRequiredError(
                    'Access denied. Use the following url to allow access and get the code from the redirect page\'s url parameter "code", then pass it as verification_code parameter of the Client object: '
                    + self.verification_link
                )
            else:
                self._get_refresh_token(verification_code)

        self._get_access_token()

        self.cache = ResponseCache()
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.access_token}",
            "User-Agent": self.user_agent
        })

    def _get_refresh_token(self, verification_code):
        """
        Exchange verification code for refresh token.

        Parameters:
            verification_code (str): The OAuth2 verification code

        Raises:
            BasecampAPIError: If token request fails
        """
        verification_url = f"{self.token_url}?type=web_server&client_id={self.client_id}&redirect_uri={self.redirect_uri}&client_secret={self.client_secret}&code={verification_code}"
        response = requests.post(verification_url, timeout=10)

        if not response.ok:
            raise BasecampAPIError(
                f"Status code: {response.status_code}. {response.reason}. Error text: {response.text}."
            )
        else:
            self.refresh_token = response.json()["refresh_token"]
            print("refresh_token added to credentials.")
            print(
                "Please save your refresh_token for future access: "
                + self.refresh_token
            )

    def _get_access_token(self):
        """
        Get new access token using refresh token.

        Raises:
            BasecampAPIError: If token refresh fails
        """
        access_url = f"{self.token_url}?type=refresh&refresh_token={self.refresh_token}&client_id={self.client_id}&redirect_uri={self.redirect_uri}&client_secret={self.client_secret}"
        response = requests.post(access_url, timeout=10)
        if not response.ok:
            raise BasecampAPIError(
                f"Status code: {response.status_code}. {response.reason}. Error text: {response.text}."
            )
        else:
            self.access_token = response.json()["access_token"]
            print("Authentication successful!")

    def request(self, method: str, url: str, **kwargs) -> dict:
        """
        Make a request to the Basecamp API with caching support.

        Handles GET request caching and pagination automatically. For paginated responses,
        combines all pages into a single result list. Non-GET requests bypass the cache.

        Parameters:
            method (str): HTTP method (GET, POST, etc)
            url (str): API endpoint URL
            **kwargs: Additional arguments to pass to requests

        Returns:
            dict: Response data for single resources
            list: Combined response data for paginated list endpoints

        Raises:
            BasecampAPIError: If the request fails
        """
        def get_next_page_url(headers):
            if 'Link' in headers:
                links = headers['Link'].split(',')
                for link in links:
                    if 'rel="next"' in link:
                        return link.split(';')[0].strip('<>')
            return None
    
        # Only cache GET requests
        if method.upper() == "GET":
            all_results = []
            current_url = url
            current_kwargs = kwargs.copy()

            while current_url:
                # Add caching headers to request
                headers = current_kwargs.get("headers", {})
                headers.update(self.cache.get_cached_headers(current_url))
                current_kwargs["headers"] = headers

                response = self.session.request(method, current_url, **current_kwargs)
                
                if response.status_code == 304:
                    return self.cache.get_cached_response(current_url)

                if response.ok:
                    self.cache.store(current_url, response)

                if not response.ok and response.status_code != 304:
                    raise BasecampAPIError(
                        f"Status code: {response.status_code}. {response.reason}. "
                        f"Error text: {response.text}."
                    )

                data = response.json() if response.content else None
                if isinstance(data, list):
                    all_results.extend(data)
                else:
                    return data

                current_url = get_next_page_url(response.headers)
                if current_url:
                    current_kwargs.pop('params', None)

            return all_results
            
        response = self.session.request(method, url, **kwargs)
        if not response.ok:
            raise BasecampAPIError(
                f"Status code: {response.status_code}. {response.reason}. "
                f"Error text: {response.text}."
            )
        return response.json() if response.content else None

    def refresh_access_token(self):
        """
        Refresh the access token when it expires.

        Updates the session headers with the new token.
        """
        self._get_access_token()
        self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})

    def close(self):
        """Close the session and free up system resources."""
        if hasattr(self, "session"):
            self.session.close()

    def __enter__(self):
        """Enable context manager support."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources when exiting context."""
        self.close()
