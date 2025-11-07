//! Integration tests for no-std functionality
//! 
//! These tests verify that the no-std Vec implementations work correctly.
//! The no-std code paths are tested by compiling without the std feature.

use justcode_core::{config, Decode, Encode};

#[derive(Encode, Decode, PartialEq, Debug, Clone)]
struct SimpleStruct {
    value: u32,
    flag: bool,
}

// Test that Vec encoding/decoding works (this will use std Vec implementation in default build)
// To test no-std implementation, compile with --no-default-features
#[test]
fn test_vec_implementation() {
    let config = config::standard();
    
    let value = vec![1u32, 2, 3, 4, 5];
    let encoded = justcode_core::encode_to_vec(&value, config).unwrap();
    let (decoded, _): (Vec<u32>, usize) = justcode_core::decode_from_slice(&encoded, config).unwrap();
    
    assert_eq!(value, decoded);
}

#[test]
fn test_empty_vec_implementation() {
    let config = config::standard();
    
    let value: Vec<u32> = Vec::new();
    let encoded = justcode_core::encode_to_vec(&value, config).unwrap();
    let (decoded, _): (Vec<u32>, usize) = justcode_core::decode_from_slice(&encoded, config).unwrap();
    
    assert_eq!(value, decoded);
}

#[test]
fn test_struct_with_vec() {
    let config = config::standard();
    
    let data = SimpleStruct {
        value: 42,
        flag: true,
    };
    
    let vec_data = vec![data.clone(), data];
    let encoded = justcode_core::encode_to_vec(&vec_data, config).unwrap();
    let (decoded, _): (Vec<SimpleStruct>, usize) = justcode_core::decode_from_slice(&encoded, config).unwrap();
    
    assert_eq!(vec_data, decoded);
}

#[test]
fn test_option_with_vec() {
    let config = config::standard();
    
    let value: Option<Vec<u32>> = Some(vec![1, 2, 3]);
    let encoded = justcode_core::encode_to_vec(&value, config).unwrap();
    let (decoded, _): (Option<Vec<u32>>, usize) = justcode_core::decode_from_slice(&encoded, config).unwrap();
    
    assert_eq!(value, decoded);
}

#[test]
fn test_large_vec_implementation() {
    let config = config::standard();
    
    let mut value = Vec::new();
    for i in 0..100 {
        value.push(i as u32);
    }
    
    let encoded = justcode_core::encode_to_vec(&value, config).unwrap();
    let (decoded, _): (Vec<u32>, usize) = justcode_core::decode_from_slice(&encoded, config).unwrap();
    
    assert_eq!(value, decoded);
}

