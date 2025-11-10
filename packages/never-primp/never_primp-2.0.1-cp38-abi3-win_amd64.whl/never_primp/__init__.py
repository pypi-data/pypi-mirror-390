from __future__ import annotations

import asyncio
import sys
from functools import partial
from typing import TYPE_CHECKING, TypedDict, Iterator
from collections.abc import MutableMapping

if sys.version_info <= (3, 11):
    from typing_extensions import Unpack
else:
    from typing import Unpack


from .never_primp import RClient

if TYPE_CHECKING:
    from .never_primp import IMPERSONATE, IMPERSONATE_OS, ClientRequestParams, HttpMethod, RequestParams, Response
else:

    class _Unpack:
        @staticmethod
        def __getitem__(*args, **kwargs):
            pass

    Unpack = _Unpack()
    RequestParams = ClientRequestParams = TypedDict


class HeadersJar(MutableMapping):
    """
    A dict-like container for managing HTTP headers, compatible with requests.Session.headers API.

    Examples:
        client = Client()

        # Set headers
        client.headers['User-Agent'] = 'CustomAgent/1.0'
        client.headers['Accept'] = 'application/json'

        # Get headers
        value = client.headers['User-Agent']
        value = client.headers.get('Accept', 'default')

        # Update multiple headers
        client.headers.update({'X-Custom': 'value1', 'X-Another': 'value2'})

        # Delete headers
        del client.headers['User-Agent']

        # Clear all headers
        client.headers.clear()

        # Check existence
        if 'User-Agent' in client.headers:
            print("User-Agent exists")

        # Convert to dict
        all_headers = dict(client.headers)
    """

    def __init__(self, client: RClient):
        """Initialize HeadersJar with a reference to the client."""
        self._client = client

    def __getitem__(self, name: str) -> str:
        """Get a header value by name."""
        value = self._client.get_header(name)
        if value is None:
            raise KeyError(name)
        return value

    def __setitem__(self, name: str, value: str) -> None:
        """Set a header by name."""
        self._client.set_header(name, value)

    def __delitem__(self, name: str) -> None:
        """Delete a header by name."""
        # Check if header exists first
        if self._client.get_header(name) is None:
            raise KeyError(name)
        self._client.delete_header(name)

    def __iter__(self) -> Iterator[str]:
        """Iterate over header names."""
        return iter(self._client.get_headers().keys())

    def __len__(self) -> int:
        """Return the number of headers."""
        return len(self._client.get_headers())

    def __contains__(self, name: object) -> bool:
        """Check if a header exists."""
        if not isinstance(name, str):
            return False
        return self._client.get_header(name) is not None

    def __repr__(self) -> str:
        """Return string representation of headers."""
        headers = self._client.get_headers()
        return f"HeadersJar({headers})"

    def get(self, name: str, default: str | None = None) -> str | None:
        """Get a header value with a default fallback."""
        value = self._client.get_header(name)
        return value if value is not None else default

    def update(self, headers: dict[str, str]) -> None:
        """
        Update multiple headers at once.

        Args:
            headers: Dictionary of header names to values
        """
        self._client.headers_update(headers)

    def clear(self) -> None:
        """Remove all headers."""
        self._client.clear_headers()

    def set(self, name: str, value: str) -> None:
        """
        Set a single header.

        Args:
            name: Header name
            value: Header value
        """
        self._client.set_header(name, value)


class CookieJar(MutableMapping):
    """
    A dict-like container for managing HTTP cookies, compatible with requests.Session.cookies API.

    Examples:
        client = Client()

        # Set cookies
        client.cookies['session_id'] = 'abc123'
        client.cookies['user_token'] = 'xyz789'

        # Get cookies
        value = client.cookies['session_id']
        value = client.cookies.get('user_token', 'default')

        # Update multiple cookies
        client.cookies.update({'key1': 'value1', 'key2': 'value2'})

        # Delete cookies
        del client.cookies['session_id']

        # Clear all cookies
        client.cookies.clear()

        # Check existence
        if 'session_id' in client.cookies:
            print("Session exists")

        # Convert to dict
        all_cookies = dict(client.cookies)
    """

    def __init__(self, client: RClient):
        """Initialize CookieJar with a reference to the client."""
        self._client = client

    def __getitem__(self, name: str) -> str:
        """Get a cookie value by name."""
        value = self._client.get_cookie(name)
        if value is None:
            raise KeyError(name)
        return value

    def __setitem__(self, name: str, value: str) -> None:
        """Set a cookie by name."""
        self._client.set_cookie(name, value)

    def __delitem__(self, name: str) -> None:
        """Delete a cookie by name."""
        # Check if cookie exists first
        if self._client.get_cookie(name) is None:
            raise KeyError(name)
        self._client.delete_cookie(name)

    def __iter__(self) -> Iterator[str]:
        """Iterate over cookie names."""
        return iter(self._client.get_all_cookies().keys())

    def __len__(self) -> int:
        """Return the number of cookies."""
        return len(self._client.get_all_cookies())

    def __contains__(self, name: object) -> bool:
        """Check if a cookie exists."""
        if not isinstance(name, str):
            return False
        return self._client.get_cookie(name) is not None

    def __repr__(self) -> str:
        """Return string representation of cookies."""
        cookies = self._client.get_all_cookies()
        return f"CookieJar({cookies})"

    def get(self, name: str, default: str | None = None) -> str | None:
        """Get a cookie value with a default fallback."""
        value = self._client.get_cookie(name)
        return value if value is not None else default

    def update(self, cookies: dict[str, str], domain: str | None = None, path: str | None = None) -> None:
        """
        Update multiple cookies at once.

        Args:
            cookies: Dictionary of cookie names to values
            domain: Optional domain for the cookies (e.g., ".example.com")
            path: Optional path for the cookies (e.g., "/")
        """
        self._client.update_cookies(cookies, domain=domain, path=path)

    def clear(self) -> None:
        """Remove all cookies."""
        self._client.clear_cookies()

    def set(self, name: str, value: str, domain: str | None = None, path: str | None = None) -> None:
        """
        Set a single cookie with optional domain and path.

        Args:
            name: Cookie name
            value: Cookie value
            domain: Optional domain (e.g., ".example.com")
            path: Optional path (e.g., "/")
        """
        self._client.set_cookie(name, value, domain=domain, path=path)


class Client(RClient):
    """Initializes an HTTP client that can impersonate web browsers with Architecture v2.0 features."""

    def __init__(
            self,
            # Auth
            auth: tuple[str, str | None] | None = None,
            auth_bearer: str | None = None,
            # Request config
            params: dict[str, str] | None = None,
            headers: dict[str, str] | None = None,
            cookies: dict[str, str] | None = None,
            # Cookie management
            cookie_store: bool | None = True,
            split_cookies: bool | None = False,
            # HTTP options
            referer: bool | None = True,
            follow_redirects: bool | None = True,
            max_redirects: int | None = 20,
            redirect_history: bool | None = False,  # NEW in v2.0
            https_only: bool | None = False,
            http1_only: bool | None = False,
            http2_only: bool | None = False,
            # Proxy
            proxy: str | None = None,
            # Timeout (NEW fine-grained control in v2.0)
            timeout: float | None = 30,
            connect_timeout: float | None = None,  # NEW in v2.0
            read_timeout: float | None = None,      # NEW in v2.0
            # Impersonate
            impersonate: IMPERSONATE | None = None,
            impersonate_os: IMPERSONATE_OS | None = None,
            # TLS
            verify: bool | None = True,
            verify_hostname: bool | None = None,    # NEW in v2.0
            ca_cert_file: str | None = None,
            min_tls_version: str | None = None,     # NEW in v2.0
            max_tls_version: str | None = None,     # NEW in v2.0
            # TCP basic
            tcp_nodelay: bool | None = None,
            tcp_keepalive: float | None = None,
            tcp_keepalive_interval: float | None = None,     # NEW in v2.0
            tcp_keepalive_retries: int | None = None,        # NEW in v2.0
            tcp_reuse_address: bool | None = None,           # NEW in v2.0
            # TCP buffer (NEW in v2.0)
            tcp_send_buffer_size: int | None = None,
            tcp_recv_buffer_size: int | None = None,
            # TCP binding (NEW in v2.0)
            local_ipv4: str | None = None,
            local_ipv6: str | None = None,
            interface: str | None = None,
            # Connection pool
            pool_idle_timeout: float | None = None,
            pool_max_idle_per_host: int | None = None,
            pool_max_size: int | None = None,                # NEW in v2.0
            # DNS (NEW in v2.0)
            dns_overrides: dict[str, list[str]] | None = None,
    ):
        """
        Args:
            auth: a tuple containing the username and an optional password for basic authentication. Default is None.
            auth_bearer: a string representing the bearer token for bearer token authentication. Default is None.
            params: a map of query parameters to append to the URL. Default is None.
            headers: an optional ordered map of HTTP headers with strict order preservation.
                Headers will be sent in the exact order specified, with automatic positioning of:
                - Host (first position)
                - Content-Length (second position for POST/PUT/PATCH)
                - Content-Type (third position if auto-calculated)
                - cookie (second-to-last position)
                - priority (last position)
                Example: {"User-Agent": "...", "Accept": "...", "Accept-Language": "..."}
                Note: Python 3.7+ dict maintains insertion order by default.
            cookies: initial cookies to set for the client. These cookies will be included in all requests.
                Can be updated later using client.cookies.update(). Default is None.
            cookie_store: enable a persistent cookie store. Received cookies will be preserved and included
                 in additional requests. Default is True.
            split_cookies: split cookies into multiple `cookie` headers (HTTP/2 style) instead of a single
                `Cookie` header. Useful for mimicking browser behavior in HTTP/2. Default is False.
                When True: cookie: a=1 \n cookie: b=2 \n cookie: c=3
                When False: Cookie: a=1; b=2; c=3
            referer: automatic setting of the `Referer` header. Default is True.
            proxy: proxy URL for HTTP requests, example: "socks5://127.0.0.1:9150". Default is None.
            timeout: timeout for HTTP requests in seconds. Default is 30.
            impersonate: impersonate browser. Supported browsers:
                "chrome_100", "chrome_101", "chrome_104", "chrome_105", "chrome_106",
                "chrome_107", "chrome_108", "chrome_109", "chrome_114", "chrome_116",
                "chrome_117", "chrome_118", "chrome_119", "chrome_120", "chrome_123",
                "chrome_124", "chrome_126", "chrome_127", "chrome_128", "chrome_129",
                "chrome_130", "chrome_131", "chrome_133"
                "safari_15.3", "safari_15.5", "safari_15.6.1", "safari_16",
                "safari_16.5", "safari_17.0", "safari_17.2.1", "safari_17.4.1",
                "safari_17.5", "safari_18",  "safari_18.2",
                "safari_ios_16.5", "safari_ios_17.2", "safari_ios_17.4.1", "safari_ios_18.1.1",
                "safari_ipad_18",
                "okhttp_3.9", "okhttp_3.11", "okhttp_3.13", "okhttp_3.14", "okhttp_4.9",
                "okhttp_4.10", "okhttp_5",
                "edge_101", "edge_122", "edge_127", "edge_131",
                "firefox_109", "firefox_117", "firefox_128", "firefox_133", "firefox_135".
                Default is None.
            impersonate_os: impersonate OS. Supported OS:
                "android", "ios", "linux", "macos", "windows". Default is None.
            follow_redirects: a boolean to enable or disable following redirects. Default is True.
            max_redirects: the maximum number of redirects if `follow_redirects` is True. Default is 20.
            verify: an optional boolean indicating whether to verify SSL certificates. Default is True.
            ca_cert_file: path to CA certificate store. Default is None.
            https_only: restrict the Client to be used with HTTPS only requests. Default is False.
            http1_only: if true - use only HTTP/1.1. Default is False.
            http2_only: if true - use only HTTP/2. Default is False.
                Note: http1_only and http2_only are mutually exclusive. If both are true, http1_only takes precedence.
        """
        super().__init__()
        self._cookies_jar: CookieJar | None = None
        self._headers_jar: HeadersJar | None = None

        # Set initial cookies if provided
        if cookies:
            self.update_cookies(cookies)

    @property
    def headers(self) -> HeadersJar:
        """
        Access the headers for dict-like header management.

        Returns:
            HeadersJar: A dict-like container for managing headers.

        Examples:
            # Set headers
            client.headers['User-Agent'] = 'CustomAgent/1.0'

            # Get headers
            value = client.headers['User-Agent']

            # Update headers
            client.headers.update({'Accept': 'application/json'})

            # Delete headers
            del client.headers['User-Agent']

            # Clear all
            client.headers.clear()
        """
        if self._headers_jar is None:
            self._headers_jar = HeadersJar(self)
        return self._headers_jar

    @headers.setter
    def headers(self, value: dict[str, str] | None) -> None:
        """Set headers by replacing all existing headers."""
        self.set_headers(value)
        # Reset the jar so it picks up new headers
        self._headers_jar = None

    @property
    def cookies(self) -> CookieJar:
        """
        Access the cookie jar for dict-like cookie management.

        Returns:
            CookieJar: A dict-like container for managing cookies.

        Examples:
            # Set cookies
            client.cookies['session_id'] = 'abc123'

            # Get cookies
            value = client.cookies['session_id']

            # Update cookies
            client.cookies.update({'key': 'value'})

            # Delete cookies
            del client.cookies['session_id']

            # Clear all
            client.cookies.clear()
        """
        if self._cookies_jar is None:
            self._cookies_jar = CookieJar(self)
        return self._cookies_jar

    def __enter__(self) -> Client:
        return self

    def __exit__(self, *args):
        del self

    def request(self, method: HttpMethod, url: str, **kwargs: Unpack[RequestParams]) -> Response:
        """
        Send an HTTP request with support for requests-toolbelt MultipartEncoder.

        Supports both native primp format and requests-toolbelt MultipartEncoder:
        - Native: request(url, data={...}, files={...})
        - Toolbelt: request(url, data=MultipartEncoder(...))
        """
        # Check if data is a MultipartEncoder from requests-toolbelt
        data = kwargs.get('data')
        if data is not None and hasattr(data, 'fields') and hasattr(data, 'content_type'):
            # This looks like a MultipartEncoder
            # Extract fields and convert to primp format
            converted_data = {}
            converted_files = {}

            try:
                # MultipartEncoder.fields is a dict-like object
                for field_name, field_value in data.fields.items():
                    if isinstance(field_value, tuple):
                        # File field: (filename, file_obj, content_type)
                        if len(field_value) >= 2:
                            filename = field_value[0]
                            file_obj = field_value[1]

                            # Read the file content
                            if hasattr(file_obj, 'read'):
                                file_content = file_obj.read()
                                # Reset file pointer if possible
                                if hasattr(file_obj, 'seek'):
                                    try:
                                        file_obj.seek(0)
                                    except:
                                        pass
                            else:
                                file_content = file_obj

                            # Add mime type if provided
                            if len(field_value) >= 3:
                                mime_type = field_value[2]
                                converted_files[field_name] = (filename, file_content, mime_type)
                            else:
                                converted_files[field_name] = (filename, file_content)
                    else:
                        # Regular field
                        if isinstance(field_value, bytes):
                            converted_data[field_name] = field_value.decode('utf-8')
                        else:
                            converted_data[field_name] = str(field_value)

                # Replace data and files in kwargs
                if converted_data:
                    kwargs['data'] = converted_data
                else:
                    kwargs.pop('data', None)

                if converted_files:
                    kwargs['files'] = converted_files

            except Exception as e:
                # If conversion fails, fall back to treating it as raw content
                # Read the encoder as bytes and send as content
                if hasattr(data, 'read'):
                    kwargs['content'] = data.read()
                    kwargs.pop('data', None)

                    # Get content type from encoder
                    if hasattr(data, 'content_type'):
                        headers = kwargs.get('headers', {})
                        if not isinstance(headers, dict):
                            headers = dict(headers)
                        headers['Content-Type'] = data.content_type
                        kwargs['headers'] = headers

        return super().request(method=method, url=url, **kwargs)

    def get(self, url: str, **kwargs: Unpack[RequestParams]) -> Response:
        return self.request(method="GET", url=url, **kwargs)

    def head(self, url: str, **kwargs: Unpack[RequestParams]) -> Response:
        return self.request(method="HEAD", url=url, **kwargs)

    def options(self, url: str, **kwargs: Unpack[RequestParams]) -> Response:
        return self.request(method="OPTIONS", url=url, **kwargs)

    def delete(self, url: str, **kwargs: Unpack[RequestParams]) -> Response:
        return self.request(method="DELETE", url=url, **kwargs)

    def post(self, url: str, **kwargs: Unpack[RequestParams]) -> Response:
        return self.request(method="POST", url=url, **kwargs)

    def put(self, url: str, **kwargs: Unpack[RequestParams]) -> Response:
        return self.request(method="PUT", url=url, **kwargs)

    def patch(self, url: str, **kwargs: Unpack[RequestParams]) -> Response:
        return self.request(method="PATCH", url=url, **kwargs)


class AsyncClient(Client):
    """Asynchronous version of Client, providing the same interface and parameters."""

    def __init__(
            self,
            # Auth
            auth: tuple[str, str | None] | None = None,
            auth_bearer: str | None = None,
            # Request config
            params: dict[str, str] | None = None,
            headers: dict[str, str] | None = None,
            cookies: dict[str, str] | None = None,
            # Cookie management
            cookie_store: bool | None = True,
            split_cookies: bool | None = False,
            # HTTP options
            referer: bool | None = True,
            follow_redirects: bool | None = True,
            max_redirects: int | None = 20,
            redirect_history: bool | None = False,
            https_only: bool | None = False,
            http1_only: bool | None = False,
            http2_only: bool | None = False,
            # Proxy
            proxy: str | None = None,
            # Timeout
            timeout: float | None = 30,
            connect_timeout: float | None = None,
            read_timeout: float | None = None,
            # Impersonate
            impersonate: IMPERSONATE | None = None,
            impersonate_os: IMPERSONATE_OS | None = None,
            # TLS
            verify: bool | None = True,
            verify_hostname: bool | None = None,
            ca_cert_file: str | None = None,
            min_tls_version: str | None = None,
            max_tls_version: str | None = None,
            # TCP basic
            tcp_nodelay: bool | None = None,
            tcp_keepalive: float | None = None,
            tcp_keepalive_interval: float | None = None,
            tcp_keepalive_retries: int | None = None,
            tcp_reuse_address: bool | None = None,
            # TCP buffer
            tcp_send_buffer_size: int | None = None,
            tcp_recv_buffer_size: int | None = None,
            # TCP binding
            local_ipv4: str | None = None,
            local_ipv6: str | None = None,
            interface: str | None = None,
            # Connection pool
            pool_idle_timeout: float | None = None,
            pool_max_idle_per_host: int | None = None,
            pool_max_size: int | None = None,
            # DNS
            dns_overrides: dict[str, list[str]] | None = None,
    ):
        super().__init__(
            # Auth
            auth=auth,
            auth_bearer=auth_bearer,
            # Request config
            params=params,
            headers=headers,
            cookies=cookies,
            # Cookie management
            cookie_store=cookie_store,
            split_cookies=split_cookies,
            # HTTP options
            referer=referer,
            follow_redirects=follow_redirects,
            max_redirects=max_redirects,
            redirect_history=redirect_history,
            https_only=https_only,
            http1_only=http1_only,
            http2_only=http2_only,
            # Proxy
            proxy=proxy,
            # Timeout
            timeout=timeout,
            connect_timeout=connect_timeout,
            read_timeout=read_timeout,
            # Impersonate
            impersonate=impersonate,
            impersonate_os=impersonate_os,
            # TLS
            verify=verify,
            verify_hostname=verify_hostname,
            ca_cert_file=ca_cert_file,
            min_tls_version=min_tls_version,
            max_tls_version=max_tls_version,
            # TCP basic
            tcp_nodelay=tcp_nodelay,
            tcp_keepalive=tcp_keepalive,
            tcp_keepalive_interval=tcp_keepalive_interval,
            tcp_keepalive_retries=tcp_keepalive_retries,
            tcp_reuse_address=tcp_reuse_address,
            # TCP buffer
            tcp_send_buffer_size=tcp_send_buffer_size,
            tcp_recv_buffer_size=tcp_recv_buffer_size,
            # TCP binding
            local_ipv4=local_ipv4,
            local_ipv6=local_ipv6,
            interface=interface,
            # Connection pool
            pool_idle_timeout=pool_idle_timeout,
            pool_max_idle_per_host=pool_max_idle_per_host,
            pool_max_size=pool_max_size,
            # DNS
            dns_overrides=dns_overrides,
        )

    async def __aenter__(self) -> "AsyncClient":
        return self

    async def __aexit__(self, *args):
        del self

    async def _run_sync_asyncio(self, fn, *args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, partial(fn, *args, **kwargs))

    async def request(self, method: HttpMethod, url: str, **kwargs: Unpack[RequestParams]):
        """Asynchronous version of Client.request"""
        return await self._run_sync_asyncio(super().request, method=method, url=url, **kwargs)

    async def get(self, url: str, **kwargs: Unpack[RequestParams]):
        return await self.request(method="GET", url=url, **kwargs)

    async def head(self, url: str, **kwargs: Unpack[RequestParams]):
        return await self.request(method="HEAD", url=url, **kwargs)

    async def options(self, url: str, **kwargs: Unpack[RequestParams]):
        return await self.request(method="OPTIONS", url=url, **kwargs)

    async def delete(self, url: str, **kwargs: Unpack[RequestParams]):
        return await self.request(method="DELETE", url=url, **kwargs)

    async def post(self, url: str, **kwargs: Unpack[RequestParams]):
        return await self.request(method="POST", url=url, **kwargs)

    async def put(self, url: str, **kwargs: Unpack[RequestParams]):
        return await self.request(method="PUT", url=url, **kwargs)

    async def patch(self, url: str, **kwargs: Unpack[RequestParams]):
        return await self.request(method="PATCH", url=url, **kwargs)
def request(
        method: HttpMethod,
        url: str,
        impersonate: IMPERSONATE | None = None,
        impersonate_os: IMPERSONATE_OS | None = None,
        verify: bool | None = True,
        ca_cert_file: str | None = None,
        **kwargs: Unpack[RequestParams],
):
    """
    Args:
        method: the HTTP method to use (e.g., "GET", "POST").
        url: the URL to which the request will be made.
        impersonate: impersonate browser. Supported browsers:
            "chrome_100", "chrome_101", "chrome_104", "chrome_105", "chrome_106",
            "chrome_107", "chrome_108", "chrome_109", "chrome_114", "chrome_116",
            "chrome_117", "chrome_118", "chrome_119", "chrome_120", "chrome_123",
            "chrome_124", "chrome_126", "chrome_127", "chrome_128", "chrome_129",
            "chrome_130", "chrome_131", "chrome_133",
            "safari_15.3", "safari_15.5", "safari_15.6.1", "safari_16",
            "safari_16.5", "safari_17.0", "safari_17.2.1", "safari_17.4.1",
            "safari_17.5", "safari_18",  "safari_18.2",
            "safari_ios_16.5", "safari_ios_17.2", "safari_ios_17.4.1", "safari_ios_18.1.1",
            "safari_ipad_18",
            "okhttp_3.9", "okhttp_3.11", "okhttp_3.13", "okhttp_3.14", "okhttp_4.9",
            "okhttp_4.10", "okhttp_5",
            "edge_101", "edge_122", "edge_127", "edge_131",
            "firefox_109", "firefox_117", "firefox_128", "firefox_133", "firefox_135".
            Default is None.
        impersonate_os: impersonate OS. Supported OS:
            "android", "ios", "linux", "macos", "windows". Default is None.
        verify: an optional boolean indicating whether to verify SSL certificates. Default is True.
        ca_cert_file: path to CA certificate store. Default is None.
        auth: a tuple containing the username and an optional password for basic authentication. Default is None.
        auth_bearer: a string representing the bearer token for bearer token authentication. Default is None.
        params: a map of query parameters to append to the URL. Default is None.
        headers: an optional map of HTTP headers to send with requests. If `impersonate` is set, this will be ignored.
        cookies: an optional map of cookies to send with requests as the `Cookie` header.
        timeout: the timeout for the request in seconds. Default is 30.
        content: the content to send in the request body as bytes. Default is None.
        data: the form data to send in the request body. Default is None.
        json: a JSON serializable object to send in the request body. Default is None.
        files: a map of file fields to file paths to be sent as multipart/form-data. Default is None.
    """
    with Client(
            impersonate=impersonate,
            impersonate_os=impersonate_os,
            verify=verify,
            ca_cert_file=ca_cert_file,
    ) as client:
        return client.request(method, url, **kwargs)


def get(url: str, **kwargs: Unpack[ClientRequestParams]):
    return request(method="GET", url=url, **kwargs)


def head(url: str, **kwargs: Unpack[ClientRequestParams]):
    return request(method="HEAD", url=url, **kwargs)


def options(url: str, **kwargs: Unpack[ClientRequestParams]):
    return request(method="OPTIONS", url=url, **kwargs)


def delete(url: str, **kwargs: Unpack[ClientRequestParams]):
    return request(method="DELETE", url=url, **kwargs)


def post(url: str, **kwargs: Unpack[ClientRequestParams]):
    return request(method="POST", url=url, **kwargs)


def put(url: str, **kwargs: Unpack[ClientRequestParams]):
    return request(method="PUT", url=url, **kwargs)


def patch(url: str, **kwargs: Unpack[ClientRequestParams]):
    return request(method="PATCH", url=url, **kwargs)
