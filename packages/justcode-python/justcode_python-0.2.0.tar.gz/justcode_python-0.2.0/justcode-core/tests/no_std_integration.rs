//! Integration tests specifically for no-std Vec implementations
//!
//! These tests compile and run WITHOUT the `std` feature to test the no-std Vec code paths.
//!
//! To run these tests:
//! ```bash
//! cargo test --package justcode-core --test no_std_integration --no-default-features --features derive
//! ```

#![cfg(not(feature = "std"))]
#![no_std]

extern crate alloc;

use alloc::vec::Vec;
use justcode_core::{config, Decode, Encode};

#[derive(Encode, Decode, PartialEq, Debug)]
struct TestStruct {
    id: u32,
    data: Vec<u8>,
}

#[derive(Encode, Decode, PartialEq, Debug)]
struct NestedStruct {
    items: Vec<TestStruct>,
    count: u32,
}

#[test]
fn test_no_std_vec_basic() {
    let config = config::standard();
    
    let value = alloc::vec![1u32, 2, 3, 4, 5];
    let encoded = justcode_core::encode_to_vec(&value, config).unwrap();
    let (decoded, _): (Vec<u32>, usize) = justcode_core::decode_from_slice(&encoded, config).unwrap();
    
    assert_eq!(value, decoded);
}

#[test]
fn test_no_std_vec_empty() {
    let config = config::standard();
    
    let value: Vec<u32> = Vec::new();
    let encoded = justcode_core::encode_to_vec(&value, config).unwrap();
    let (decoded, _): (Vec<u32>, usize) = justcode_core::decode_from_slice(&encoded, config).unwrap();
    
    assert_eq!(value, decoded);
}

#[test]
fn test_no_std_vec_large() {
    let config = config::standard();
    
    let mut value = Vec::new();
    for i in 0..100 {
        value.push(i as u32);
    }
    
    let encoded = justcode_core::encode_to_vec(&value, config).unwrap();
    let (decoded, _): (Vec<u32>, usize) = justcode_core::decode_from_slice(&encoded, config).unwrap();
    
    assert_eq!(value, decoded);
}

#[test]
fn test_no_std_struct_with_vec() {
    let config = config::standard();
    
    let data = TestStruct {
        id: 42,
        data: alloc::vec![1, 2, 3, 4, 5],
    };
    
    let encoded = justcode_core::encode_to_vec(&data, config).unwrap();
    let (decoded, _): (TestStruct, usize) = justcode_core::decode_from_slice(&encoded, config).unwrap();
    
    assert_eq!(data, decoded);
}

#[test]
fn test_no_std_nested_vec() {
    let config = config::standard();
    
    let data = NestedStruct {
        items: alloc::vec![
            TestStruct {
                id: 1,
                data: alloc::vec![1, 2, 3],
            },
            TestStruct {
                id: 2,
                data: alloc::vec![4, 5, 6],
            },
        ],
        count: 2,
    };
    
    let encoded = justcode_core::encode_to_vec(&data, config).unwrap();
    let (decoded, _): (NestedStruct, usize) = justcode_core::decode_from_slice(&encoded, config).unwrap();
    
    assert_eq!(data, decoded);
}

#[test]
fn test_no_std_option_with_vec() {
    let config = config::standard();
    
    let value: Option<Vec<u32>> = Some(alloc::vec![1, 2, 3]);
    let encoded = justcode_core::encode_to_vec(&value, config).unwrap();
    let (decoded, _): (Option<Vec<u32>>, usize) = justcode_core::decode_from_slice(&encoded, config).unwrap();
    
    assert_eq!(value, decoded);
    
    let none_value: Option<Vec<u32>> = None;
    let encoded = justcode_core::encode_to_vec(&none_value, config).unwrap();
    let (decoded, _): (Option<Vec<u32>>, usize) = justcode_core::decode_from_slice(&encoded, config).unwrap();
    
    assert_eq!(none_value, decoded);
}

#[test]
fn test_no_std_vec_of_primitives() {
    let config = config::standard();
    
    // Test different primitive types in Vec
    let u8_vec = alloc::vec![1u8, 2, 3, 255];
    let encoded = justcode_core::encode_to_vec(&u8_vec, config).unwrap();
    let (decoded, _): (Vec<u8>, usize) = justcode_core::decode_from_slice(&encoded, config).unwrap();
    assert_eq!(u8_vec, decoded);
    
    let u32_vec = alloc::vec![100u32, 200, 300];
    let encoded = justcode_core::encode_to_vec(&u32_vec, config).unwrap();
    let (decoded, _): (Vec<u32>, usize) = justcode_core::decode_from_slice(&encoded, config).unwrap();
    assert_eq!(u32_vec, decoded);
    
    let bool_vec = alloc::vec![true, false, true];
    let encoded = justcode_core::encode_to_vec(&bool_vec, config).unwrap();
    let (decoded, _): (Vec<bool>, usize) = justcode_core::decode_from_slice(&encoded, config).unwrap();
    assert_eq!(bool_vec, decoded);
}

#[test]
fn test_no_std_vec_varint_encoding() {
    let config = config::standard();
    
    // Test that varint encoding works with no-std Vec
    let small_vec = alloc::vec![1u32]; // Small length should use 1 byte varint
    let encoded = justcode_core::encode_to_vec(&small_vec, config).unwrap();
    // First byte should be the varint-encoded length (1), then 4 bytes for the u32
    assert!(encoded.len() <= 6); // 1 byte varint + 4 bytes u32
    
    let (decoded, _): (Vec<u32>, usize) = justcode_core::decode_from_slice(&encoded, config).unwrap();
    assert_eq!(small_vec, decoded);
}

#[test]
fn test_no_std_vec_with_config() {
    // Test with different configurations
    let config_with_limit = config::standard().with_limit(1000);
    let value = alloc::vec![1u32, 2, 3];
    let encoded = justcode_core::encode_to_vec(&value, config_with_limit).unwrap();
    let (decoded, _): (Vec<u32>, usize) = justcode_core::decode_from_slice(&encoded, config_with_limit).unwrap();
    assert_eq!(value, decoded);
    
    let config_no_varint = config::standard().with_variable_int_encoding(false);
    let value = alloc::vec![1u32, 2, 3];
    let encoded = justcode_core::encode_to_vec(&value, config_no_varint).unwrap();
    let (decoded, _): (Vec<u32>, usize) = justcode_core::decode_from_slice(&encoded, config_no_varint).unwrap();
    assert_eq!(value, decoded);
}
