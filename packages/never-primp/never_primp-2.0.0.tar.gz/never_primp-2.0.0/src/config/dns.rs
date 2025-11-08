use std::collections::HashMap;
use std::net::SocketAddr;

/// DNS 配置
#[derive(Clone, Default)]
pub struct DnsConfig {
    pub overrides: HashMap<String, Vec<SocketAddr>>,
    pub use_hickory: bool,
}

impl DnsConfig {
    /// 应用到 wreq ClientBuilder
    pub fn apply(&self, mut builder: wreq::ClientBuilder) -> wreq::ClientBuilder {
        // 应用 DNS 覆盖
        for (domain, addrs) in &self.overrides {
            builder = builder.resolve_to_addrs(domain, addrs);
        }

        // 禁用 hickory-dns（如果需要）
        #[cfg(feature = "hickory-dns")]
        if !self.use_hickory {
            builder = builder.no_hickory_dns();
        }

        builder
    }
}
