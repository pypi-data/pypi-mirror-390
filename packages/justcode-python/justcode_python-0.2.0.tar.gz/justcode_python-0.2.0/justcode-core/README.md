# Justcode

A compact binary encoder/decoder with space-efficient encoding scheme. The encoded size will be the same or smaller than the size that the object takes up in memory in a running Rust program.

Justcode is a replacement for bincode, providing similar functionality with a focus on binary encoding without any ideological baggage.

## Features

- **Compact Encoding**: Space-efficient binary encoding that's the same size or smaller than in-memory representation
- **Varint Encoding**: Variable-length integer encoding for lengths and small values (enabled by default)
- **Architecture Invariant**: Byte-order independent, works across different architectures
- **Streaming API**: Reader/Writer API for integration with files, network streams, and compression libraries
- **Configurable**: Size limits, variable int encoding, and other options
- **Derive Macros**: Automatic `Encode` and `Decode` trait implementations

## Usage

Add to your `Cargo.toml`:

```toml
[dependencies]
justcode-core = { path = "../services/justcode/justcode-core" }
```

## Example

```rust
use justcode_core::{config, Decode, Encode};

#[derive(Encode, Decode, PartialEq, Debug)]
struct Entity {
    x: f32,
    y: f32,
}

#[derive(Encode, Decode, PartialEq, Debug)]
struct World(Vec<Entity>);

fn main() {
    let config = config::standard();

    let world = World(vec![Entity { x: 0.0, y: 4.0 }, Entity { x: 10.0, y: 20.5 }]);

    let encoded: Vec<u8> = justcode_core::encode_to_vec(&world, config).unwrap();

    // The length of the vector is encoded as a varint u64, which in this case is encoded as a single byte
    // See the documentation on varint for more information.
    // The 4 floats are encoded in 4 bytes each.
    assert_eq!(encoded.len(), 1 + 4 * 4);

    let (decoded, len): (World, usize) = justcode_core::decode_from_slice(&encoded[..], config).unwrap();

    assert_eq!(world, decoded);
    assert_eq!(len, encoded.len()); // read all bytes
}
```

## Configuration

Justcode provides a configurable encoding system:

```rust
use justcode_core::config;

// Standard configuration (varint encoding enabled, no size limit)
let config = config::standard();

// With size limit (recommended for untrusted input)
let config = config::standard().with_limit(1024 * 1024); // 1MB limit

// Without variable int encoding (fixed-size integers)
let config = config::standard().with_variable_int_encoding(false);
```

## Supported Types

### Primitives

- All integer types: `u8`, `u16`, `u32`, `u64`, `usize`, `i8`, `i16`, `i32`, `i64`
- Floating point: `f32`, `f64`
- Boolean: `bool`
- Character: `char`

### Collections

- `Vec<T>` where `T: Encode/Decode`
- `Option<T>` where `T: Encode/Decode`
- `String` and `&str`
- Arrays up to 32 elements
- Tuples up to 4 elements

### Custom Types

Use the derive macros for structs and enums:

```rust
#[derive(Encode, Decode)]
struct MyStruct {
    field1: u32,
    field2: String,
}

#[derive(Encode, Decode)]
enum MyEnum {
    Variant1,
    Variant2(u32),
    Variant3 { x: f32, y: f32 },
}
```

## Enum Encoding

Enums are encoded with a variant index (using varint encoding by default) followed by the variant data. The variant index is determined by the order of variants in the enum definition.

## Reader/Writer API

For streaming operations:

```rust
use justcode_core::{config, writer::Writer, reader::Reader};

let config = config::standard();
let mut writer = Writer::new(config);
value.encode(&mut writer)?;
let bytes = writer.into_bytes();

let mut reader = Reader::new(&bytes, config);
let decoded = T::decode(&mut reader)?;
```

## Testing

### Standard Tests

Run all tests with:

```bash
cargo test --workspace
```

### No-Std Tests

Test the no-std code paths separately:

```bash
cargo test --package justcode-core --test no_std_integration --no-default-features --features derive
```

The no-std tests verify that the conditionally compiled Vec implementations work correctly without the `std` feature.

## FAQ

### Is Justcode suitable for storage?

Yes, the encoding format is stable when using the same configuration. Justcode is architecture-invariant and space-efficient, making it suitable for storage. However, it does not implement data versioning schemes or file headers.

### Is Justcode suitable for untrusted inputs?

Justcode attempts to protect against hostile data. Use `Config::with_limit()` to set a maximum size limit to prevent memory exhaustion attacks. Deserializing malicious inputs will fail safely without causing undefined behavior.

### What is Justcode's MSRV (minimum supported Rust version)?

Justcode requires Rust 1.70.0 or later.

### Why does justcode not respect `#[repr(u8)]`?

Justcode encodes enum variants using varint encoding (or u32 when variable int encoding is disabled). This ensures compact encoding while maintaining compatibility. If you need to interop with a different protocol, consider implementing `Encode` and `Decode` manually.

## License

MIT
