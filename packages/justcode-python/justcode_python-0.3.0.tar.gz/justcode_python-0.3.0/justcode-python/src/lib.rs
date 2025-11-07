//! # Justcode Python Bindings
//!
//! Python bindings for justcode binary encoder/decoder using PyO3.

use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyList, PyDict, PyInt, PyFloat, PyString, PyBool};
use justcode_core::{Config, encode_to_vec, decode_from_slice};
use justcode_core::config;

/// Python wrapper for Config
#[pyclass]
#[derive(Clone)]
pub struct PyConfig {
    inner: Config,
}

#[pymethods]
impl PyConfig {
    #[new]
    #[pyo3(signature = (size_limit = None, variable_int_encoding = None))]
    fn new(
        size_limit: Option<usize>,
        variable_int_encoding: Option<bool>,
    ) -> Self {
        let mut config = config::standard();
        
        if let Some(limit) = size_limit {
            config = config.with_limit(limit);
        }
        
        if let Some(use_varint) = variable_int_encoding {
            config = config.with_variable_int_encoding(use_varint);
        }
        
        Self { inner: config }
    }
    
    /// Create a standard configuration
    #[staticmethod]
    fn standard() -> Self {
        Self {
            inner: config::standard(),
        }
    }
    
    /// Set size limit
    fn with_limit(&self, limit: usize) -> Self {
        Self {
            inner: self.inner.with_limit(limit),
        }
    }
    
    /// Set variable int encoding
    fn with_variable_int_encoding(&self, enabled: bool) -> Self {
        Self {
            inner: self.inner.with_variable_int_encoding(enabled),
        }
    }
    
    /// Get size limit
    fn get_limit(&self) -> Option<usize> {
        self.inner.limit
    }
    
    /// Check if variable int encoding is enabled
    fn uses_variable_int_encoding(&self) -> bool {
        self.inner.variable_int_encoding
    }
}

/// Encode a Python value to bytes
#[pyfunction]
#[pyo3(signature = (value, config = None))]
fn encode(value: &Bound<PyAny>, config: Option<PyConfig>) -> PyResult<Vec<u8>> {
    let cfg = config.unwrap_or_else(|| PyConfig::standard()).inner;
    
    // Handle different Python types
    // IMPORTANT: Check bool BEFORE int, because bool is a subclass of int in Python
    // This ensures True/False are encoded as 1-byte bools, not 8-byte ints
    if let Ok(bool_val) = value.extract::<bool>() {
        encode_to_vec(&bool_val, cfg)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Encoding error: {}", e)))
    } else if let Ok(bytes) = value.cast::<PyBytes>() {
        let data: Vec<u8> = bytes.as_bytes().to_vec();
        encode_to_vec(&data, cfg)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Encoding error: {}", e)))
    } else if let Ok(int_val) = value.extract::<i64>() {
        encode_to_vec(&int_val, cfg)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Encoding error: {}", e)))
    } else if let Ok(uint_val) = value.extract::<u64>() {
        encode_to_vec(&uint_val, cfg)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Encoding error: {}", e)))
    } else if let Ok(float_val) = value.extract::<f64>() {
        encode_to_vec(&float_val, cfg)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Encoding error: {}", e)))
    } else if let Ok(str_val) = value.extract::<String>() {
        encode_to_vec(&str_val, cfg)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Encoding error: {}", e)))
    } else if let Ok(list) = value.cast::<PyList>() {
        encode_list(list, cfg)
    } else if let Ok(dict) = value.cast::<PyDict>() {
        encode_dict(dict, cfg)
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
            format!("Unsupported type for encoding: {}", value.get_type().name()?)
        ))
    }
}

/// Encode a Python list
fn encode_list(list: &Bound<PyList>, config: Config) -> PyResult<Vec<u8>> {
    // For now, encode as Vec<u8> by converting each item to bytes
    // This is a simplified approach - in a real implementation, you'd want
    // to handle heterogeneous lists more carefully
    let mut all_bytes = Vec::new();
    for item in list.iter() {
        if let Ok(bytes) = item.cast::<PyBytes>() {
            all_bytes.extend_from_slice(bytes.as_bytes());
        } else if let Ok(int_val) = item.extract::<i64>() {
            let encoded = encode_to_vec(&int_val, config)
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Encoding error: {}", e)))?;
            all_bytes.extend_from_slice(&encoded);
        } else {
            return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                "List items must be bytes or integers"
            ));
        }
    }
    
    encode_to_vec(&all_bytes, config)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Encoding error: {}", e)))
}

/// Encode a Python dict (simplified - just encode as bytes)
fn encode_dict(dict: &Bound<PyDict>, config: Config) -> PyResult<Vec<u8>> {
    // For simplicity, convert dict to a sorted list of key-value pairs as bytes
    let mut pairs: Vec<(String, Vec<u8>)> = Vec::new();
    
    for (key, value) in dict.iter() {
        let key_str = key.extract::<String>()
            .map_err(|_| PyErr::new::<pyo3::exceptions::PyTypeError, _>("Dict keys must be strings"))?;
        
        let value_bytes = if let Ok(bytes) = value.cast::<PyBytes>() {
            bytes.as_bytes().to_vec()
        } else if let Ok(int_val) = value.extract::<i64>() {
            encode_to_vec(&int_val, config)
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Encoding error: {}", e)))?
        } else if let Ok(str_val) = value.extract::<String>() {
            encode_to_vec(&str_val, config)
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Encoding error: {}", e)))?
        } else {
            return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                "Dict values must be bytes, strings, or integers"
            ));
        };
        
        pairs.push((key_str, value_bytes));
    }
    
    // Encode pairs count and then each pair
    let mut result = encode_to_vec(&(pairs.len() as u64), config)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Encoding error: {}", e)))?;
    
    for (key, value_bytes) in pairs {
        let key_encoded = encode_to_vec(&key, config)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Encoding error: {}", e)))?;
        result.extend_from_slice(&key_encoded);
        result.extend_from_slice(&value_bytes);
    }
    
    Ok(result)
}

/// Decode bytes to a Python value
#[pyfunction]
#[pyo3(signature = (data, config = None, target_type = None))]
fn decode(data: &Bound<PyAny>, config: Option<PyConfig>, target_type: Option<&str>) -> PyResult<Py<PyAny>> {
    let cfg = config.unwrap_or_else(|| PyConfig::standard()).inner;
    
    // Extract bytes from Python
    let bytes = if let Ok(py_bytes) = data.cast::<PyBytes>() {
        py_bytes.as_bytes()
    } else {
        return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
            "Expected bytes or bytearray"
        ));
    };
    
    let py = data.py();
    
    // If target type is specified, decode to that type
    if let Some(type_name) = target_type {
        match type_name {
            "int" | "i64" => {
                let (value, _): (i64, usize) = decode_from_slice(bytes, cfg)
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Decoding error: {}", e)))?;
                return Ok(PyInt::new(py, value).into());
            }
            "uint" | "u64" => {
                let (value, _): (u64, usize) = decode_from_slice(bytes, cfg)
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Decoding error: {}", e)))?;
                return Ok(PyInt::new(py, value as i64).into());
            }
            "float" | "f64" => {
                let (value, _): (f64, usize) = decode_from_slice(bytes, cfg)
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Decoding error: {}", e)))?;
                return Ok(PyFloat::new(py, value).into());
            }
            "bool" => {
                let (value, _): (bool, usize) = decode_from_slice(bytes, cfg)
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Decoding error: {}", e)))?;
                // Use into_pyobject to get Bound, then clone before unbinding to avoid move issues
                let bound_result = value.into_pyobject(py);
                let bound = bound_result.unwrap();
                // Clone the Bound before unbinding to satisfy borrow checker
                let cloned = <pyo3::Bound<'_, PyBool> as Clone>::clone(&bound);
                return Ok(cloned.unbind().into());
            }
            "str" | "string" => {
                let (value, _): (String, usize) = decode_from_slice(bytes, cfg)
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Decoding error: {}", e)))?;
                return Ok(PyString::new(py, &value).into());
            }
            "bytes" => {
                let (value, _): (Vec<u8>, usize) = decode_from_slice(bytes, cfg)
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Decoding error: {}", e)))?;
                return Ok(PyBytes::new(py, &value).into());
            }
            _ => {
                return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                    format!("Unknown target type: {}", type_name)
                ));
            }
        }
    }
    
    // Try to auto-detect type by attempting different decodings
    // Order matters: try more specific types first to avoid false matches
    // We need to check that all bytes were consumed to ensure correct type detection
    
    // Try as String first (most common for text data)
    if let Ok((value, consumed)) = decode_from_slice::<String>(bytes, cfg) {
        if consumed == bytes.len() {
            return Ok(PyString::new(py, &value).into());
        }
    }
    
    // Try as bool (single byte, very specific)
    if let Ok((value, consumed)) = decode_from_slice::<bool>(bytes, cfg) {
        if consumed == bytes.len() {
            // into_pyobject returns Result<Bound, Infallible>, so unwrap is safe
            let bound = value.into_pyobject(py).unwrap();
            let cloned = <pyo3::Bound<'_, PyBool> as Clone>::clone(&bound);
            return Ok(cloned.unbind().into());
        }
    }
    
    // Try as i64
    if let Ok((value, consumed)) = decode_from_slice::<i64>(bytes, cfg) {
        if consumed == bytes.len() {
            return Ok(PyInt::new(py, value).into());
        }
    }
    
    // Try as u64
    if let Ok((value, consumed)) = decode_from_slice::<u64>(bytes, cfg) {
        if consumed == bytes.len() {
            return Ok(PyInt::new(py, value as i64).into());
        }
    }
    
    // Try as f64
    if let Ok((value, consumed)) = decode_from_slice::<f64>(bytes, cfg) {
        if consumed == bytes.len() {
            return Ok(PyFloat::new(py, value).into());
        }
    }
    
    // Try as Vec<u8> (bytes) last, as it's the least specific
    if let Ok((value, consumed)) = decode_from_slice::<Vec<u8>>(bytes, cfg) {
        if consumed == bytes.len() {
            return Ok(PyBytes::new(py, &value).into());
        }
    }
    
    Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
        "Could not decode bytes - unknown format"
    ))
}

/// Python module definition
#[pymodule]
fn justcode(_py: Python, m: &Bound<PyModule>) -> PyResult<()> {
    m.add_class::<PyConfig>()?;
    m.add_function(wrap_pyfunction!(encode, m)?)?;
    m.add_function(wrap_pyfunction!(decode, m)?)?;
    m.add("__version__", "0.3.0")?;
    Ok(())
}

// Note: Rust unit tests for PyO3 bindings require Python to be linked at compile time,
// which is complex to set up. Instead, we use comprehensive Python pytest tests
// in tests/test_justcode_python.py which are more appropriate for testing Python bindings.
//
// To run the Python tests:
//   cd justcode-python
//   maturin develop
//   pytest tests/test_justcode_python.py -v
