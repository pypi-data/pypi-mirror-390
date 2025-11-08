use anyhow::Result;
use std::time::Duration;

/// 连接池配置
#[derive(Clone, Debug)]
pub struct PoolConfig {
    pub idle_timeout: Option<Duration>,
    pub max_idle_per_host: usize,
    pub max_size: Option<u32>,
}

impl Default for PoolConfig {
    fn default() -> Self {
        Self {
            idle_timeout: Some(Duration::from_secs(90)),
            max_idle_per_host: usize::MAX,
            max_size: None,
        }
    }
}

impl PoolConfig {
    /// 验证配置的有效性
    pub fn validate(&self) -> Result<()> {
        if let Some(max) = self.max_size {
            if max == 0 {
                return Err(anyhow::anyhow!("pool_max_size cannot be 0"));
            }
        }
        Ok(())
    }

    /// 应用到 wreq ClientBuilder
    pub fn apply(&self, builder: wreq::ClientBuilder) -> wreq::ClientBuilder {
        let mut builder = builder.pool_max_idle_per_host(self.max_idle_per_host);

        if let Some(timeout) = self.idle_timeout {
            builder = builder.pool_idle_timeout(timeout);
        }
        if let Some(max) = self.max_size {
            builder = builder.pool_max_size(max);
        }

        builder
    }
}
