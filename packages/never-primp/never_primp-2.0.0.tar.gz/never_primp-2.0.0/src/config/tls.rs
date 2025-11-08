use anyhow::Result;
use wreq::tls::{CertStore, Identity, KeyLog, TlsVersion};

/// TLS 配置
#[derive(Clone)]
pub struct TlsConfig {
    pub verify: bool,
    pub verify_hostname: bool,
    pub cert_store: Option<CertStore>,
    pub identity: Option<Identity>,
    pub ca_cert_file: Option<String>,
    pub min_version: Option<TlsVersion>,
    pub max_version: Option<TlsVersion>,
    pub keylog: Option<KeyLog>,
    pub tls_info: bool,
    pub tls_sni: bool,
}

impl Default for TlsConfig {
    fn default() -> Self {
        Self {
            verify: true,
            verify_hostname: true,
            cert_store: None,
            identity: None,
            ca_cert_file: None,
            min_version: None,
            max_version: None,
            keylog: None,
            tls_info: false,
            tls_sni: true,
        }
    }
}

impl TlsConfig {
    /// 验证配置的有效性
    pub fn validate(&self) -> Result<()> {
        // TlsVersion doesn't implement PartialOrd, so we can't validate the version range
        // wreq will handle any invalid configurations at runtime
        Ok(())
    }

    /// 应用到 wreq ClientBuilder
    pub fn apply(&self, builder: wreq::ClientBuilder) -> wreq::ClientBuilder {
        let mut builder = builder
            .cert_verification(self.verify)
            .verify_hostname(self.verify_hostname)
            .tls_sni(self.tls_sni)
            .tls_info(self.tls_info);

        if let Some(ref cert_store) = self.cert_store {
            builder = builder.cert_store(cert_store.clone());
        }
        if let Some(ref identity) = self.identity {
            builder = builder.identity(identity.clone());
        }
        if let Some(ref min_ver) = self.min_version {
            builder = builder.min_tls_version(*min_ver);
        }
        if let Some(ref max_ver) = self.max_version {
            builder = builder.max_tls_version(*max_ver);
        }
        if let Some(ref keylog) = self.keylog {
            builder = builder.keylog(keylog.clone());
        }

        builder
    }
}
