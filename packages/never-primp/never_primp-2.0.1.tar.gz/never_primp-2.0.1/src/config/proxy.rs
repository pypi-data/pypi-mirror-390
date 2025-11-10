use anyhow::Result;

/// 代理配置
#[derive(Clone, Default)]
pub struct ProxyConfig {
    pub url: Option<String>,
}

impl ProxyConfig {
    /// 应用到 wreq ClientBuilder
    ///
    /// 支持的代理格式（v6.0.0-rc.21+）：
    /// - http://proxy:port
    /// - socks5://proxy:port
    /// - http://user:pass@proxy:port
    /// - http://user@proxy:port (rc.21+ 支持省略密码)
    pub fn apply(&self, builder: wreq::ClientBuilder) -> Result<wreq::ClientBuilder> {
        if let Some(ref proxy_url) = self.url {
            // 将 https:// 替换为 http://（wreq 代理限制）
            let http_proxy = if proxy_url.starts_with("https://") {
                proxy_url.replacen("https://", "http://", 1)
            } else {
                proxy_url.clone()
            };
            Ok(builder.proxy(wreq::Proxy::all(&http_proxy)?))
        } else {
            // 从环境变量读取代理
            if let Ok(env_proxy) = std::env::var("PRIMP_PROXY") {
                let http_proxy = if env_proxy.starts_with("https://") {
                    env_proxy.replacen("https://", "http://", 1)
                } else {
                    env_proxy
                };
                Ok(builder.proxy(wreq::Proxy::all(&http_proxy)?))
            } else {
                Ok(builder)
            }
        }
    }
}
