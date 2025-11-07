//! Error types for justcode encoding/decoding.

use thiserror::Error;

#[cfg(feature = "std")]
use std::string::String;

#[cfg(not(feature = "std"))]
extern crate alloc;
#[cfg(not(feature = "std"))]
use alloc::string::String;

/// Result type for justcode operations.
pub type Result<T> = core::result::Result<T, JustcodeError>;

/// Errors that can occur during encoding or decoding.
#[derive(Error, Debug, Clone, PartialEq, Eq)]
pub enum JustcodeError {
    /// Not enough bytes to decode the value.
    #[error("unexpected end of input: expected {expected} bytes, got {got}")]
    UnexpectedEndOfInput { expected: usize, got: usize },

    /// Size limit exceeded during decoding.
    #[error("size limit exceeded: limit is {limit}, but {requested} bytes were requested")]
    SizeLimitExceeded { limit: usize, requested: usize },

    /// Invalid varint encoding.
    #[error("invalid varint encoding")]
    InvalidVarint,

    /// Custom error message.
    #[error("{0}")]
    Custom(String),
}

impl JustcodeError {
    /// Create a custom error with a message.
    pub fn custom(msg: impl Into<String>) -> Self {
        Self::Custom(msg.into())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_error_display() {
        let err = JustcodeError::UnexpectedEndOfInput {
            expected: 10,
            got: 5,
        };
        assert!(err.to_string().contains("unexpected end of input"));
    }

    #[test]
    fn test_custom_error() {
        let err = JustcodeError::custom("test error");
        assert_eq!(err.to_string(), "test error");
    }
}

