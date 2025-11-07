//! Writer for encoding values to bytes.

use crate::config::Config;
use crate::error::Result;

#[cfg(not(feature = "std"))]
use alloc::vec::Vec;

/// Writer for encoding values to a byte buffer.
pub struct Writer {
    buffer: Vec<u8>,
    config: Config,
}

impl Writer {
    /// Create a new writer with the given configuration.
    pub fn new(config: Config) -> Self {
        Self {
            buffer: Vec::new(),
            config,
        }
    }

    /// Write a single byte.
    pub fn write_u8(&mut self, value: u8) -> Result<()> {
        self.buffer.push(value);
        Ok(())
    }

    /// Write a u16 in little-endian format.
    pub fn write_u16(&mut self, value: u16) -> Result<()> {
        self.buffer.extend_from_slice(&value.to_le_bytes());
        Ok(())
    }

    /// Write a u32 in little-endian format.
    pub fn write_u32(&mut self, value: u32) -> Result<()> {
        self.buffer.extend_from_slice(&value.to_le_bytes());
        Ok(())
    }

    /// Write a u64 in little-endian format.
    pub fn write_u64(&mut self, value: u64) -> Result<()> {
        self.buffer.extend_from_slice(&value.to_le_bytes());
        Ok(())
    }

    /// Write an i8.
    pub fn write_i8(&mut self, value: i8) -> Result<()> {
        self.write_u8(value as u8)
    }

    /// Write an i16 in little-endian format.
    pub fn write_i16(&mut self, value: i16) -> Result<()> {
        self.write_u16(value as u16)
    }

    /// Write an i32 in little-endian format.
    pub fn write_i32(&mut self, value: i32) -> Result<()> {
        self.write_u32(value as u32)
    }

    /// Write an i64 in little-endian format.
    pub fn write_i64(&mut self, value: i64) -> Result<()> {
        self.write_u64(value as u64)
    }

    /// Write an f32 in little-endian format.
    pub fn write_f32(&mut self, value: f32) -> Result<()> {
        self.write_u32(value.to_bits())
    }

    /// Write an f64 in little-endian format.
    pub fn write_f64(&mut self, value: f64) -> Result<()> {
        self.write_u64(value.to_bits())
    }

    /// Write a boolean (encoded as u8: 0 = false, 1 = true).
    pub fn write_bool(&mut self, value: bool) -> Result<()> {
        self.write_u8(if value { 1 } else { 0 })
    }

    /// Write a byte slice.
    pub fn write_bytes(&mut self, bytes: &[u8]) -> Result<()> {
        self.buffer.extend_from_slice(bytes);
        Ok(())
    }

    /// Get the current configuration.
    pub fn config(&self) -> Config {
        self.config
    }

    /// Consume the writer and return the encoded bytes.
    pub fn into_bytes(self) -> Vec<u8> {
        self.buffer
    }

    /// Get a reference to the current buffer.
    pub fn as_bytes(&self) -> &[u8] {
        &self.buffer
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config;

    #[test]
    fn test_write_primitives() {
        let config = config::standard();
        let mut writer = Writer::new(config);

        writer.write_u8(42).unwrap();
        writer.write_u16(1000).unwrap();
        writer.write_u32(100000).unwrap();
        writer.write_u64(1000000000).unwrap();
        writer.write_bool(true).unwrap();
        writer.write_bool(false).unwrap();

        let bytes = writer.into_bytes();
        assert_eq!(bytes.len(), 1 + 2 + 4 + 8 + 1 + 1);
    }

    #[test]
    fn test_write_floats() {
        let config = config::standard();
        let mut writer = Writer::new(config);

        writer.write_f32(3.14).unwrap();
        writer.write_f64(2.718).unwrap();

        let bytes = writer.into_bytes();
        assert_eq!(bytes.len(), 4 + 8);
    }

    #[test]
    fn test_write_signed_integers() {
        let config = config::standard();
        let mut writer = Writer::new(config);

        writer.write_i8(-42).unwrap();
        writer.write_i16(-1000).unwrap();
        writer.write_i32(-100000).unwrap();
        writer.write_i64(-1000000000).unwrap();

        let bytes = writer.into_bytes();
        assert_eq!(bytes.len(), 1 + 2 + 4 + 8);
    }

    #[test]
    fn test_write_bytes() {
        let config = config::standard();
        let mut writer = Writer::new(config);
        writer.write_bytes(&[1, 2, 3, 4, 5]).unwrap();
        let bytes = writer.into_bytes();
        assert_eq!(bytes, &[1, 2, 3, 4, 5]);
    }

    #[test]
    fn test_as_bytes() {
        let config = config::standard();
        let mut writer = Writer::new(config);
        writer.write_u8(42).unwrap();
        let bytes_ref = writer.as_bytes();
        assert_eq!(bytes_ref, &[42]);
        // Should still be able to write after as_bytes
        writer.write_u8(43).unwrap();
        assert_eq!(writer.as_bytes(), &[42, 43]);
    }

    #[test]
    fn test_config() {
        let config = config::standard().with_limit(100);
        let writer = Writer::new(config);
        assert_eq!(writer.config().limit, Some(100));
    }

    #[test]
    fn test_write_special_floats() {
        let config = config::standard();
        let mut writer = Writer::new(config);
        
        writer.write_f32(f32::INFINITY).unwrap();
        writer.write_f32(f32::NEG_INFINITY).unwrap();
        writer.write_f32(f32::NAN).unwrap();
        writer.write_f64(f64::INFINITY).unwrap();
        writer.write_f64(f64::NEG_INFINITY).unwrap();
        writer.write_f64(f64::NAN).unwrap();
        
        let bytes = writer.into_bytes();
        assert_eq!(bytes.len(), 4 * 3 + 8 * 3);
    }
}

