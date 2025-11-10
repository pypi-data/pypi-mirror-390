use anyhow::Result;
use std::time::Duration;

/// 超时配置
#[derive(Clone, Debug)]
pub struct TimeoutConfig {
    pub total: Option<Duration>,    // 总超时（从连接到响应完成）
    pub connect: Option<Duration>,   // 连接超时
    pub read: Option<Duration>,      // 读取响应超时
}

impl Default for TimeoutConfig {
    fn default() -> Self {
        Self {
            total: Some(Duration::from_secs(30)),
            connect: None,
            read: None,
        }
    }
}

impl TimeoutConfig {
    /// 验证配置的有效性
    pub fn validate(&self) -> Result<()> {
        if let Some(total) = self.total {
            if total.as_secs() == 0 {
                return Err(anyhow::anyhow!("timeout cannot be 0"));
            }
        }
        Ok(())
    }

    /// 合并超时配置（用于请求级覆盖）
    #[allow(dead_code)]
    pub fn merge(&mut self, other: &TimeoutConfig) {
        if other.total.is_some() {
            self.total = other.total;
        }
        if other.connect.is_some() {
            self.connect = other.connect;
        }
        if other.read.is_some() {
            self.read = other.read;
        }
    }

    /// 应用到 wreq ClientBuilder
    pub fn apply(&self, builder: wreq::ClientBuilder) -> wreq::ClientBuilder {
        let mut builder = builder;
        if let Some(timeout) = self.total {
            builder = builder.timeout(timeout);
        }
        if let Some(timeout) = self.connect {
            builder = builder.connect_timeout(timeout);
        }
        if let Some(timeout) = self.read {
            builder = builder.read_timeout(timeout);
        }
        builder
    }
}
