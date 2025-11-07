//! Configuration for encoding and decoding behavior.

/// Configuration options for justcode encoding/decoding.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Config {
    /// Maximum size limit for deserialization (prevents memory exhaustion attacks).
    /// If `None`, no limit is enforced.
    pub limit: Option<usize>,
    /// Use variable-length integer encoding for lengths and enum variants.
    /// When enabled, small values use fewer bytes.
    pub variable_int_encoding: bool,
}

impl Config {
    /// Create a new configuration with default settings.
    pub fn new() -> Self {
        Self {
            limit: None,
            variable_int_encoding: true,
        }
    }

    /// Set a maximum size limit for deserialization.
    ///
    /// This helps prevent memory exhaustion attacks by limiting
    /// the amount of memory that can be allocated during decoding.
    pub fn with_limit(mut self, limit: usize) -> Self {
        self.limit = Some(limit);
        self
    }

    /// Enable or disable variable-length integer encoding.
    ///
    /// When enabled, small integers and lengths are encoded using
    /// fewer bytes (varint encoding). This is enabled by default.
    pub fn with_variable_int_encoding(mut self, enabled: bool) -> Self {
        self.variable_int_encoding = enabled;
        self
    }
}

impl Default for Config {
    fn default() -> Self {
        Self::new()
    }
}

/// Standard configuration (same as default).
///
/// This is equivalent to `Config::new()` and provides:
/// - Variable-length integer encoding enabled
/// - No size limit (use `with_limit()` if needed for untrusted input)
pub fn standard() -> Config {
    Config::new()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_config_default() {
        let config = Config::default();
        assert_eq!(config.variable_int_encoding, true);
        assert_eq!(config.limit, None);
    }

    #[test]
    fn test_config_with_limit() {
        let config = Config::new().with_limit(1024);
        assert_eq!(config.limit, Some(1024));
    }

    #[test]
    fn test_config_with_variable_int_encoding() {
        let config = Config::new().with_variable_int_encoding(false);
        assert_eq!(config.variable_int_encoding, false);
    }

    #[test]
    fn test_standard_config() {
        let config = standard();
        assert_eq!(config.variable_int_encoding, true);
        assert_eq!(config.limit, None);
    }

    #[test]
    fn test_config_chaining() {
        let config = Config::new()
            .with_limit(1024)
            .with_variable_int_encoding(false);
        assert_eq!(config.limit, Some(1024));
        assert_eq!(config.variable_int_encoding, false);
    }
}

