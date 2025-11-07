//! Memory size verification tests
//!
//! This test suite verifies the claim that "The encoded size will be the same
//! or smaller than the size that the object takes up in memory in a running
//! Rust program."
//!
//! It measures actual memory usage (stack + heap) and compares it to encoded sizes.

use justcode_core::{config, Decode, Encode};
use std::mem;

/// Calculate the actual memory footprint of a value
/// This includes both stack and heap allocations
trait MemorySize {
    fn memory_size(&self) -> usize;
}

impl MemorySize for u8 {
    fn memory_size(&self) -> usize {
        mem::size_of::<u8>()
    }
}

impl MemorySize for u16 {
    fn memory_size(&self) -> usize {
        mem::size_of::<u16>()
    }
}

impl MemorySize for u32 {
    fn memory_size(&self) -> usize {
        mem::size_of::<u32>()
    }
}

impl MemorySize for u64 {
    fn memory_size(&self) -> usize {
        mem::size_of::<u64>()
    }
}

impl MemorySize for i8 {
    fn memory_size(&self) -> usize {
        mem::size_of::<i8>()
    }
}

impl MemorySize for i16 {
    fn memory_size(&self) -> usize {
        mem::size_of::<i16>()
    }
}

impl MemorySize for i32 {
    fn memory_size(&self) -> usize {
        mem::size_of::<i32>()
    }
}

impl MemorySize for i64 {
    fn memory_size(&self) -> usize {
        mem::size_of::<i64>()
    }
}

impl MemorySize for f32 {
    fn memory_size(&self) -> usize {
        mem::size_of::<f32>()
    }
}

impl MemorySize for f64 {
    fn memory_size(&self) -> usize {
        mem::size_of::<f64>()
    }
}

impl MemorySize for bool {
    fn memory_size(&self) -> usize {
        mem::size_of::<bool>()
    }
}

impl MemorySize for char {
    fn memory_size(&self) -> usize {
        mem::size_of::<char>()
    }
}

impl<T> MemorySize for Vec<T>
where
    T: MemorySize,
{
    fn memory_size(&self) -> usize {
        // Stack size of Vec (pointer, length, capacity)
        let vec_overhead = mem::size_of::<Vec<T>>();
        // Heap-allocated data (capacity, not length, because Vec allocates capacity)
        let data_size = self.capacity() * mem::size_of::<T>();
        // For each element, calculate its memory size (which may include heap allocations)
        // Subtract the stack size of T since we already counted it in data_size
        let element_extra_heap: usize = self
            .iter()
            .map(|e| {
                let element_total = e.memory_size();
                let element_stack = mem::size_of::<T>();
                element_total.saturating_sub(element_stack)
            })
            .sum();
        vec_overhead + data_size + element_extra_heap
    }
}

impl MemorySize for String {
    fn memory_size(&self) -> usize {
        // Stack size of String (pointer, length, capacity)
        let string_overhead = mem::size_of::<String>();
        // Heap-allocated bytes
        let data_size = self.capacity();
        string_overhead + data_size
    }
}

impl<T> MemorySize for Option<T>
where
    T: MemorySize,
{
    fn memory_size(&self) -> usize {
        match self {
            Some(value) => mem::size_of::<Option<T>>() + value.memory_size(),
            None => mem::size_of::<Option<T>>(),
        }
    }
}

#[derive(Encode, Decode, PartialEq, Debug, Clone)]
struct Point {
    x: f32,
    y: f32,
}

impl MemorySize for Point {
    fn memory_size(&self) -> usize {
        mem::size_of::<Point>()
    }
}

#[derive(Encode, Decode, PartialEq, Debug, Clone)]
struct Entity {
    id: u32,
    position: Point,
    health: f32,
    active: bool,
}

impl MemorySize for Entity {
    fn memory_size(&self) -> usize {
        mem::size_of::<Entity>()
    }
}

#[derive(Encode, Decode, PartialEq, Debug, Clone)]
struct World {
    entities: Vec<Entity>,
    name: String,
}

impl MemorySize for World {
    fn memory_size(&self) -> usize {
        let struct_size = mem::size_of::<World>();
        let entities_size = self.entities.memory_size();
        let name_size = self.name.memory_size();
        struct_size + entities_size + name_size - mem::size_of::<Vec<Entity>>() - mem::size_of::<String>()
    }
}

/// Test helper that verifies encoded size <= memory size
fn verify_size_claim<T: Encode + MemorySize>(value: &T, name: &str, config: config::Config) {
    let memory_size = value.memory_size();
    let encoded = justcode_core::encode_to_vec(value, config).unwrap();
    let encoded_size = encoded.len();
    
    println!(
        "  {}: memory={} bytes, encoded={} bytes, ratio={:.2}%",
        name,
        memory_size,
        encoded_size,
        (encoded_size as f64 / memory_size as f64) * 100.0
    );
    
    assert!(
        encoded_size <= memory_size,
        "Encoded size ({}) exceeds memory size ({}) for {}",
        encoded_size,
        memory_size,
        name
    );
}

#[test]
fn test_primitives_memory_size() {
    println!("\n=== Testing Primitives ===");
    let config = config::standard();
    
    verify_size_claim(&42u8, "u8", config);
    verify_size_claim(&42u16, "u16", config);
    verify_size_claim(&42u32, "u32", config);
    verify_size_claim(&42u64, "u64", config);
    verify_size_claim(&42i8, "i8", config);
    verify_size_claim(&42i16, "i16", config);
    verify_size_claim(&42i32, "i32", config);
    verify_size_claim(&42i64, "i64", config);
    verify_size_claim(&3.14f32, "f32", config);
    verify_size_claim(&3.14f64, "f64", config);
    verify_size_claim(&true, "bool", config);
    verify_size_claim(&'A', "char", config);
}

#[test]
fn test_vec_primitives_memory_size() {
    println!("\n=== Testing Vec of Primitives ===");
    let config = config::standard();
    
    let empty_vec: Vec<u32> = vec![];
    verify_size_claim(&empty_vec, "Vec<u32> (empty)", config);
    
    let small_vec = vec![1u32, 2, 3, 4, 5];
    verify_size_claim(&small_vec, "Vec<u32> (5 elements)", config);
    
    let medium_vec: Vec<u32> = (0..100).collect();
    verify_size_claim(&medium_vec, "Vec<u32> (100 elements)", config);
    
    let large_vec: Vec<u32> = (0..1000).collect();
    verify_size_claim(&large_vec, "Vec<u32> (1000 elements)", config);
    
    let vec_u8: Vec<u8> = (0..255).collect();
    verify_size_claim(&vec_u8, "Vec<u8> (255 elements)", config);
}

#[test]
fn test_string_memory_size() {
    println!("\n=== Testing String ===");
    let config = config::standard();
    
    let empty_string = String::new();
    verify_size_claim(&empty_string, "String (empty)", config);
    
    let small_string = "Hello".to_string();
    verify_size_claim(&small_string, "String (small)", config);
    
    let medium_string = "Hello, World! This is a medium-sized string.".to_string();
    verify_size_claim(&medium_string, "String (medium)", config);
    
    let large_string = "A".repeat(1000);
    verify_size_claim(&large_string, "String (1000 chars)", config);
}

#[test]
fn test_option_memory_size() {
    println!("\n=== Testing Option ===");
    let config = config::standard();
    
    let some_u32 = Some(42u32);
    verify_size_claim(&some_u32, "Option<u32> (Some)", config);
    
    let none_u32: Option<u32> = None;
    verify_size_claim(&none_u32, "Option<u32> (None)", config);
    
    let some_string = Some("Hello".to_string());
    verify_size_claim(&some_string, "Option<String> (Some)", config);
    
    let none_string: Option<String> = None;
    verify_size_claim(&none_string, "Option<String> (None)", config);
}

#[test]
fn test_structs_memory_size() {
    println!("\n=== Testing Structs ===");
    let config = config::standard();
    
    let point = Point { x: 1.0, y: 2.0 };
    verify_size_claim(&point, "Point", config);
    
    let entity = Entity {
        id: 1,
        position: Point { x: 0.0, y: 4.0 },
        health: 100.0,
        active: true,
    };
    verify_size_claim(&entity, "Entity", config);
    
    let world = World {
        entities: vec![
            Entity {
                id: 1,
                position: Point { x: 0.0, y: 4.0 },
                health: 100.0,
                active: true,
            },
            Entity {
                id: 2,
                position: Point { x: 10.0, y: 20.5 },
                health: 75.5,
                active: false,
            },
        ],
        name: "Test World".to_string(),
    };
    verify_size_claim(&world, "World (2 entities)", config);
    
    let large_world = World {
        entities: (0..100)
            .map(|i| Entity {
                id: i,
                position: Point {
                    x: i as f32,
                    y: (i * 2) as f32,
                },
                health: 100.0,
                active: i % 2 == 0,
            })
            .collect(),
        name: "Large World".to_string(),
    };
    verify_size_claim(&large_world, "World (100 entities)", config);
}

#[test]
fn test_nested_collections_memory_size() {
    println!("\n=== Testing Nested Collections ===");
    let config = config::standard();
    
    let vec_of_strings = vec![
        "Hello".to_string(),
        "World".to_string(),
        "Test".to_string(),
    ];
    verify_size_claim(&vec_of_strings, "Vec<String> (3 elements)", config);
    
    let vec_of_vecs: Vec<Vec<u32>> = vec![
        vec![1, 2, 3],
        vec![4, 5, 6],
        vec![7, 8, 9],
    ];
    verify_size_claim(&vec_of_vecs, "Vec<Vec<u32>> (3x3)", config);
    
    let vec_of_options: Vec<Option<String>> = vec![
        Some("Hello".to_string()),
        None,
        Some("World".to_string()),
    ];
    verify_size_claim(&vec_of_options, "Vec<Option<String>> (3 elements)", config);
}

#[test]
fn test_comprehensive_memory_verification() {
    println!("\n=== Comprehensive Memory Verification ===");
    let config = config::standard();
    
    // Test various sizes and types
    let u32_val = 42u32;
    verify_size_claim(&u32_val, "u32 (comprehensive)", config);
    
    let vec_val = vec![1u32, 2, 3];
    verify_size_claim(&vec_val, "Vec<u32> (3, comprehensive)", config);
    
    let string_val = "Hello".to_string();
    verify_size_claim(&string_val, "String (5, comprehensive)", config);
    
    let option_val = Some(42u32);
    verify_size_claim(&option_val, "Option<u32> (Some, comprehensive)", config);
}

#[test]
fn test_varint_encoding_benefit() {
    println!("\n=== Testing Varint Encoding Benefit ===");
    let config_with_varint = config::standard().with_variable_int_encoding(true);
    let config_without_varint = config::standard().with_variable_int_encoding(false);
    
    // Small values benefit from varint encoding
    let small_vec: Vec<u32> = (0..10).collect();
    
    let encoded_with = justcode_core::encode_to_vec(&small_vec, config_with_varint).unwrap();
    let encoded_without = justcode_core::encode_to_vec(&small_vec, config_without_varint).unwrap();
    
    println!(
        "  Vec<u32> (10 elements): with_varint={} bytes, without_varint={} bytes",
        encoded_with.len(),
        encoded_without.len()
    );
    
    // Varint should be smaller or equal for small values
    assert!(encoded_with.len() <= encoded_without.len());
}

