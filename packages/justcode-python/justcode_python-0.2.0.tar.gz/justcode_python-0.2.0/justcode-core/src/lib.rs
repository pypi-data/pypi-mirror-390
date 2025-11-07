//! # Justcode
//!
//! A compact binary encoder/decoder with space-efficient encoding scheme.
//! The encoded size will be the same or smaller than the in-memory size.
//!
//! ## Features
//!
//! - Compact binary encoding (space-efficient)
//! - Varint encoding for lengths and small integers
//! - Architecture invariant (byte-order independent)
//! - Streaming Reader/Writer API
//! - Configurable encoding options
//!
//! ## Example
//!
//! ```rust
//! use justcode_core::{Encode, Decode, config};
//!
//! #[derive(Encode, Decode, PartialEq, Debug)]
//! struct Entity {
//!     x: f32,
//!     y: f32,
//! }
//!
//! #[derive(Encode, Decode, PartialEq, Debug)]
//! struct World(Vec<Entity>);
//!
//! fn main() {
//!     let config = config::standard();
//!     let world = World(vec![Entity { x: 0.0, y: 4.0 }, Entity { x: 10.0, y: 20.5 }]);
//!
//!     let encoded = justcode_core::encode_to_vec(&world, config).unwrap();
//!     let (decoded, len) = justcode_core::decode_from_slice(&encoded, config).unwrap();
//!
//!     assert_eq!(world, decoded);
//!     assert_eq!(len, encoded.len());
//! }
//! ```

#![cfg_attr(not(feature = "std"), no_std)]

#[cfg(not(feature = "std"))]
extern crate alloc;

#[cfg(not(feature = "std"))]
use alloc::vec::Vec;

pub mod config;
pub mod decode;
pub mod encode;
pub mod error;
pub mod reader;
pub mod varint;
pub mod writer;

pub use config::Config;
pub use decode::Decode;
pub use encode::Encode;
pub use error::{JustcodeError, Result};

// Re-export derive macros (when derive feature is enabled)
#[cfg(feature = "derive")]
pub use justcode_derive::{Decode, Encode};

/// Encode a value to a `Vec<u8>`.
///
/// # Example
///
/// ```rust
/// use justcode_core::{Encode, config};
///
/// let value = 42u32;
/// let config = config::standard();
/// let encoded = justcode_core::encode_to_vec(&value, config).unwrap();
/// ```
pub fn encode_to_vec<T: Encode>(value: &T, config: Config) -> Result<Vec<u8>> {
    let mut writer = writer::Writer::new(config);
    value.encode(&mut writer)?;
    Ok(writer.into_bytes())
}

/// Decode a value from a byte slice.
///
/// Returns the decoded value and the number of bytes consumed.
///
/// # Example
///
/// ```rust
/// use justcode_core::{Decode, config};
///
/// let data = [0x2A, 0x00, 0x00, 0x00];
/// let config = config::standard();
/// let (value, len): (u32, usize) = justcode_core::decode_from_slice(&data, config).unwrap();
/// assert_eq!(value, 42);
/// assert_eq!(len, 4);
/// ```
pub fn decode_from_slice<T: Decode>(bytes: &[u8], config: Config) -> Result<(T, usize)> {
    let mut reader = reader::Reader::new(bytes, config);
    let value = T::decode(&mut reader)?;
    let len = reader.bytes_read();
    Ok((value, len))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_encode_decode_u32() {
        let config = config::standard();
        let value = 42u32;
        let encoded = encode_to_vec(&value, config).unwrap();
        let (decoded, len): (u32, usize) = decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);
        assert_eq!(len, encoded.len());
    }

    #[test]
    fn test_encode_decode_vec() {
        let config = config::standard();
        let value = vec![1u32, 2, 3, 4];
        let encoded = encode_to_vec(&value, config).unwrap();
        let (decoded, len): (Vec<u32>, usize) = decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);
        assert_eq!(len, encoded.len());
    }
}

