use anyhow::Result;
use std::net::{IpAddr, Ipv4Addr, Ipv6Addr};
use std::time::Duration;

/// TCP 连接配置
#[derive(Clone, Debug)]
pub struct TcpConfig {
    // 基础选项
    pub nodelay: bool,
    pub reuse_address: bool,

    // Keepalive 选项
    pub keepalive: Option<Duration>,
    pub keepalive_interval: Option<Duration>,
    pub keepalive_retries: Option<u32>,

    // 缓冲区选项
    pub send_buffer_size: Option<usize>,
    pub recv_buffer_size: Option<usize>,

    // 连接选项
    pub connect_timeout: Option<Duration>,
    pub happy_eyeballs_timeout: Option<Duration>,

    // 绑定选项
    pub local_address: Option<IpAddr>,
    pub local_ipv4: Option<Ipv4Addr>,
    pub local_ipv6: Option<Ipv6Addr>,
    pub interface: Option<String>,

    // Linux/Android 特定
    #[cfg(any(target_os = "android", target_os = "fuchsia", target_os = "linux"))]
    pub user_timeout: Option<Duration>,
}

impl Default for TcpConfig {
    fn default() -> Self {
        Self {
            nodelay: true,
            reuse_address: false,
            keepalive: Some(Duration::from_secs(15)),
            keepalive_interval: Some(Duration::from_secs(15)),
            keepalive_retries: Some(3),
            send_buffer_size: None,
            recv_buffer_size: None,
            connect_timeout: None,
            happy_eyeballs_timeout: Some(Duration::from_millis(300)),
            local_address: None,
            local_ipv4: None,
            local_ipv6: None,
            interface: None,
            #[cfg(any(target_os = "android", target_os = "fuchsia", target_os = "linux"))]
            user_timeout: Some(Duration::from_secs(30)),
        }
    }
}

impl TcpConfig {
    /// 验证配置的有效性
    pub fn validate(&self) -> Result<()> {
        if let Some(timeout) = self.connect_timeout {
            if timeout.as_secs() > 300 {
                return Err(anyhow::anyhow!("connect_timeout too large (max 300s)"));
            }
        }
        Ok(())
    }

    /// 应用到 wreq ClientBuilder
    pub fn apply(&self, builder: wreq::ClientBuilder) -> wreq::ClientBuilder {
        let mut builder = builder
            .tcp_nodelay(self.nodelay)
            .tcp_reuse_address(self.reuse_address);

        if let Some(ka) = self.keepalive {
            builder = builder.tcp_keepalive(ka);
        }
        if let Some(interval) = self.keepalive_interval {
            builder = builder.tcp_keepalive_interval(interval);
        }
        if let Some(retries) = self.keepalive_retries {
            builder = builder.tcp_keepalive_retries(retries);
        }
        if let Some(size) = self.send_buffer_size {
            builder = builder.tcp_send_buffer_size(size);
        }
        if let Some(size) = self.recv_buffer_size {
            builder = builder.tcp_recv_buffer_size(size);
        }
        if let Some(timeout) = self.connect_timeout {
            builder = builder.connect_timeout(timeout);
        }
        if let Some(timeout) = self.happy_eyeballs_timeout {
            builder = builder.tcp_happy_eyeballs_timeout(timeout);
        }
        if let Some(addr) = self.local_address {
            builder = builder.local_address(addr);
        }
        if self.local_ipv4.is_some() || self.local_ipv6.is_some() {
            builder = builder.local_addresses(self.local_ipv4, self.local_ipv6);
        }
        if let Some(ref _iface) = self.interface {
            #[cfg(any(
                target_os = "android",
                target_os = "fuchsia",
                target_os = "linux",
                target_os = "macos",
                target_os = "ios",
                target_os = "tvos",
                target_os = "watchos",
                target_os = "visionos",
            ))]
            {
                builder = builder.interface(_iface.clone());
            }
        }
        #[cfg(any(target_os = "android", target_os = "fuchsia", target_os = "linux"))]
        if let Some(timeout) = self.user_timeout {
            builder = builder.tcp_user_timeout(timeout);
        }

        builder
    }
}
