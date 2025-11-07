//! Encoding trait and implementations.

use crate::reader::Reader;
use crate::varint::{decode_length, encode_length};
use crate::writer::Writer;
use crate::Result;

/// Trait for types that can be encoded to binary format.
pub trait Encode {
    /// Encode this value into the writer.
    fn encode(&self, writer: &mut Writer) -> Result<()>;
}

/// Trait for types that can be decoded from binary format.
pub trait Decode: Sized {
    /// Decode a value from the reader.
    fn decode(reader: &mut Reader) -> Result<Self>;
}

// Implementations for primitive types

impl Encode for u8 {
    fn encode(&self, writer: &mut Writer) -> Result<()> {
        writer.write_u8(*self)
    }
}

impl Decode for u8 {
    fn decode(reader: &mut Reader) -> Result<Self> {
        reader.read_u8()
    }
}

impl Encode for u16 {
    fn encode(&self, writer: &mut Writer) -> Result<()> {
        writer.write_u16(*self)
    }
}

impl Decode for u16 {
    fn decode(reader: &mut Reader) -> Result<Self> {
        reader.read_u16()
    }
}

impl Encode for u32 {
    fn encode(&self, writer: &mut Writer) -> Result<()> {
        writer.write_u32(*self)
    }
}

impl Decode for u32 {
    fn decode(reader: &mut Reader) -> Result<Self> {
        reader.read_u32()
    }
}

impl Encode for u64 {
    fn encode(&self, writer: &mut Writer) -> Result<()> {
        writer.write_u64(*self)
    }
}

impl Decode for u64 {
    fn decode(reader: &mut Reader) -> Result<Self> {
        reader.read_u64()
    }
}

impl Encode for usize {
    fn encode(&self, writer: &mut Writer) -> Result<()> {
        writer.write_u64(*self as u64)
    }
}

impl Decode for usize {
    fn decode(reader: &mut Reader) -> Result<Self> {
        Ok(reader.read_u64()? as usize)
    }
}

impl Encode for i8 {
    fn encode(&self, writer: &mut Writer) -> Result<()> {
        writer.write_i8(*self)
    }
}

impl Decode for i8 {
    fn decode(reader: &mut Reader) -> Result<Self> {
        reader.read_i8()
    }
}

impl Encode for i16 {
    fn encode(&self, writer: &mut Writer) -> Result<()> {
        writer.write_i16(*self)
    }
}

impl Decode for i16 {
    fn decode(reader: &mut Reader) -> Result<Self> {
        reader.read_i16()
    }
}

impl Encode for i32 {
    fn encode(&self, writer: &mut Writer) -> Result<()> {
        writer.write_i32(*self)
    }
}

impl Decode for i32 {
    fn decode(reader: &mut Reader) -> Result<Self> {
        reader.read_i32()
    }
}

impl Encode for i64 {
    fn encode(&self, writer: &mut Writer) -> Result<()> {
        writer.write_i64(*self)
    }
}

impl Decode for i64 {
    fn decode(reader: &mut Reader) -> Result<Self> {
        reader.read_i64()
    }
}

impl Encode for f32 {
    fn encode(&self, writer: &mut Writer) -> Result<()> {
        writer.write_f32(*self)
    }
}

impl Decode for f32 {
    fn decode(reader: &mut Reader) -> Result<Self> {
        reader.read_f32()
    }
}

impl Encode for f64 {
    fn encode(&self, writer: &mut Writer) -> Result<()> {
        writer.write_f64(*self)
    }
}

impl Decode for f64 {
    fn decode(reader: &mut Reader) -> Result<Self> {
        reader.read_f64()
    }
}

impl Encode for bool {
    fn encode(&self, writer: &mut Writer) -> Result<()> {
        writer.write_bool(*self)
    }
}

impl Decode for bool {
    fn decode(reader: &mut Reader) -> Result<Self> {
        reader.read_bool()
    }
}

impl Encode for char {
    fn encode(&self, writer: &mut Writer) -> Result<()> {
        (*self as u32).encode(writer)
    }
}

impl Decode for char {
    fn decode(reader: &mut Reader) -> Result<Self> {
        let code = u32::decode(reader)?;
        char::from_u32(code).ok_or_else(|| crate::error::JustcodeError::custom("invalid char"))
    }
}

// Implementations for collections

#[cfg(feature = "std")]
impl<T: Encode> Encode for Vec<T> {
    fn encode(&self, writer: &mut Writer) -> Result<()> {
        let config = writer.config();
        encode_length(writer, self.len(), config)?;
        for item in self {
            item.encode(writer)?;
        }
        Ok(())
    }
}

#[cfg(feature = "std")]
impl<T: Decode> Decode for Vec<T> {
    fn decode(reader: &mut Reader) -> Result<Self> {
        let config = reader.config();
        let len = decode_length(reader, config)?;
        let mut vec = Vec::with_capacity(len.min(1024)); // Cap initial capacity
        for _ in 0..len {
            vec.push(T::decode(reader)?);
        }
        Ok(vec)
    }
}

#[cfg(not(feature = "std"))]
use alloc::vec::Vec;

#[cfg(not(feature = "std"))]
impl<T: Encode> Encode for Vec<T> {
    fn encode(&self, writer: &mut Writer) -> Result<()> {
        let config = writer.config();
        encode_length(writer, self.len(), config)?;
        for item in self {
            item.encode(writer)?;
        }
        Ok(())
    }
}

#[cfg(not(feature = "std"))]
impl<T: Decode> Decode for Vec<T> {
    fn decode(reader: &mut Reader) -> Result<Self> {
        let config = reader.config();
        let len = decode_length(reader, config)?;
        let mut vec = Vec::new();
        for _ in 0..len {
            vec.push(T::decode(reader)?);
        }
        Ok(vec)
    }
}

impl<T: Encode> Encode for Option<T> {
    fn encode(&self, writer: &mut Writer) -> Result<()> {
        match self {
            Some(value) => {
                writer.write_bool(true)?;
                value.encode(writer)?;
            }
            None => {
                writer.write_bool(false)?;
            }
        }
        Ok(())
    }
}

impl<T: Decode> Decode for Option<T> {
    fn decode(reader: &mut Reader) -> Result<Self> {
        if reader.read_bool()? {
            Ok(Some(T::decode(reader)?))
        } else {
            Ok(None)
        }
    }
}

#[cfg(feature = "std")]
impl Encode for String {
    fn encode(&self, writer: &mut Writer) -> Result<()> {
        self.as_bytes().to_vec().encode(writer)
    }
}

#[cfg(not(feature = "std"))]
impl Encode for alloc::string::String {
    fn encode(&self, writer: &mut Writer) -> Result<()> {
        self.as_bytes().to_vec().encode(writer)
    }
}

#[cfg(feature = "std")]
impl Decode for String {
    fn decode(reader: &mut Reader) -> Result<Self> {
        let bytes = Vec::<u8>::decode(reader)?;
        String::from_utf8(bytes)
            .map_err(|e| crate::error::JustcodeError::custom(format!("invalid UTF-8: {}", e)))
    }
}

#[cfg(not(feature = "std"))]
impl Decode for alloc::string::String {
    fn decode(reader: &mut Reader) -> Result<Self> {
        extern crate alloc;
        use alloc::format;
        let bytes = Vec::<u8>::decode(reader)?;
        alloc::string::String::from_utf8(bytes)
            .map_err(|e| crate::error::JustcodeError::custom(format!("invalid UTF-8: {}", e)))
    }
}

#[cfg(feature = "std")]
impl Encode for &str {
    fn encode(&self, writer: &mut Writer) -> Result<()> {
        self.as_bytes().to_vec().encode(writer)
    }
}

// Implement Encode for &[u8] by converting to Vec
impl Encode for &[u8] {
    fn encode(&self, writer: &mut Writer) -> Result<()> {
        self.to_vec().encode(writer)
    }
}

// Tuple implementations

impl<T1: Encode> Encode for (T1,) {
    fn encode(&self, writer: &mut Writer) -> Result<()> {
        self.0.encode(writer)
    }
}

impl<T1: Decode> Decode for (T1,) {
    fn decode(reader: &mut Reader) -> Result<Self> {
        Ok((T1::decode(reader)?,))
    }
}

impl<T1: Encode, T2: Encode> Encode for (T1, T2) {
    fn encode(&self, writer: &mut Writer) -> Result<()> {
        self.0.encode(writer)?;
        self.1.encode(writer)
    }
}

impl<T1: Decode, T2: Decode> Decode for (T1, T2) {
    fn decode(reader: &mut Reader) -> Result<Self> {
        Ok((T1::decode(reader)?, T2::decode(reader)?))
    }
}

impl<T1: Encode, T2: Encode, T3: Encode> Encode for (T1, T2, T3) {
    fn encode(&self, writer: &mut Writer) -> Result<()> {
        self.0.encode(writer)?;
        self.1.encode(writer)?;
        self.2.encode(writer)
    }
}

impl<T1: Decode, T2: Decode, T3: Decode> Decode for (T1, T2, T3) {
    fn decode(reader: &mut Reader) -> Result<Self> {
        Ok((
            T1::decode(reader)?,
            T2::decode(reader)?,
            T3::decode(reader)?,
        ))
    }
}

impl<T1: Encode, T2: Encode, T3: Encode, T4: Encode> Encode for (T1, T2, T3, T4) {
    fn encode(&self, writer: &mut Writer) -> Result<()> {
        self.0.encode(writer)?;
        self.1.encode(writer)?;
        self.2.encode(writer)?;
        self.3.encode(writer)
    }
}

impl<T1: Decode, T2: Decode, T3: Decode, T4: Decode> Decode for (T1, T2, T3, T4) {
    fn decode(reader: &mut Reader) -> Result<Self> {
        Ok((
            T1::decode(reader)?,
            T2::decode(reader)?,
            T3::decode(reader)?,
            T4::decode(reader)?,
        ))
    }
}

// Array implementations (up to 32 elements)

macro_rules! impl_array {
    ($n:expr) => {
        impl<T: Encode> Encode for [T; $n] {
            fn encode(&self, writer: &mut Writer) -> Result<()> {
                for item in self {
                    item.encode(writer)?;
                }
                Ok(())
            }
        }

        impl<T: Decode + Copy + Default> Decode for [T; $n] {
            fn decode(reader: &mut Reader) -> Result<Self> {
                let mut arr = [T::default(); $n];
                for item in &mut arr {
                    *item = T::decode(reader)?;
                }
                Ok(arr)
            }
        }
    };
}

impl_array!(0);
impl_array!(1);
impl_array!(2);
impl_array!(3);
impl_array!(4);
impl_array!(5);
impl_array!(6);
impl_array!(7);
impl_array!(8);
impl_array!(9);
impl_array!(10);
impl_array!(11);
impl_array!(12);
impl_array!(13);
impl_array!(14);
impl_array!(15);
impl_array!(16);
impl_array!(17);
impl_array!(18);
impl_array!(19);
impl_array!(20);
impl_array!(21);
impl_array!(22);
impl_array!(23);
impl_array!(24);
impl_array!(25);
impl_array!(26);
impl_array!(27);
impl_array!(28);
impl_array!(29);
impl_array!(30);
impl_array!(31);
impl_array!(32);

// Enum encoding support
// Enums are encoded as: variant_index (u32 or varint) + variant data
// The variant index is encoded based on config.variable_int_encoding

impl Encode for () {
    fn encode(&self, _writer: &mut Writer) -> Result<()> {
        Ok(())
    }
}

impl Decode for () {
    fn decode(_reader: &mut Reader) -> Result<Self> {
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config;

    #[test]
    fn test_encode_decode_all_primitives() {
        let config = config::standard();
        
        // Test u8
        let value = 42u8;
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): (u8, usize) = crate::decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);

        // Test u16
        let value = 1000u16;
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): (u16, usize) = crate::decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);

        // Test u32
        let value = 100000u32;
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): (u32, usize) = crate::decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);

        // Test u64
        let value = 1000000000u64;
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): (u64, usize) = crate::decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);

        // Test usize
        let value = 42usize;
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): (usize, usize) = crate::decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);

        // Test i8
        let value = -42i8;
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): (i8, usize) = crate::decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);

        // Test i16
        let value = -1000i16;
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): (i16, usize) = crate::decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);

        // Test i32
        let value = -100000i32;
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): (i32, usize) = crate::decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);

        // Test i64
        let value = -1000000000i64;
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): (i64, usize) = crate::decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);

        // Test f32
        let value = 3.14f32;
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): (f32, usize) = crate::decode_from_slice(&encoded, config).unwrap();
        assert!((value - decoded).abs() < 0.001);

        // Test f64
        let value = 2.718f64;
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): (f64, usize) = crate::decode_from_slice(&encoded, config).unwrap();
        assert!((value - decoded).abs() < 0.0001);

        // Test bool
        let value = true;
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): (bool, usize) = crate::decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);

        let value = false;
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): (bool, usize) = crate::decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);

        // Test char
        let value = 'A';
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): (char, usize) = crate::decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);

        let value = '🦊';
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): (char, usize) = crate::decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);
    }

    #[test]
    fn test_encode_decode_primitives() {
        let config = config::standard();
        let test_cases: Vec<Box<dyn Fn(&mut Writer) -> Result<()>>> = vec![
            Box::new(|w| 42u8.encode(w)),
            Box::new(|w| 1000u16.encode(w)),
            Box::new(|w| 100000u32.encode(w)),
            Box::new(|w| 1000000000u64.encode(w)),
            Box::new(|w| true.encode(w)),
            Box::new(|w| 3.14f32.encode(w)),
        ];

        for encode_fn in test_cases {
            let mut writer = Writer::new(config);
            encode_fn(&mut writer).unwrap();
            let bytes = writer.into_bytes();
            assert!(!bytes.is_empty());
        }
    }

    #[test]
    fn test_encode_decode_vec() {
        let config = config::standard();
        let value = vec![1u32, 2, 3, 4, 5];
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): (Vec<u32>, usize) = crate::decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);
    }

    #[test]
    fn test_encode_decode_empty_vec() {
        let config = config::standard();
        let value: Vec<u32> = vec![];
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): (Vec<u32>, usize) = crate::decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);
    }

    #[test]
    fn test_encode_decode_large_vec() {
        let config = config::standard();
        let value: Vec<u8> = (0u8..255).chain(0u8..255).chain(0u8..255).chain(0u8..235).collect();
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): (Vec<u8>, usize) = crate::decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);
    }

    #[test]
    fn test_encode_decode_option() {
        let config = config::standard();
        let value = Some(42u32);
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): (Option<u32>, usize) = crate::decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);

        let value = None::<u32>;
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): (Option<u32>, usize) = crate::decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);
    }

    #[test]
    fn test_encode_option_none_directly() {
        let config = config::standard();
        let mut writer = Writer::new(config);
        let none: Option<u32> = None;
        none.encode(&mut writer).unwrap();
        let bytes = writer.into_bytes();
        // Should be just a single byte (false)
        assert_eq!(bytes.len(), 1);
        assert_eq!(bytes[0], 0);
    }

    #[test]
    fn test_encode_option_some_directly() {
        let config = config::standard();
        let mut writer = Writer::new(config);
        let some: Option<u32> = Some(42);
        some.encode(&mut writer).unwrap();
        let bytes = writer.into_bytes();
        // Should be 1 byte (true) + 4 bytes (u32)
        assert_eq!(bytes.len(), 5);
        assert_eq!(bytes[0], 1);
    }

    #[test]
    fn test_encode_decode_string() {
        let config = config::standard();
        let value = "hello, world!".to_string();
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): (String, usize) = crate::decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);
    }

    #[test]
    fn test_encode_decode_str() {
        let config = config::standard();
        let value = "hello, world!";
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): (String, usize) = crate::decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);
    }

    #[test]
    fn test_encode_decode_bytes() {
        let config = config::standard();
        let value: &[u8] = &[1, 2, 3, 4, 5];
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): (Vec<u8>, usize) = crate::decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);
    }

    #[test]
    fn test_encode_decode_tuple() {
        let config = config::standard();
        let value = (42u32, "hello".to_string(), true);
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): ((u32, String, bool), usize) =
            crate::decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);
    }

    #[test]
    fn test_encode_decode_tuple1() {
        let config = config::standard();
        let value = (42u32,);
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): ((u32,), usize) = crate::decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);
    }

    #[test]
    fn test_encode_decode_tuple2() {
        let config = config::standard();
        let value = (42u32, "hello".to_string());
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): ((u32, String), usize) = crate::decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);
    }

    #[test]
    fn test_encode_decode_tuple4() {
        let config = config::standard();
        let value = (1u32, 2u32, 3u32, 4u32);
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): ((u32, u32, u32, u32), usize) = crate::decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);
    }

    #[test]
    fn test_encode_decode_unit() {
        let config = config::standard();
        let value = ();
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): ((), usize) = crate::decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);
    }

    #[test]
    fn test_encode_decode_arrays() {
        let config = config::standard();
        
        // Test array of size 0
        let value: [u8; 0] = [];
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): ([u8; 0], usize) = crate::decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);

        // Test array of size 1
        let value = [42u8];
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): ([u8; 1], usize) = crate::decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);

        // Test array of size 5
        let value = [1u32, 2, 3, 4, 5];
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): ([u32; 5], usize) = crate::decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);

        // Test array of size 32
        let value: [u8; 32] = [0; 32];
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): ([u8; 32], usize) = crate::decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);
    }

    #[test]
    fn test_invalid_char() {
        let config = config::standard();
        let mut writer = Writer::new(config);
        // Write an invalid char code
        writer.write_u32(0x110000).unwrap();
        let bytes = writer.into_bytes();
        
        let mut reader = crate::reader::Reader::new(&bytes, config);
        let result: Result<char> = char::decode(&mut reader);
        assert!(result.is_err());
    }

    #[test]
    fn test_invalid_utf8() {
        let config = config::standard();
        // Create invalid UTF-8 bytes
        let invalid_bytes = vec![0xFF, 0xFE, 0xFD];
        let mut writer = Writer::new(config);
        invalid_bytes.encode(&mut writer).unwrap();
        let bytes = writer.into_bytes();
        
        let mut reader = crate::reader::Reader::new(&bytes, config);
        let result: Result<String> = String::decode(&mut reader);
        assert!(result.is_err());
    }
}

// Test no-std Vec implementations when std feature is disabled
#[cfg(all(test, not(feature = "std")))]
mod no_std_tests {
    use super::*;
    use crate::config;
    extern crate alloc;

    #[test]
    fn test_no_std_vec_encode() {
        let config = config::standard();
        let value = alloc::vec![1u32, 2, 3, 4, 5];
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): (alloc::vec::Vec<u32>, usize) = crate::decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);
    }

    #[test]
    fn test_no_std_vec_empty() {
        let config = config::standard();
        let value: alloc::vec::Vec<u32> = alloc::vec![];
        let encoded = crate::encode_to_vec(&value, config).unwrap();
        let (decoded, _): (alloc::vec::Vec<u32>, usize) = crate::decode_from_slice(&encoded, config).unwrap();
        assert_eq!(value, decoded);
    }
}
