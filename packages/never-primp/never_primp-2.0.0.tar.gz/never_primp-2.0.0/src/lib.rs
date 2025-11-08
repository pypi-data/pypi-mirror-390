#![allow(clippy::too_many_arguments)]
use std::sync::{Arc, LazyLock, Mutex, RwLock};
use std::sync::atomic::{AtomicBool, Ordering};
use std::collections::HashSet;
use std::time::Duration;

use anyhow::Result;
use foldhash::fast::RandomState;
use indexmap::IndexMap;
use pyo3::prelude::*;
use pythonize::depythonize;
use wreq::{
    header::OrigHeaderMap,
    multipart,
    redirect::Policy,
    Body, Method,
};
use wreq_util::{Emulation, EmulationOS, EmulationOption};
use serde_json::Value;
use serde_urlencoded;
use tokio::{
    fs::File,
    runtime::{self, Runtime},
};
use tokio_util::codec::{BytesCodec, FramedRead};
use tracing;

mod config;
use config::{ClientConfig, HttpVersion};

mod impersonate;
use impersonate::{ImpersonateFromStr, ImpersonateOSFromStr};
mod response;
use response::Response;

mod traits;
use traits::HeadersTraits;

mod utils;
use utils::load_ca_certs;

type IndexMapSSR = IndexMap<String, String, RandomState>;

// Tokio global one-thread runtime
static RUNTIME: LazyLock<Runtime> = LazyLock::new(|| {
    runtime::Builder::new_current_thread()
        .enable_all()
        .build()
        .unwrap()
});

#[pyclass(subclass)]
/// HTTP client that can impersonate web browsers.
///
/// Architecture v2.0: Uses modular configuration (config::ClientConfig) to manage all settings.
/// This eliminates code duplication and improves maintainability.
pub struct RClient {
    // Core components
    client: Arc<Mutex<wreq::Client>>,
    client_dirty: Arc<AtomicBool>,  // Flag to mark client needs rebuild (lazy rebuild optimization)
    cookie_jar: Arc<wreq::cookie::Jar>,
    deleted_cookies: Arc<RwLock<HashSet<String>>>,  // Track deleted cookies

    // Unified configuration object (all settings centrally managed)
    config: Arc<RwLock<ClientConfig>>,

    // Runtime state (frequently changing)
    headers: Arc<RwLock<Option<IndexMapSSR>>>,
    #[pyo3(get, set)]
    params: Option<IndexMapSSR>,
    #[pyo3(get, set)]
    split_cookies: Option<bool>,

    // Note: timeout, proxy, impersonate, auth, etc. are now stored in config
    // and accessed via getters/setters (see get_timeout(), set_timeout(), etc.)
}

#[pymethods]
impl RClient {
    /// Initializes an HTTP client that can impersonate web browsers.
    ///
    /// This function creates a new HTTP client instance that can impersonate various web browsers.
    /// It allows for customization of headers, proxy settings, timeout, impersonation type, SSL certificate verification,
    /// and HTTP version preferences.
    ///
    /// # Arguments
    ///
    /// * `auth` - A tuple containing the username and an optional password for basic authentication. Default is None.
    /// * `auth_bearer` - A string representing the bearer token for bearer token authentication. Default is None.
    /// * `params` - A map of query parameters to append to the URL. Default is None.
    /// * `headers` - An optional ordered map of HTTP headers with strict order preservation.
    ///   Headers will be sent in the exact order specified, with automatic positioning of:
    ///   - Host (first position)
    ///   - Content-Length (second position for POST/PUT/PATCH)
    ///   - Content-Type (third position if auto-calculated)
    ///   - cookie (second-to-last position)
    ///   - priority (last position)
    /// * `cookie_store` - Enable a persistent cookie store. Received cookies will be preserved and included
    ///         in additional requests. Default is `true`.
    /// * `split_cookies` - Split cookies into multiple `cookie` headers (HTTP/2 style) instead of a single `Cookie` header.
    ///         Useful for mimicking browser behavior in HTTP/2. Default is `false`.
    /// * `referer` - Enable or disable automatic setting of the `Referer` header. Default is `true`.
    /// * `proxy` - An optional proxy URL for HTTP requests.
    /// * `timeout` - An optional timeout for HTTP requests in seconds.
    /// * `impersonate` - An optional entity to impersonate. Supported browsers and versions include Chrome, Safari, OkHttp, and Edge.
    /// * `impersonate_os` - An optional entity to impersonate OS. Supported OS: android, ios, linux, macos, windows.
    /// * `follow_redirects` - A boolean to enable or disable following redirects. Default is `true`.
    /// * `max_redirects` - The maximum number of redirects to follow. Default is 20. Applies if `follow_redirects` is `true`.
    /// * `verify` - An optional boolean indicating whether to verify SSL certificates. Default is `true`.
    /// * `ca_cert_file` - Path to CA certificate store. Default is None.
    /// * `https_only` - Restrict the Client to be used with HTTPS only requests. Default is `false`.
    /// * `http1_only` - If true - use only HTTP/1.1. Default is `false`.
    /// * `http2_only` - If true - use only HTTP/2. Default is `false`.
    ///   Note: `http1_only` and `http2_only` are mutually exclusive. If both are true, `http1_only` takes precedence.
    ///
    /// # Example
    ///
    /// ```
    /// from primp import Client
    ///
    /// client = Client(
    ///     auth=("name", "password"),
    ///     params={"p1k": "p1v", "p2k": "p2v"},
    ///     headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"},
    ///     cookie_store=False,
    ///     referer=False,
    ///     proxy="http://127.0.0.1:8080",
    ///     timeout=10,
    ///     impersonate="chrome_123",
    ///     impersonate_os="windows",
    ///     follow_redirects=True,
    ///     max_redirects=1,
    ///     verify=True,
    ///     ca_cert_file="/cert/cacert.pem",
    ///     https_only=True,
    ///     http2_only=True,
    /// )
    /// ```
    #[new]
    #[pyo3(signature = (
        // Auth
        auth=None, auth_bearer=None,
        // Request config
        params=None, headers=None, cookies=None,
        // Cookie management
        cookie_store=true, split_cookies=false,
        // HTTP options
        referer=true, follow_redirects=true, max_redirects=20, redirect_history=false,
        https_only=false, http1_only=false, http2_only=false,
        // Proxy
        proxy=None,
        // Timeout (总超时 + 细分超时) NEW!
        timeout=30.0, connect_timeout=None, read_timeout=None,
        // Impersonate
        impersonate=None, impersonate_os=None,
        // TLS
        verify=true, verify_hostname=None, ca_cert_file=None,
        min_tls_version=None, max_tls_version=None,
        // TCP basic
        tcp_nodelay=None, tcp_keepalive=None,
        tcp_keepalive_interval=None, tcp_keepalive_retries=None,
        tcp_reuse_address=None,
        // TCP buffer NEW!
        tcp_send_buffer_size=None, tcp_recv_buffer_size=None,
        // TCP binding NEW!
        local_ipv4=None, local_ipv6=None, interface=None,
        // Connection pool
        pool_idle_timeout=None, pool_max_idle_per_host=None, pool_max_size=None,
        // DNS NEW!
        dns_overrides=None
    ))]
    #[allow(clippy::too_many_arguments)]
    fn new(
        // Auth
        auth: Option<(String, Option<String>)>,
        auth_bearer: Option<String>,
        // Request config
        params: Option<IndexMapSSR>,
        headers: Option<IndexMapSSR>,
        cookies: Option<IndexMapSSR>,
        // Cookie management
        cookie_store: Option<bool>,
        split_cookies: Option<bool>,
        // HTTP options
        referer: Option<bool>,
        follow_redirects: Option<bool>,
        max_redirects: Option<usize>,
        redirect_history: Option<bool>,
        https_only: Option<bool>,
        http1_only: Option<bool>,
        http2_only: Option<bool>,
        // Proxy
        proxy: Option<String>,
        // Timeout
        timeout: Option<f64>,
        connect_timeout: Option<f64>,
        read_timeout: Option<f64>,
        // Impersonate
        impersonate: Option<String>,
        impersonate_os: Option<String>,
        // TLS
        verify: Option<bool>,
        verify_hostname: Option<bool>,
        ca_cert_file: Option<String>,
        min_tls_version: Option<String>,
        max_tls_version: Option<String>,
        // TCP basic
        tcp_nodelay: Option<bool>,
        tcp_keepalive: Option<f64>,
        tcp_keepalive_interval: Option<f64>,
        tcp_keepalive_retries: Option<u32>,
        tcp_reuse_address: Option<bool>,
        // TCP buffer
        tcp_send_buffer_size: Option<usize>,
        tcp_recv_buffer_size: Option<usize>,
        // TCP binding
        local_ipv4: Option<String>,
        local_ipv6: Option<String>,
        interface: Option<String>,
        // Connection pool
        pool_idle_timeout: Option<f64>,
        pool_max_idle_per_host: Option<usize>,
        pool_max_size: Option<u32>,
        // DNS
        dns_overrides: Option<std::collections::HashMap<String, Vec<String>>>,
    ) -> Result<Self> {
        use std::net::SocketAddr;

        // 构建统一配置对象 (Architecture v2.0: Modular configuration)
        let mut config = ClientConfig::default();

        // === Auth ===
        config.auth.basic = auth;
        config.auth.bearer = auth_bearer;

        // === HTTP ===
        config.http.referer = referer.unwrap_or(true);
        config.http.follow_redirects = follow_redirects.unwrap_or(true);
        config.http.max_redirects = max_redirects.unwrap_or(20);
        config.http.redirect_history = redirect_history.unwrap_or(false);
        config.http.https_only = https_only.unwrap_or(false);

        // HTTP version
        config.http.http_version = if http1_only.unwrap_or(false) {
            HttpVersion::Http1Only
        } else if http2_only.unwrap_or(false) {
            HttpVersion::Http2Only
        } else {
            HttpVersion::Auto
        };

        // === Timeout ===
        if let Some(t) = timeout {
            config.timeout.total = Some(Duration::from_secs_f64(t));
        }
        if let Some(t) = connect_timeout {
            config.timeout.connect = Some(Duration::from_secs_f64(t));
        }
        if let Some(t) = read_timeout {
            config.timeout.read = Some(Duration::from_secs_f64(t));
        }

        // === TLS ===
        config.tls.verify = verify.unwrap_or(true);
        if let Some(v) = verify_hostname {
            config.tls.verify_hostname = v;
        }
        config.tls.ca_cert_file = ca_cert_file.clone();

        // TLS version parsing
        if let Some(ref ver_str) = min_tls_version {
            config.tls.min_version = Self::parse_tls_version(ver_str)?;
        }
        if let Some(ref ver_str) = max_tls_version {
            config.tls.max_version = Self::parse_tls_version(ver_str)?;
        }

        // Load CA certs if specified
        if let Some(ref ca_bundle_path) = ca_cert_file {
            unsafe {
                std::env::set_var("PRIMP_CA_BUNDLE", ca_bundle_path);
            }
        }
        if config.tls.verify {
            if let Some(cert_store) = load_ca_certs() {
                config.tls.cert_store = Some(cert_store.clone());
            }
        }

        // === TCP ===
        if let Some(v) = tcp_nodelay {
            config.tcp.nodelay = v;
        }
        if let Some(v) = tcp_reuse_address {
            config.tcp.reuse_address = v;
        }
        if let Some(v) = tcp_keepalive {
            config.tcp.keepalive = Some(Duration::from_secs_f64(v));
        }
        if let Some(v) = tcp_keepalive_interval {
            config.tcp.keepalive_interval = Some(Duration::from_secs_f64(v));
        }
        if let Some(v) = tcp_keepalive_retries {
            config.tcp.keepalive_retries = Some(v);
        }
        if let Some(v) = tcp_send_buffer_size {
            config.tcp.send_buffer_size = Some(v);
        }
        if let Some(v) = tcp_recv_buffer_size {
            config.tcp.recv_buffer_size = Some(v);
        }

        // TCP binding
        if let Some(ref addr_str) = local_ipv4 {
            config.tcp.local_ipv4 = Some(addr_str.parse()?);
        }
        if let Some(ref addr_str) = local_ipv6 {
            config.tcp.local_ipv6 = Some(addr_str.parse()?);
        }
        if let Some(ref iface) = interface {
            config.tcp.interface = Some(iface.clone());
        }

        // === Pool ===
        if let Some(v) = pool_idle_timeout {
            config.pool.idle_timeout = Some(Duration::from_secs_f64(v));
        }
        if let Some(v) = pool_max_idle_per_host {
            config.pool.max_idle_per_host = v;
        }
        if let Some(v) = pool_max_size {
            config.pool.max_size = Some(v);
        }

        // === Proxy ===
        config.proxy.url = proxy.or_else(|| std::env::var("PRIMP_PROXY").ok());

        // === DNS ===
        if let Some(overrides) = dns_overrides {
            for (domain, addrs) in overrides {
                let socket_addrs: Vec<SocketAddr> = addrs
                    .iter()
                    .filter_map(|s| s.parse().ok())
                    .collect();
                if !socket_addrs.is_empty() {
                    config.dns.overrides.insert(domain, socket_addrs);
                }
            }
        }

        // === Impersonate ===
        config.impersonate.browser = impersonate.clone();
        config.impersonate.os = impersonate_os.clone();

        // === Cookie store ===
        config.cookie_store = cookie_store.unwrap_or(true);

        // 验证配置
        config.validate()?;

        // 创建 cookie jar
        let cookie_jar = Arc::new(wreq::cookie::Jar::default());

        // 使用统一配置构建客户端 (Single source of truth)
        let client = Arc::new(Mutex::new(Self::build_client_from_config(
            &config,
            Some(cookie_jar.clone()),
        )?));

        let rclient = RClient {
            client,
            client_dirty: Arc::new(AtomicBool::new(false)),
            cookie_jar: cookie_jar.clone(),
            deleted_cookies: Arc::new(RwLock::new(HashSet::new())),
            config: Arc::new(RwLock::new(config)),
            headers: Arc::new(RwLock::new(headers)),
            params,
            split_cookies,
        };

        // Set initial cookies if provided
        if let Some(init_cookies) = cookies {
            rclient.update_cookies(init_cookies, None, None)?;
        }

        Ok(rclient)
    }

    pub fn get_headers(&self) -> Result<IndexMapSSR> {
        if let Ok(headers_guard) = self.headers.read() {
            Ok(headers_guard.clone().unwrap_or_else(|| IndexMap::with_capacity_and_hasher(10, RandomState::default())))
        } else {
            Ok(IndexMap::with_capacity_and_hasher(10, RandomState::default()))
        }
    }

    pub fn set_headers(&mut self, new_headers: Option<IndexMapSSR>) -> Result<()> {
        if let Ok(mut headers_guard) = self.headers.write() {
            *headers_guard = new_headers;
        }
        self.client_dirty.store(true, Ordering::Release);
        Ok(())
    }

    pub fn headers_update(&mut self, new_headers: Option<IndexMapSSR>) -> Result<()> {
        if let Some(new_headers) = new_headers {
            if let Ok(mut headers_guard) = self.headers.write() {
                if let Some(existing_headers) = headers_guard.as_mut() {
                    // Update existing headers (preserves insertion order)
                    for (key, value) in new_headers {
                        existing_headers.insert(key, value);
                    }
                } else {
                    // No existing headers, set new ones
                    *headers_guard = Some(new_headers);
                }
            }
            self.client_dirty.store(true, Ordering::Release);
        }
        Ok(())
    }

    /// Set a single header.
    ///
    /// # Arguments
    /// * `name` - Header name
    /// * `value` - Header value
    pub fn set_header(&mut self, name: String, value: String) -> Result<()> {
        if let Ok(mut headers_guard) = self.headers.write() {
            if let Some(existing_headers) = headers_guard.as_mut() {
                existing_headers.insert(name, value);
            } else {
                let mut new_headers = IndexMap::with_capacity_and_hasher(10, RandomState::default());
                new_headers.insert(name, value);
                *headers_guard = Some(new_headers);
            }
        }
        self.client_dirty.store(true, Ordering::Release);
        Ok(())
    }

    /// Get a single header value by name.
    /// Returns None if the header doesn't exist.
    pub fn get_header(&self, name: String) -> Result<Option<String>> {
        if let Ok(headers_guard) = self.headers.read() {
            if let Some(headers) = headers_guard.as_ref() {
                return Ok(headers.get(&name).cloned());
            }
        }
        Ok(None)
    }

    /// Delete a single header by name.
    pub fn delete_header(&mut self, name: String) -> Result<()> {
        if let Ok(mut headers_guard) = self.headers.write() {
            if let Some(headers) = headers_guard.as_mut() {
                headers.shift_remove(&name);
            }
        }
        self.client_dirty.store(true, Ordering::Release);
        Ok(())
    }

    /// Clear all headers.
    pub fn clear_headers(&mut self) -> Result<()> {
        if let Ok(mut headers_guard) = self.headers.write() {
            *headers_guard = None;
        }
        self.client_dirty.store(true, Ordering::Release);
        Ok(())
    }

    #[getter]
    pub fn get_proxy(&self) -> Result<Option<String>> {
        if let Ok(cfg) = self.config.read() {
            Ok(cfg.proxy.url.clone())
        } else {
            Ok(None)
        }
    }

    #[setter]
    pub fn set_proxy(&mut self, proxy: String) -> Result<()> {
        if let Ok(mut cfg) = self.config.write() {
            cfg.proxy.url = Some(proxy);
        }
        self.client_dirty.store(true, Ordering::Release);
        Ok(())
    }

    #[setter]
    pub fn set_impersonate(&mut self, impersonate: String) -> Result<()> {
        if let Ok(mut cfg) = self.config.write() {
            cfg.impersonate.browser = Some(impersonate);
        }
        self.client_dirty.store(true, Ordering::Release);
        Ok(())
    }

    #[setter]
    pub fn set_impersonate_os(&mut self, impersonate_os: String) -> Result<()> {
        if let Ok(mut cfg) = self.config.write() {
            cfg.impersonate.os = Some(impersonate_os);
        }
        self.client_dirty.store(true, Ordering::Release);
        Ok(())
    }

    #[getter]
    pub fn get_impersonate(&self) -> Result<Option<String>> {
        if let Ok(cfg) = self.config.read() {
            Ok(cfg.impersonate.browser.clone())
        } else {
            Ok(None)
        }
    }

    #[getter]
    pub fn get_impersonate_os(&self) -> Result<Option<String>> {
        if let Ok(cfg) = self.config.read() {
            Ok(cfg.impersonate.os.clone())
        } else {
            Ok(None)
        }
    }

    #[getter]
    pub fn get_timeout(&self) -> Result<Option<f64>> {
        if let Ok(cfg) = self.config.read() {
            Ok(cfg.timeout.total.map(|d| d.as_secs_f64()))
        } else {
            Ok(None)
        }
    }

    #[setter]
    pub fn set_timeout(&mut self, timeout: f64) -> Result<()> {
        if let Ok(mut cfg) = self.config.write() {
            cfg.timeout.total = Some(Duration::from_secs_f64(timeout));
        }
        self.client_dirty.store(true, Ordering::Release);
        Ok(())
    }

    #[getter]
    pub fn get_auth(&self) -> Result<Option<(String, Option<String>)>> {
        if let Ok(cfg) = self.config.read() {
            Ok(cfg.auth.basic.clone())
        } else {
            Ok(None)
        }
    }

    #[setter]
    pub fn set_auth(&mut self, auth: (String, Option<String>)) -> Result<()> {
        if let Ok(mut cfg) = self.config.write() {
            cfg.auth.basic = Some(auth);
        }
        self.client_dirty.store(true, Ordering::Release);
        Ok(())
    }

    #[getter]
    pub fn get_auth_bearer(&self) -> Result<Option<String>> {
        if let Ok(cfg) = self.config.read() {
            Ok(cfg.auth.bearer.clone())
        } else {
            Ok(None)
        }
    }

    #[setter]
    pub fn set_auth_bearer(&mut self, token: String) -> Result<()> {
        if let Ok(mut cfg) = self.config.write() {
            cfg.auth.bearer = Some(token);
        }
        self.client_dirty.store(true, Ordering::Release);
        Ok(())
    }

    /// Get all cookies from the jar without requiring a URL.
    /// Returns a dictionary of cookie names to values.
    fn get_all_cookies(&self) -> Result<IndexMapSSR> {
        let mut cookies = IndexMap::with_capacity_and_hasher(10, RandomState::default());
        let deleted = self.deleted_cookies.read().unwrap();

        for cookie in self.cookie_jar.get_all() {
            let name = cookie.name();
            // Filter out deleted cookies
            if !deleted.contains(name) {
                cookies.insert(name.to_string(), cookie.value().to_string());
            }
        }
        Ok(cookies)
    }

    /// Set a single cookie without requiring a URL.
    ///
    /// # Arguments
    /// * `name` - Cookie name
    /// * `value` - Cookie value
    /// * `domain` - Optional domain (e.g., ".example.com"). If None, uses a wildcard domain.
    /// * `path` - Optional path (e.g., "/"). If None, uses "/".
    #[pyo3(signature = (name, value, domain=None, path=None))]
    fn set_cookie(
        &self,
        name: String,
        value: String,
        domain: Option<String>,
        path: Option<String>,
    ) -> Result<()> {
        let domain = domain.unwrap_or_else(|| "0.0.0.0".to_string());
        let path = path.unwrap_or_else(|| "/".to_string());

        // Construct a URL from domain and path
        let url = format!("http://{}{}", domain, path);
        let uri: wreq::Uri = url.parse()?;

        let cookie_str = format!("{}={}", name, value);
        self.cookie_jar.add_cookie_str(&cookie_str, &uri);

        // Remove from deleted list
        self.deleted_cookies.write().unwrap().remove(&name);
        Ok(())
    }

    /// Get a single cookie value by name.
    /// Returns None if the cookie doesn't exist.
    #[pyo3(signature = (name))]
    fn get_cookie(&self, name: String) -> Result<Option<String>> {
        // Check if deleted
        if self.deleted_cookies.read().unwrap().contains(&name) {
            return Ok(None);
        }

        for cookie in self.cookie_jar.get_all() {
            if cookie.name() == name {
                return Ok(Some(cookie.value().to_string()));
            }
        }
        Ok(None)
    }

    /// Update multiple cookies at once without requiring a URL.
    ///
    /// # Arguments
    /// * `cookies` - Dictionary of cookie names to values
    /// * `domain` - Optional domain. If None, uses a wildcard domain.
    /// * `path` - Optional path. If None, uses "/".
    #[pyo3(signature = (cookies, domain=None, path=None))]
    fn update_cookies(
        &self,
        cookies: IndexMapSSR,
        domain: Option<String>,
        path: Option<String>,
    ) -> Result<()> {
        let domain = domain.unwrap_or_else(|| "0.0.0.0".to_string());
        let path = path.unwrap_or_else(|| "/".to_string());

        let url = format!("http://{}{}", domain, path);
        let uri: wreq::Uri = url.parse()?;

        let mut deleted = self.deleted_cookies.write().unwrap();
        for (name, value) in cookies {
            let cookie_str = format!("{}={}", name, value);
            self.cookie_jar.add_cookie_str(&cookie_str, &uri);
            // Remove from deleted list
            deleted.remove(&name);
        }
        Ok(())
    }

    /// Delete a single cookie by name.
    /// Sets the cookie to an empty value with Max-Age=0 to delete it.
    #[pyo3(signature = (name))]
    fn delete_cookie(&self, name: String) -> Result<()> {
        // To delete a cookie, set it with an expiration in the past
        let url = "http://0.0.0.0/";
        let uri: wreq::Uri = url.parse()?;

        // Set cookie with Max-Age=0 to delete it
        let cookie_str = format!("{}=; Max-Age=0", name);
        self.cookie_jar.add_cookie_str(&cookie_str, &uri);

        // Add to deleted list
        self.deleted_cookies.write().unwrap().insert(name);
        Ok(())
    }

    /// Clear all cookies from the jar.
    /// Sets all cookies with Max-Age=0 to mark them as expired.
    fn clear_cookies(&self) -> Result<()> {
        // Get all cookie names first to avoid borrow issues
        let cookie_names: Vec<String> = self.cookie_jar
            .get_all()
            .map(|c| c.name().to_string())
            .collect();

        // Set each cookie with Expires in the past to mark as deleted
        let url = "http://0.0.0.0/";
        let uri: wreq::Uri = url.parse()?;

        let mut deleted = self.deleted_cookies.write().unwrap();
        for name in cookie_names {
            // Use Expires with a date in the past (Unix epoch)
            let cookie_str = format!("{}=; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Max-Age=0", name);
            self.cookie_jar.add_cookie_str(&cookie_str, &uri);
            // Add to deleted list
            deleted.insert(name);
        }
        Ok(())
    }

    /// Constructs an HTTP request with the given method, URL, and optionally sets a timeout, headers, and query parameters.
    /// Sends the request and returns a `Response` object containing the server's response.
    ///
    /// # Arguments
    ///
    /// * `method` - The HTTP method to use (e.g., "GET", "POST").
    /// * `url` - The URL to which the request will be made.
    /// * `params` - A map of query parameters to append to the URL. Default is None.
    /// * `headers` - A map of HTTP headers to send with the request. Default is None.
    /// * `cookies` - An optional map of cookies to send with requests as the `Cookie` header.
    /// * `content` - The content to send in the request body as bytes. Default is None.
    /// * `data` - The form data to send in the request body. Default is None.
    /// * `json` -  A JSON serializable object to send in the request body. Default is None.
    /// * `files` - Files to upload as multipart/form-data. Supports:
    ///   - dict[str, str]: field name to file path
    ///   - dict[str, bytes]: field name to file content
    ///   - dict[str, tuple]: field name to (filename, content, mime_type)
    ///   Can be combined with `data` for mixed form fields and files.
    /// * `auth` - A tuple containing the username and an optional password for basic authentication. Default is None.
    /// * `auth_bearer` - A string representing the bearer token for bearer token authentication. Default is None.
    /// * `timeout` - The timeout for the request in seconds. Default is 30.
    /// * `proxy` - An optional proxy URL for this specific request (overrides client proxy). Default is None.
    /// * `verify` - An optional boolean to verify SSL certificates for this specific request (overrides client verify). Default is None.
    ///
    /// # Returns
    ///
    /// * `Response` - A response object containing the server's response to the request.
    ///
    /// # Errors
    ///
    /// * `PyException` - If there is an error making the request.
    #[pyo3(signature = (method, url, params=None, headers=None, cookies=None, content=None,
        data=None, json=None, files=None, follow_redirects=None, auth=None, auth_bearer=None, timeout=None, proxy=None, verify=None))]
    fn request(
        &self,
        py: Python,
        method: &str,
        url: &str,
        params: Option<IndexMapSSR>,
        headers: Option<IndexMapSSR>,
        cookies: Option<IndexMapSSR>,
        content: Option<Vec<u8>>,
        data: Option<&Bound<'_, PyAny>>,
        json: Option<&Bound<'_, PyAny>>,
        files: Option<&Bound<'_, PyAny>>,
        follow_redirects: Option<bool>,
        auth: Option<(String, Option<String>)>,
        auth_bearer: Option<String>,
        timeout: Option<f64>,
        proxy: Option<String>,
        verify: Option<bool>,
    ) -> Result<Response> {
        // Rebuild client if dirty flag is set (lazy rebuild optimization)
        self.rebuild_client_if_dirty()?;

        // Check if we need to create a temporary client with overridden settings
        let needs_temp_client = proxy.is_some() || verify.is_some() || timeout.is_some();

        let client = if needs_temp_client {
            // Create temporary client with overridden settings
            self.build_temp_client_with_overrides(proxy.as_deref(), verify, timeout)?
        } else {
            Arc::clone(&self.client)
        };

        // Read configuration once at the beginning
        let base_config = self.config.read().unwrap();

        let method = Method::from_bytes(method.as_bytes())?;
        let is_post_put_patch = matches!(method, Method::POST | Method::PUT | Method::PATCH);
        let params = params.or_else(|| self.params.clone());
        let data_value: Option<Value> = data.map(depythonize).transpose()?;
        let json_value: Option<Value> = json.map(depythonize).transpose()?;
        let auth = auth.or(base_config.auth.basic.clone());
        let auth_bearer = auth_bearer.or(base_config.auth.bearer.clone());
        let effective_timeout = timeout.or(base_config.timeout.total.map(|d| d.as_secs_f64()));

        // Process files before async block (must be done in Python context)
        enum FileData {
            Path(String, String), // (field_name, file_path)
            Bytes(String, String, Vec<u8>), // (field_name, filename, bytes)
            BytesWithMime(String, String, Vec<u8>, String), // (field_name, filename, bytes, mime)
        }

        let mut files_data: Vec<FileData> = Vec::new();
        if let Some(files_obj) = files {
            if let Ok(files_dict) = files_obj.downcast::<pyo3::types::PyDict>() {
                for (key, value) in files_dict.iter() {
                    let field_name: String = key.extract()?;

                    // Case 1: String (file path)
                    if let Ok(file_path) = value.extract::<String>() {
                        files_data.push(FileData::Path(field_name, file_path));
                    }
                    // Case 2: Bytes (raw data)
                    else if let Ok(bytes) = value.extract::<Vec<u8>>() {
                        files_data.push(FileData::Bytes(field_name.clone(), field_name, bytes));
                    }
                    // Case 3: Tuple (filename, data, [mime_type])
                    else if let Ok(tuple) = value.downcast::<pyo3::types::PyTuple>() {
                        let len = tuple.len();
                        if len >= 2 {
                            let filename: String = tuple.get_item(0)?.extract()?;

                            // Data can be bytes or string (path)
                            if let Ok(bytes) = tuple.get_item(1)?.extract::<Vec<u8>>() {
                                if len >= 3 {
                                    if let Ok(mime_str) = tuple.get_item(2)?.extract::<String>() {
                                        files_data.push(FileData::BytesWithMime(
                                            field_name.clone(),
                                            filename,
                                            bytes,
                                            mime_str,
                                        ));
                                    } else {
                                        files_data.push(FileData::Bytes(field_name.clone(), filename, bytes));
                                    }
                                } else {
                                    files_data.push(FileData::Bytes(field_name.clone(), filename, bytes));
                                }
                            } else if let Ok(path) = tuple.get_item(1)?.extract::<String>() {
                                files_data.push(FileData::Path(field_name, path));
                            }
                        }
                    }
                }
            }
        }

        let has_files = !files_data.is_empty();

        // Get effective follow_redirects setting (request param overrides client setting)
        let effective_follow_redirects = follow_redirects.unwrap_or(base_config.http.follow_redirects);
        let effective_max_redirects = base_config.http.max_redirects;

        let future = async {
            // Create request builder
            let mut request_builder = client.lock().unwrap().request(method, url);

            // Per-request redirect control
            if effective_follow_redirects {
                request_builder = request_builder.redirect(Policy::limited(effective_max_redirects));
            } else {
                request_builder = request_builder.redirect(Policy::none());
            }

            // Params
            if let Some(params) = params {
                request_builder = request_builder.query(&params);
            }

            // Calculate body content and length for POST/PUT/PATCH (before setting headers)
            let (body_bytes, content_type_header): (Option<Vec<u8>>, Option<String>) = if is_post_put_patch {
                if has_files {
                    // Multipart will be handled later, can't pre-calculate
                    (None, None)
                } else if let Some(content) = content {
                    // Raw bytes content - move instead of clone to avoid allocation
                    (Some(content), None)
                } else if let Some(form_data) = &data_value {
                    // Data - smart handling
                    if let Some(json_str) = form_data.as_str() {
                        // JSON string
                        if let Ok(parsed_json) = serde_json::from_str::<Value>(json_str) {
                            let serialized = serde_json::to_vec(&parsed_json)?;
                            (Some(serialized), Some("application/json".to_string()))
                        } else {
                            (Some(json_str.as_bytes().to_vec()), None)
                        }
                    } else {
                        // Check if nested
                        let is_nested = if let Some(obj) = form_data.as_object() {
                            obj.values().any(|v| v.is_object() || v.is_array())
                        } else {
                            false
                        };

                        if is_nested {
                            // Nested - use JSON
                            let serialized = serde_json::to_vec(&form_data)?;
                            (Some(serialized), Some("application/json".to_string()))
                        } else {
                            // Flat - use form-urlencoded
                            let encoded = serde_urlencoded::to_string(&form_data)?;
                            (Some(encoded.as_bytes().to_vec()), Some("application/x-www-form-urlencoded".to_string()))
                        }
                    }
                } else if let Some(json_data) = &json_value {
                    // JSON
                    let serialized = serde_json::to_vec(&json_data)?;
                    (Some(serialized), Some("application/json".to_string()))
                } else {
                    (None, None)
                }
            } else {
                (None, None)
            };

            // Cookies - get effective cookies (from parameter or cookie_jar)
            // Do this BEFORE processing headers so we can include cookies in header ordering
            let effective_cookies = if let Some(cookies) = cookies {
                Some(cookies)
            } else {
                // Get cookies from cookie_jar
                let jar_cookies = self.get_all_cookies().ok();
                jar_cookies.filter(|c| !c.is_empty())
            };

            // Headers - reorder to match browser behavior: Host first, then Content-Length, then others
            // Request headers REPLACE client headers (not merge) to avoid conflicts with
            // emulation defaults when user didn't set client headers initially
            let effective_headers = {
                if let Some(request_hdrs) = headers {
                    // Request headers provided - use ONLY request headers (replace, not merge)
                    // This prevents double headers when client was initialized without headers
                    // but emulation defaults were added
                    request_hdrs
                } else {
                    // No request headers - use client headers or empty map
                    self.headers.read().ok()
                        .and_then(|guard| guard.clone())
                        .unwrap_or_else(|| IndexMapSSR::with_capacity_and_hasher(4, RandomState::default()))
                }
            };

            // Always process headers (even if empty) to ensure Content-Type and Content-Length are added
            {
                let hdrs = &effective_headers;
                // Create a new ordered map with strict ordering
                let mut reordered_headers = IndexMap::with_capacity_and_hasher(hdrs.len() + 2, RandomState::default());

                // 1. First, add Host header if present (case-insensitive check)
                let host_value = hdrs.get("Host")
                    .or_else(|| hdrs.get("host"))
                    .or_else(|| hdrs.get("HOST"));

                if let Some(host) = host_value {
                    reordered_headers.insert("Host".to_string(), host.clone());
                }

                // 2. For POST/PUT/PATCH with body, add Content-Length in 2nd position
                if let Some(ref body) = body_bytes {
                    let content_length = body.len().to_string();
                    reordered_headers.insert("Content-Length".to_string(), content_length);
                } else if has_files {
                    // For multipart, we can't pre-calculate, but reserve the position
                    // This will be overwritten by wreq, but maintains position
                    reordered_headers.insert("Content-Length".to_string(), "0".to_string());
                }

                // 3. Only add auto-calculated Content-Type in 3rd position if user didn't provide one
                // This allows user's Content-Type to maintain its original position in headers
                let user_has_content_type = hdrs.iter()
                    .any(|(k, _)| k.to_lowercase() == "content-type");

                if !user_has_content_type {
                    if let Some(ct) = content_type_header {
                        // No user Content-Type, use auto-calculated in 3rd position
                        reordered_headers.insert("Content-Type".to_string(), ct);
                    }
                }

                // 4. Add all other headers in their original order (including user's Content-Type if provided)
                // Skip: Host, Content-Length (already handled above)
                // Skip: priority, cookie (will be added at the end)
                let mut priority_header: Option<(String, String)> = None;
                let mut cookie_from_headers: Option<(String, String)> = None;

                for (key, value) in hdrs.iter() {
                    let key_lower = key.to_lowercase();

                    // Skip host, content-length (already handled above)
                    if key_lower == "host" || key_lower == "content-length" {
                        continue;
                    }

                    // For Content-Type: skip if already auto-added, otherwise add in user's original position
                    if key_lower == "content-type" {
                        // Check if we already auto-added Content-Type in step 3
                        let already_exists = reordered_headers.keys().any(|k| k.to_lowercase() == "content-type");
                        if already_exists {
                            continue;  // Skip, already auto-added
                        }
                        // Otherwise, fall through to add user's Content-Type in original position
                    }

                    // Check if this header (by lowercase name) is already in reordered_headers
                    let already_exists = reordered_headers.keys().any(|k| k.to_lowercase() == key_lower);
                    if already_exists {
                        continue;
                    }

                    if key_lower == "priority" {
                        priority_header = Some((key.clone(), value.clone()));
                    } else if key_lower == "cookie" {
                        cookie_from_headers = Some((key.clone(), value.clone()));
                    } else {
                        reordered_headers.insert(key.clone(), value.clone());
                    }
                }

                // 5. Handle cookies based on split_cookies option
                let should_add_cookies_separately = self.split_cookies.unwrap_or(false);

                // Build orig_headermap manually to control exact order
                let mut orig_headermap = OrigHeaderMap::with_capacity(reordered_headers.len() + 10);

                // Add all current headers to orig_headermap
                for (key, _) in reordered_headers.iter() {
                    orig_headermap.insert(key.clone());
                }

                if should_add_cookies_separately {
                    // Split cookies: add each cookie as a separate header in orig_headermap
                    if let Some(cookies) = &effective_cookies {
                        for (_k, _v) in cookies.iter() {
                            // Add to orig_headermap for ordering
                            orig_headermap.insert("cookie".to_string());
                            // Add to request_builder after applying headers
                        }
                    } else if let Some((_, ref value)) = cookie_from_headers {
                        // Split the cookie value and add each part
                        for part in value.split(';') {
                            let part = part.trim();
                            if !part.is_empty() {
                                orig_headermap.insert("cookie".to_string());
                            }
                        }
                    }

                    // Add priority to orig_headermap at the end
                    if let Some((ref key, _)) = priority_header {
                        orig_headermap.insert(key.clone());
                    }
                } else {
                    // Merge cookies into single header
                    if let Some(cookies) = &effective_cookies {
                        if !cookies.is_empty() {
                            let cookie_value = cookies
                                .iter()
                                .map(|(k, v)| format!("{}={}", k, v))
                                .collect::<Vec<_>>()
                                .join("; ");
                            reordered_headers.insert("cookie".to_string(), cookie_value);
                            orig_headermap.insert("cookie".to_string());
                        }
                    } else if let Some((ref key, ref value)) = cookie_from_headers {
                        reordered_headers.insert(key.clone(), value.clone());
                        orig_headermap.insert(key.clone());
                    }

                    // Add priority at the very end
                    if let Some((ref key, ref value)) = priority_header {
                        reordered_headers.insert(key.clone(), value.clone());
                        orig_headermap.insert(key.clone());
                    }
                }

                // Apply the reordered headers with strict order preservation
                let headers_headermap = reordered_headers.to_headermap();
                request_builder = request_builder
                    .headers(headers_headermap)
                    .orig_headers(orig_headermap);

                // If split_cookies=true, add cookies separately using header_append
                if should_add_cookies_separately {
                    if let Some(cookies) = &effective_cookies {
                        if !cookies.is_empty() {
                            for (k, v) in cookies.iter() {
                                let cookie_value = format!("{}={}", k, v);
                                request_builder = request_builder.header_append("cookie", cookie_value);
                            }
                        }
                    } else if let Some((_, ref value)) = cookie_from_headers {
                        // If cookie came from headers, split it
                        for part in value.split(';') {
                            let part = part.trim();
                            if !part.is_empty() {
                                request_builder = request_builder.header_append("cookie", part);
                            }
                        }
                    }

                    // Add priority after cookies to maintain order
                    // Use header_append to ensure it's added at the end
                    if let Some((ref key, ref value)) = priority_header {
                        request_builder = request_builder.header_append(key, value);
                    }
                }
            }  // End of header processing block

            // Only if method POST || PUT || PATCH
            if is_post_put_patch {
                // Files - handle multipart/form-data
                if has_files {
                    let mut form = multipart::Form::new();

                    // Add data fields to multipart if present
                    if let Some(form_data) = &data_value {
                        if let Some(obj) = form_data.as_object() {
                            for (key, value) in obj {
                                let value_str = match value {
                                    Value::String(s) => s.clone(),
                                    _ => value.to_string(),
                                };
                                form = form.text(key.clone(), value_str);
                            }
                        }
                    }

                    // Process files
                    for file_data in files_data {
                        match file_data {
                            FileData::Path(field_name, file_path) => {
                                let file = File::open(&file_path).await?;
                                let stream = FramedRead::new(file, BytesCodec::new());
                                let file_body = Body::wrap_stream(stream);

                                // Extract filename from path
                                let filename = std::path::Path::new(&file_path)
                                    .file_name()
                                    .and_then(|n| n.to_str())
                                    .unwrap_or(&field_name)
                                    .to_string();

                                let part = multipart::Part::stream(file_body).file_name(filename);
                                form = form.part(field_name, part);
                            }
                            FileData::Bytes(field_name, filename, bytes) => {
                                let part = multipart::Part::bytes(bytes).file_name(filename);
                                form = form.part(field_name, part);
                            }
                            FileData::BytesWithMime(field_name, filename, bytes, mime_str) => {
                                let mut part = multipart::Part::bytes(bytes).file_name(filename);
                                if let Ok(mime) = mime_str.parse::<mime::Mime>() {
                                    part = part.mime_str(mime.as_ref())?;
                                }
                                form = form.part(field_name, part);
                            }
                        }
                    }

                    request_builder = request_builder.multipart(form);
                }
                // Use pre-serialized body bytes
                else if let Some(body) = body_bytes {
                    request_builder = request_builder.body(body);
                }
            }

            // Auth
            if let Some((username, password)) = auth {
                request_builder = request_builder.basic_auth(username, password);
            } else if let Some(token) = auth_bearer {
                request_builder = request_builder.bearer_auth(token);
            }

            // Timeout (use effective_timeout instead of timeout)
            if let Some(seconds) = effective_timeout {
                request_builder = request_builder.timeout(Duration::from_secs_f64(seconds));
            }

            // Send the request and await the response
            let resp: wreq::Response = request_builder.send().await?;
            let url: String = resp.uri().to_string();
            let status_code = resp.status().as_u16();

            tracing::info!("response: {} {}", url, status_code);
            Ok((resp, url, status_code))
        };

        // Execute an async future, releasing the Python GIL for concurrency.
        // Use Tokio global runtime to block on the future.
        let response: Result<(wreq::Response, String, u16)> =
            py.detach(|| RUNTIME.block_on(future));
        let result = response?;
        let resp = http::Response::from(result.0);
        let url = result.1;
        let status_code = result.2;
        Ok(Response {
            resp,
            _content: None,
            _encoding: None,
            _headers: None,
            _cookies: None,
            url,
            status_code,
        })
    }
}

// ========== New Architecture v2.0: Unified Implementation ==========
impl RClient {
    /// Parse TLS version string to TlsVersion enum
    fn parse_tls_version(ver_str: &str) -> Result<Option<wreq::tls::TlsVersion>> {
        use wreq::tls::TlsVersion;
        match ver_str {
            "1.0" => Ok(Some(TlsVersion::TLS_1_0)),
            "1.1" => Ok(Some(TlsVersion::TLS_1_1)),
            "1.2" => Ok(Some(TlsVersion::TLS_1_2)),
            "1.3" => Ok(Some(TlsVersion::TLS_1_3)),
            _ => Err(anyhow::anyhow!("Invalid TLS version: {}", ver_str)),
        }
    }

    /// Unified client build function (eliminates 95% code duplication)
    /// Single source of truth for all client builds
    fn build_client_from_config(
        config: &ClientConfig,
        cookie_jar: Option<Arc<wreq::cookie::Jar>>,
    ) -> Result<wreq::Client> {
        // Apply all configuration modules via their apply() methods
        let builder = config.apply_to_builder(cookie_jar)?;

        // Apply browser impersonation if specified
        let builder = if let Some(ref browser) = config.impersonate.browser {
            let imp = Emulation::from_str(browser.as_str())?;
            let imp_os = if let Some(ref os) = config.impersonate.os {
                EmulationOS::from_str(os.as_str())?
            } else {
                EmulationOS::default()
            };
            let emulation_option = EmulationOption::builder()
                .emulation(imp)
                .emulation_os(imp_os)
                .skip_headers(true)
                .build();
            builder.emulation(emulation_option)
        } else {
            builder
        };

        Ok(builder.build()?)
    }

    /// Rebuild client if dirty flag is set (lazy rebuild optimization)
    fn rebuild_client_if_dirty(&self) -> Result<()> {
        if self.client_dirty.load(Ordering::Acquire) {
            if let Ok(mut client_guard) = self.client.lock() {
                if self.client_dirty.load(Ordering::Acquire) {
                    let config = self.config.read().unwrap();
                    *client_guard = Self::build_client_from_config(&config, Some(self.cookie_jar.clone()))?;
                    self.client_dirty.store(false, Ordering::Release);
                }
            }
        }
        Ok(())
    }

    /// Build temporary client with overrides (for per-request settings)
    fn build_temp_client_with_overrides(
        &self,
        proxy_override: Option<&str>,
        verify_override: Option<bool>,
        timeout_override: Option<f64>,
    ) -> Result<Arc<Mutex<wreq::Client>>> {
        // Clone base config
        let mut config = self.config.read().unwrap().clone();

        // Apply overrides
        if let Some(proxy) = proxy_override {
            config.proxy.url = Some(proxy.to_string());
        }
        if let Some(verify) = verify_override {
            config.tls.verify = verify;
        }
        if let Some(timeout) = timeout_override {
            config.timeout.total = Some(Duration::from_secs_f64(timeout));
        }

        // Build temporary client
        let client = Self::build_client_from_config(&config, Some(self.cookie_jar.clone()))?;
        Ok(Arc::new(Mutex::new(client)))
    }
}

#[pymodule]
fn never_primp(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    pyo3_log::init();

    m.add_class::<RClient>()?;
    Ok(())
}
