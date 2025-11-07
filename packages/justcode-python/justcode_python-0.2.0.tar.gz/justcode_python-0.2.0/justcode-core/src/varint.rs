//! Variable-length integer encoding (varint).

use crate::error::{JustcodeError, Result};
use crate::reader::Reader;
use crate::writer::Writer;

/// Encode a u64 as a varint.
///
/// Varints use a variable number of bytes:
/// - Values 0-127: 1 byte
/// - Values 128-16383: 2 bytes
/// - Values 16384-2097151: 3 bytes
/// - etc.
///
/// The encoding uses the high bit as a continuation bit.
pub fn encode_varint(writer: &mut Writer, mut value: u64) -> Result<()> {
    loop {
        let byte = (value & 0x7F) as u8;
        value >>= 7;
        if value == 0 {
            writer.write_u8(byte)?;
            break;
        } else {
            writer.write_u8(byte | 0x80)?;
        }
    }
    Ok(())
}

/// Decode a u64 from a varint.
pub fn decode_varint(reader: &mut Reader) -> Result<u64> {
    let mut result = 0u64;
    let mut shift = 0;

    loop {
        let byte = reader.read_u8()?;
        result |= ((byte & 0x7F) as u64) << shift;

        if (byte & 0x80) == 0 {
            break;
        }

        shift += 7;
        if shift >= 64 {
            return Err(JustcodeError::InvalidVarint);
        }
    }

    Ok(result)
}

/// Encode a usize as a varint (for lengths).
pub fn encode_length(writer: &mut Writer, value: usize, config: crate::Config) -> Result<()> {
    if config.variable_int_encoding {
        encode_varint(writer, value as u64)
    } else {
        // Use fixed-size u64 encoding
        writer.write_u64(value as u64)
    }
}

/// Decode a usize from a varint (for lengths).
pub fn decode_length(reader: &mut Reader, config: crate::Config) -> Result<usize> {
    if config.variable_int_encoding {
        let value = decode_varint(reader)?;
        Ok(value as usize)
    } else {
        // Use fixed-size u64 decoding
        let value = reader.read_u64()?;
        Ok(value as usize)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config;

    #[test]
    fn test_varint_encode_decode() {
        let config = config::standard();
        let test_cases = vec![
            0u64,
            1,
            127,
            128,
            255,
            256,
            16383,
            16384,
            65535,
            1000000,
            u64::MAX,
        ];

        for value in test_cases {
            let mut writer = Writer::new(config);
            encode_varint(&mut writer, value).unwrap();
            let bytes = writer.into_bytes();

            let mut reader = Reader::new(&bytes, config);
            let decoded = decode_varint(&mut reader).unwrap();
            assert_eq!(value, decoded);
        }
    }

    #[test]
    fn test_length_encode_decode() {
        let config = config::standard();
        let test_cases = vec![0usize, 1, 127, 128, 255, 1000, 1000000];

        for value in test_cases {
            let mut writer = Writer::new(config);
            encode_length(&mut writer, value, config).unwrap();
            let bytes = writer.into_bytes();

            let mut reader = Reader::new(&bytes, config);
            let decoded = decode_length(&mut reader, config).unwrap();
            assert_eq!(value, decoded);
        }
    }

    #[test]
    fn test_varint_small_values() {
        let config = config::standard();
        let value = 42u64;
        let mut writer = Writer::new(config);
        encode_varint(&mut writer, value).unwrap();
        let bytes = writer.into_bytes();
        // Small values should use 1 byte
        assert_eq!(bytes.len(), 1);
    }

    #[test]
    fn test_varint_multi_byte() {
        let config = config::standard();
        // Test 2-byte varint
        let value = 200u64;
        let mut writer = Writer::new(config);
        encode_varint(&mut writer, value).unwrap();
        let bytes = writer.into_bytes();
        assert_eq!(bytes.len(), 2);
        
        let mut reader = Reader::new(&bytes, config);
        let decoded = decode_varint(&mut reader).unwrap();
        assert_eq!(value, decoded);
    }

    #[test]
    fn test_varint_large_values() {
        let config = config::standard();
        // Test large varint values
        let test_cases = vec![
            (16384u64, 3),  // 3 bytes
            (2097151u64, 3), // 3 bytes
            (268435455u64, 4), // 4 bytes
        ];

        for (value, expected_bytes) in test_cases {
            let mut writer = Writer::new(config);
            encode_varint(&mut writer, value).unwrap();
            let bytes = writer.into_bytes();
            assert_eq!(bytes.len(), expected_bytes, "Value {} should use {} bytes", value, expected_bytes);
            
            let mut reader = Reader::new(&bytes, config);
            let decoded = decode_varint(&mut reader).unwrap();
            assert_eq!(value, decoded);
        }
    }

    #[test]
    fn test_invalid_varint() {
        let config = config::standard();
        // Create an invalid varint with too many continuation bytes
        let invalid_data = vec![0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80]; // 11 bytes, exceeds 64-bit limit
        let mut reader = Reader::new(&invalid_data, config);
        assert!(decode_varint(&mut reader).is_err());
    }

    #[test]
    fn test_length_fixed_encoding() {
        let config = config::standard().with_variable_int_encoding(false);
        let value = 42usize;
        let mut writer = Writer::new(config);
        encode_length(&mut writer, value, config).unwrap();
        let bytes = writer.into_bytes();
        // Should use fixed 8 bytes
        assert_eq!(bytes.len(), 8);
        
        let mut reader = Reader::new(&bytes, config);
        let decoded = decode_length(&mut reader, config).unwrap();
        assert_eq!(value, decoded);
    }

    #[test]
    fn test_length_varint_encoding() {
        let config = config::standard().with_variable_int_encoding(true);
        let value = 42usize;
        let mut writer = Writer::new(config);
        encode_length(&mut writer, value, config).unwrap();
        let bytes = writer.into_bytes();
        // Should use 1 byte varint
        assert_eq!(bytes.len(), 1);
        
        let mut reader = Reader::new(&bytes, config);
        let decoded = decode_length(&mut reader, config).unwrap();
        assert_eq!(value, decoded);
    }

    #[test]
    fn test_length_large_value() {
        let config = config::standard();
        let value = 1000000usize;
        let mut writer = Writer::new(config);
        encode_length(&mut writer, value, config).unwrap();
        let bytes = writer.into_bytes();
        
        let mut reader = Reader::new(&bytes, config);
        let decoded = decode_length(&mut reader, config).unwrap();
        assert_eq!(value, decoded);
    }
}

