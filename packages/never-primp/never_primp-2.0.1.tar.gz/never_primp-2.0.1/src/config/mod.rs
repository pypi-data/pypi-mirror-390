pub mod dns;
pub mod http;
pub mod pool;
pub mod proxy;
pub mod tcp;
pub mod timeout;
pub mod tls;

use anyhow::Result;
use foldhash::fast::RandomState;
use indexmap::IndexMap;

pub use dns::DnsConfig;
pub use http::{HttpConfig, HttpVersion};
pub use pool::PoolConfig;
pub use proxy::ProxyConfig;
pub use tcp::TcpConfig;
pub use timeout::TimeoutConfig;
pub use tls::TlsConfig;

// Type alias kept for future use
#[allow(dead_code)]
type IndexMapSSR = IndexMap<String, String, RandomState>;

/// 主配置结构体 - 所有配置的容器
#[derive(Clone)]
pub struct ClientConfig {
    pub tcp: TcpConfig,
    pub tls: TlsConfig,
    pub http: HttpConfig,
    pub timeout: TimeoutConfig,
    pub pool: PoolConfig,
    pub proxy: ProxyConfig,
    pub dns: DnsConfig,
    pub auth: AuthConfig,
    pub impersonate: ImpersonateConfig,
    pub cookie_store: bool,
}

/// 认证配置
#[derive(Clone, Default)]
pub struct AuthConfig {
    pub basic: Option<(String, Option<String>)>,
    pub bearer: Option<String>,
}

/// 浏览器模拟配置
#[derive(Clone, Default)]
pub struct ImpersonateConfig {
    pub browser: Option<String>,
    pub os: Option<String>,
}

impl Default for ClientConfig {
    fn default() -> Self {
        Self {
            tcp: TcpConfig::default(),
            tls: TlsConfig::default(),
            http: HttpConfig::default(),
            timeout: TimeoutConfig::default(),
            pool: PoolConfig::default(),
            proxy: ProxyConfig::default(),
            dns: DnsConfig::default(),
            auth: AuthConfig::default(),
            impersonate: ImpersonateConfig::default(),
            cookie_store: true,
        }
    }
}

impl ClientConfig {
    /// 验证配置的有效性
    pub fn validate(&self) -> Result<()> {
        self.tcp.validate()?;
        self.tls.validate()?;
        self.http.validate()?;
        self.timeout.validate()?;
        self.pool.validate()?;
        Ok(())
    }

    /// 应用所有配置到 wreq ClientBuilder
    pub fn apply_to_builder(
        &self,
        cookie_jar: Option<std::sync::Arc<wreq::cookie::Jar>>,
    ) -> Result<wreq::ClientBuilder> {
        let mut builder = wreq::Client::builder();

        // 应用各模块配置
        builder = self.tcp.apply(builder);
        builder = self.tls.apply(builder);
        builder = self.timeout.apply(builder);
        builder = self.http.apply(builder);
        builder = self.pool.apply(builder);
        builder = self.dns.apply(builder);
        builder = self.proxy.apply(builder)?;

        // Cookie store
        if self.cookie_store {
            if let Some(jar) = cookie_jar {
                builder = builder.cookie_provider(jar);
            }
        }

        Ok(builder)
    }
}

/// 请求级配置覆盖（用于单个请求覆盖客户端配置）
#[allow(dead_code)]
#[derive(Clone, Default)]
pub struct ConfigOverride {
    pub timeout: Option<TimeoutConfig>,
    pub proxy: Option<ProxyConfig>,
    pub tcp_local_address: Option<std::net::IpAddr>,
    pub tcp_interface: Option<String>,
    pub follow_redirects: Option<bool>,
}

impl ConfigOverride {
    /// 合并到客户端配置，返回新配置
    pub fn merge_with(&self, base: &ClientConfig) -> ClientConfig {
        let mut config = base.clone();

        // 合并 timeout
        if let Some(ref timeout_override) = self.timeout {
            config.timeout.merge(timeout_override);
        }

        // 合并 proxy
        if let Some(ref proxy_override) = self.proxy {
            config.proxy = proxy_override.clone();
        }

        // 合并 TCP local_address
        if let Some(addr) = self.tcp_local_address {
            config.tcp.local_address = Some(addr);
        }

        // 合并 TCP interface
        if let Some(ref iface) = self.tcp_interface {
            config.tcp.interface = Some(iface.clone());
        }

        // 合并 follow_redirects
        if let Some(follow) = self.follow_redirects {
            config.http.follow_redirects = follow;
        }

        config
    }
}
