//! Reader for decoding values from bytes.

use crate::config::Config;
use crate::error::{JustcodeError, Result};

/// Reader for decoding values from a byte slice.
pub struct Reader<'a> {
    data: &'a [u8],
    position: usize,
    config: Config,
}

impl<'a> Reader<'a> {
    /// Create a new reader with the given byte slice and configuration.
    pub fn new(data: &'a [u8], config: Config) -> Self {
        Self {
            data,
            position: 0,
            config,
        }
    }

    /// Read a single byte.
    pub fn read_u8(&mut self) -> Result<u8> {
        self.check_size(1)?;
        let value = self.data[self.position];
        self.position += 1;
        Ok(value)
    }

    /// Read a u16 in little-endian format.
    pub fn read_u16(&mut self) -> Result<u16> {
        self.check_size(2)?;
        let bytes = &self.data[self.position..self.position + 2];
        self.position += 2;
        Ok(u16::from_le_bytes([bytes[0], bytes[1]]))
    }

    /// Read a u32 in little-endian format.
    pub fn read_u32(&mut self) -> Result<u32> {
        self.check_size(4)?;
        let bytes = &self.data[self.position..self.position + 4];
        self.position += 4;
        Ok(u32::from_le_bytes([bytes[0], bytes[1], bytes[2], bytes[3]]))
    }

    /// Read a u64 in little-endian format.
    pub fn read_u64(&mut self) -> Result<u64> {
        self.check_size(8)?;
        let bytes = &self.data[self.position..self.position + 8];
        self.position += 8;
        Ok(u64::from_le_bytes([
            bytes[0], bytes[1], bytes[2], bytes[3], bytes[4], bytes[5], bytes[6], bytes[7],
        ]))
    }

    /// Read an i8.
    pub fn read_i8(&mut self) -> Result<i8> {
        Ok(self.read_u8()? as i8)
    }

    /// Read an i16 in little-endian format.
    pub fn read_i16(&mut self) -> Result<i16> {
        Ok(self.read_u16()? as i16)
    }

    /// Read an i32 in little-endian format.
    pub fn read_i32(&mut self) -> Result<i32> {
        Ok(self.read_u32()? as i32)
    }

    /// Read an i64 in little-endian format.
    pub fn read_i64(&mut self) -> Result<i64> {
        Ok(self.read_u64()? as i64)
    }

    /// Read an f32 in little-endian format.
    pub fn read_f32(&mut self) -> Result<f32> {
        let bits = self.read_u32()?;
        Ok(f32::from_bits(bits))
    }

    /// Read an f64 in little-endian format.
    pub fn read_f64(&mut self) -> Result<f64> {
        let bits = self.read_u64()?;
        Ok(f64::from_bits(bits))
    }

    /// Read a boolean (decoded from u8: 0 = false, 1 = true).
    pub fn read_bool(&mut self) -> Result<bool> {
        let value = self.read_u8()?;
        Ok(value != 0)
    }

    /// Read a byte slice of the given length.
    pub fn read_bytes(&mut self, len: usize) -> Result<&'a [u8]> {
        self.check_size(len)?;
        let bytes = &self.data[self.position..self.position + len];
        self.position += len;
        Ok(bytes)
    }

    /// Get the current configuration.
    pub fn config(&self) -> Config {
        self.config
    }

    /// Get the number of bytes read so far.
    pub fn bytes_read(&self) -> usize {
        self.position
    }

    /// Get the remaining bytes.
    pub fn remaining(&self) -> &'a [u8] {
        &self.data[self.position..]
    }

    /// Check if we have enough bytes remaining.
    fn check_size(&self, needed: usize) -> Result<()> {
        let available = self.data.len().saturating_sub(self.position);
        if available < needed {
            return Err(JustcodeError::UnexpectedEndOfInput {
                expected: needed,
                got: available,
            });
        }

        // Check size limit if configured
        if let Some(limit) = self.config.limit {
            let new_size = self.position + needed;
            if new_size > limit {
                return Err(JustcodeError::SizeLimitExceeded {
                    limit,
                    requested: new_size,
                });
            }
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config;

    #[test]
    fn test_read_primitives() {
        let config = config::standard();
        let data = vec![
            42u8,                    // u8
            0xE8, 0x03,              // u16: 1000
            0xA0, 0x86, 0x01, 0x00,  // u32: 100000
            0x00, 0xCA, 0x9A, 0x3B, 0x00, 0x00, 0x00, 0x00, // u64: 1000000000
            1,                       // bool: true
            0,                       // bool: false
        ];

        let mut reader = Reader::new(&data, config);
        assert_eq!(reader.read_u8().unwrap(), 42);
        assert_eq!(reader.read_u16().unwrap(), 1000);
        assert_eq!(reader.read_u32().unwrap(), 100000);
        assert_eq!(reader.read_u64().unwrap(), 1000000000);
        assert_eq!(reader.read_bool().unwrap(), true);
        assert_eq!(reader.read_bool().unwrap(), false);
    }

    #[test]
    fn test_read_floats() {
        let config = config::standard();
        let mut writer = crate::writer::Writer::new(config);
        writer.write_f32(3.14).unwrap();
        writer.write_f64(2.718).unwrap();
        let data = writer.into_bytes();

        let mut reader = Reader::new(&data, config);
        assert!((reader.read_f32().unwrap() - 3.14).abs() < 0.01);
        assert!((reader.read_f64().unwrap() - 2.718).abs() < 0.001);
    }

    #[test]
    fn test_unexpected_end_of_input() {
        let config = config::standard();
        let data = vec![42u8];
        let mut reader = Reader::new(&data, config);
        assert!(reader.read_u32().is_err());
    }

    #[test]
    fn test_size_limit() {
        let config = config::standard().with_limit(10);
        let data = vec![0u8; 20];
        let mut reader = Reader::new(&data, config);
        assert!(reader.read_bytes(15).is_err());
    }

    #[test]
    fn test_read_signed_integers() {
        let config = config::standard();
        let mut writer = crate::writer::Writer::new(config);
        writer.write_i8(-42).unwrap();
        writer.write_i16(-1000).unwrap();
        writer.write_i32(-100000).unwrap();
        writer.write_i64(-1000000000).unwrap();
        let data = writer.into_bytes();

        let mut reader = Reader::new(&data, config);
        assert_eq!(reader.read_i8().unwrap(), -42);
        assert_eq!(reader.read_i16().unwrap(), -1000);
        assert_eq!(reader.read_i32().unwrap(), -100000);
        assert_eq!(reader.read_i64().unwrap(), -1000000000);
    }

    #[test]
    fn test_read_bytes() {
        let config = config::standard();
        let data = vec![1, 2, 3, 4, 5, 6, 7, 8];
        let mut reader = Reader::new(&data, config);
        let bytes = reader.read_bytes(4).unwrap();
        assert_eq!(bytes, &[1, 2, 3, 4]);
        assert_eq!(reader.bytes_read(), 4);
    }

    #[test]
    fn test_remaining() {
        let config = config::standard();
        let data = vec![1, 2, 3, 4, 5];
        let mut reader = Reader::new(&data, config);
        reader.read_u8().unwrap();
        assert_eq!(reader.remaining(), &[2, 3, 4, 5]);
    }

    #[test]
    fn test_config() {
        let config = config::standard().with_limit(100);
        let data = vec![1, 2, 3];
        let reader = Reader::new(&data, config);
        assert_eq!(reader.config().limit, Some(100));
    }

    #[test]
    fn test_bytes_read() {
        let config = config::standard();
        let data = vec![1, 2, 3, 4, 5];
        let mut reader = Reader::new(&data, config);
        assert_eq!(reader.bytes_read(), 0);
        reader.read_u8().unwrap();
        assert_eq!(reader.bytes_read(), 1);
        reader.read_u16().unwrap();
        assert_eq!(reader.bytes_read(), 3);
    }

    #[test]
    fn test_size_limit_edge_cases() {
        let config = config::standard().with_limit(5);
        let data = vec![0u8; 10];
        let mut reader = Reader::new(&data, config);
        
        // Should succeed reading 5 bytes
        reader.read_bytes(5).unwrap();
        
        // Should fail reading beyond limit
        assert!(reader.read_bytes(1).is_err());
    }

    #[test]
    fn test_read_bool_edge_cases() {
        let config = config::standard();
        let data = vec![0, 1, 2, 255];
        let mut reader = Reader::new(&data, config);
        assert_eq!(reader.read_bool().unwrap(), false);
        assert_eq!(reader.read_bool().unwrap(), true);
        assert_eq!(reader.read_bool().unwrap(), true); // 2 != 0
        assert_eq!(reader.read_bool().unwrap(), true); // 255 != 0
    }

    #[test]
    fn test_check_size_error_message() {
        let config = config::standard();
        let data = vec![1u8, 2];
        let mut reader = Reader::new(&data, config);
        let err = reader.read_u32().unwrap_err();
        match err {
            JustcodeError::UnexpectedEndOfInput { expected, got } => {
                assert_eq!(expected, 4);
                assert_eq!(got, 2);
            }
            _ => panic!("Expected UnexpectedEndOfInput error"),
        }
    }

    #[test]
    fn test_size_limit_exceeded_error() {
        let config = config::standard().with_limit(5);
        let data = vec![0u8; 10];
        let mut reader = Reader::new(&data, config);
        // Read 5 bytes successfully
        reader.read_bytes(5).unwrap();
        // Try to read 1 more byte, should exceed limit
        let err = reader.read_bytes(1).unwrap_err();
        match err {
            JustcodeError::SizeLimitExceeded { limit, requested } => {
                assert_eq!(limit, 5);
                assert_eq!(requested, 6);
            }
            _ => panic!("Expected SizeLimitExceeded error"),
        }
    }

    #[test]
    fn test_size_limit_at_boundary() {
        let config = config::standard().with_limit(5);
        let data = vec![0u8; 10];
        let mut reader = Reader::new(&data, config);
        // Should succeed reading exactly at limit
        reader.read_bytes(5).unwrap();
        // Next read should fail
        assert!(reader.read_bytes(1).is_err());
    }

    #[test]
    fn test_check_size_with_limit_none() {
        let config = config::standard(); // No limit
        let data = vec![1u8, 2, 3, 4, 5];
        let mut reader = Reader::new(&data, config);
        // Should succeed reading all bytes when no limit
        reader.read_bytes(5).unwrap();
    }

    #[test]
    fn test_check_size_with_limit_success() {
        let config = config::standard().with_limit(10);
        let data = vec![0u8; 20];
        let mut reader = Reader::new(&data, config);
        // Should succeed reading within limit
        reader.read_bytes(5).unwrap();
        assert_eq!(reader.bytes_read(), 5);
    }

    #[test]
    fn test_check_size_exact_error_paths() {
        let config = config::standard();
        // Test UnexpectedEndOfInput error path (lines 123-124)
        let data = vec![1u8];
        let mut reader = Reader::new(&data, config);
        let err = reader.read_u16().unwrap_err();
        if let JustcodeError::UnexpectedEndOfInput { expected, got } = err {
            assert_eq!(expected, 2);
            assert_eq!(got, 1);
        } else {
            panic!("Expected UnexpectedEndOfInput");
        }

        // Test SizeLimitExceeded error path (lines 133-134)
        let config = config::standard().with_limit(3);
        let data = vec![0u8; 10];
        let mut reader = Reader::new(&data, config);
        reader.read_bytes(2).unwrap(); // Read 2 bytes, position now at 2
        let err = reader.read_bytes(2).unwrap_err(); // Try to read 2 more, would exceed limit of 3
        if let JustcodeError::SizeLimitExceeded { limit, requested } = err {
            assert_eq!(limit, 3);
            assert_eq!(requested, 4);
        } else {
            panic!("Expected SizeLimitExceeded");
        }
    }
}

