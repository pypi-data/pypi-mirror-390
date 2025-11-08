use anyhow::Result;
use wreq::redirect::Policy;

/// HTTP 配置
#[derive(Clone, Debug)]
pub struct HttpConfig {
    pub https_only: bool,
    pub http_version: HttpVersion,
    pub follow_redirects: bool,
    pub max_redirects: usize,
    pub redirect_history: bool,
    pub referer: bool,
}

/// HTTP 版本偏好
#[derive(Clone, Debug, PartialEq)]
pub enum HttpVersion {
    Auto,
    Http1Only,
    Http2Only,
}

impl Default for HttpConfig {
    fn default() -> Self {
        Self {
            https_only: false,
            http_version: HttpVersion::Auto,
            follow_redirects: true,
            max_redirects: 20,
            redirect_history: false,
            referer: true,
        }
    }
}

impl HttpConfig {
    /// 验证配置的有效性
    pub fn validate(&self) -> Result<()> {
        if self.max_redirects == 0 && self.follow_redirects {
            return Err(anyhow::anyhow!(
                "max_redirects cannot be 0 when follow_redirects is true"
            ));
        }
        Ok(())
    }

    /// 应用到 wreq ClientBuilder
    pub fn apply(&self, builder: wreq::ClientBuilder) -> wreq::ClientBuilder {
        let mut builder = builder
            .https_only(self.https_only)
            .referer(self.referer)
            .history(self.redirect_history);

        builder = match self.http_version {
            HttpVersion::Http1Only => builder.http1_only(),
            HttpVersion::Http2Only => builder.http2_only(),
            HttpVersion::Auto => builder,
        };

        if self.follow_redirects {
            builder = builder.redirect(Policy::limited(self.max_redirects));
        } else {
            builder = builder.redirect(Policy::none());
        }

        builder
    }
}
