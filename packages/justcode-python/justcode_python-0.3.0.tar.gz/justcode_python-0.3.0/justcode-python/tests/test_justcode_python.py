"""Comprehensive pytest tests for justcode-python bindings."""

import pytest
import justcode


class TestPyConfig:
    """Tests for PyConfig class."""

    def test_standard_config(self):
        """Test creating a standard configuration."""
        config = justcode.PyConfig.standard()
        assert config.uses_variable_int_encoding() is True
        assert config.get_limit() is None

    def test_config_new_default(self):
        """Test creating config with default values."""
        config = justcode.PyConfig()
        assert config.uses_variable_int_encoding() is True
        assert config.get_limit() is None

    def test_config_new_with_limit(self):
        """Test creating config with size limit."""
        config = justcode.PyConfig(size_limit=1024)
        assert config.get_limit() == 1024
        assert config.uses_variable_int_encoding() is True

    def test_config_new_with_varint(self):
        """Test creating config with variable int encoding."""
        config = justcode.PyConfig(variable_int_encoding=False)
        assert config.uses_variable_int_encoding() is False
        assert config.get_limit() is None

    def test_config_new_with_all_options(self):
        """Test creating config with all options."""
        config = justcode.PyConfig(size_limit=2048, variable_int_encoding=False)
        assert config.get_limit() == 2048
        assert config.uses_variable_int_encoding() is False

    def test_config_with_limit(self):
        """Test with_limit method."""
        config = justcode.PyConfig.standard()
        new_config = config.with_limit(4096)
        assert new_config.get_limit() == 4096
        # Original config should be unchanged
        assert config.get_limit() is None

    def test_config_with_variable_int_encoding(self):
        """Test with_variable_int_encoding method."""
        config = justcode.PyConfig.standard()
        new_config = config.with_variable_int_encoding(False)
        assert new_config.uses_variable_int_encoding() is False
        # Original config should be unchanged
        assert config.uses_variable_int_encoding() is True


class TestEncode:
    """Tests for encode function."""

    def test_encode_int(self):
        """Test encoding integers."""
        encoded = justcode.encode(42)
        assert isinstance(encoded, bytes)
        assert len(encoded) > 0

    def test_encode_negative_int(self):
        """Test encoding negative integers."""
        encoded = justcode.encode(-42)
        assert isinstance(encoded, bytes)
        assert len(encoded) > 0

    def test_encode_large_int(self):
        """Test encoding large integers."""
        encoded = justcode.encode(2**63 - 1)
        assert isinstance(encoded, bytes)
        assert len(encoded) > 0

    def test_encode_string(self):
        """Test encoding strings."""
        encoded = justcode.encode("hello")
        assert isinstance(encoded, bytes)
        assert len(encoded) > 0

    def test_encode_empty_string(self):
        """Test encoding empty string."""
        encoded = justcode.encode("")
        assert isinstance(encoded, bytes)
        assert len(encoded) > 0

    def test_encode_unicode_string(self):
        """Test encoding Unicode strings."""
        encoded = justcode.encode("hello 世界")
        assert isinstance(encoded, bytes)
        assert len(encoded) > 0

    def test_encode_bool_true(self):
        """Test encoding boolean True."""
        encoded = justcode.encode(True)
        assert isinstance(encoded, bytes)
        assert len(encoded) > 0

    def test_encode_bool_false(self):
        """Test encoding boolean False."""
        encoded = justcode.encode(False)
        assert isinstance(encoded, bytes)
        assert len(encoded) > 0

    def test_encode_float(self):
        """Test encoding floats."""
        encoded = justcode.encode(3.14159)
        assert isinstance(encoded, bytes)
        assert len(encoded) > 0

    def test_encode_bytes(self):
        """Test encoding bytes."""
        encoded = justcode.encode(b"hello")
        assert isinstance(encoded, bytes)
        assert len(encoded) > 0

    def test_encode_with_config(self):
        """Test encoding with custom config."""
        config = justcode.PyConfig(size_limit=1024)
        encoded = justcode.encode(42, config=config)
        assert isinstance(encoded, bytes)
        assert len(encoded) > 0

    def test_encode_unsupported_type(self):
        """Test encoding unsupported type raises error."""
        # Lists with integers are supported, so test with an actually unsupported type
        # Use a custom object that can't be encoded
        class UnsupportedType:
            pass
        
        with pytest.raises(TypeError):
            justcode.encode(UnsupportedType())


class TestDecode:
    """Tests for decode function."""

    def test_decode_int(self):
        """Test decoding integers."""
        encoded = justcode.encode(12345)
        decoded = justcode.decode(encoded, target_type="int")
        assert decoded == 12345

    def test_decode_negative_int(self):
        """Test decoding negative integers."""
        encoded = justcode.encode(-12345)
        decoded = justcode.decode(encoded, target_type="int")
        assert decoded == -12345

    def test_decode_string(self):
        """Test decoding strings."""
        encoded = justcode.encode("test string")
        decoded = justcode.decode(encoded, target_type="str")
        assert decoded == "test string"

    def test_decode_empty_string(self):
        """Test decoding empty string."""
        encoded = justcode.encode("")
        decoded = justcode.decode(encoded, target_type="str")
        assert decoded == ""

    def test_decode_bool_true(self):
        """Test decoding boolean True."""
        encoded = justcode.encode(True)
        decoded = justcode.decode(encoded, target_type="bool")
        assert decoded is True

    def test_decode_bool_false(self):
        """Test decoding boolean False."""
        encoded = justcode.encode(False)
        decoded = justcode.decode(encoded, target_type="bool")
        assert decoded is False

    def test_decode_float(self):
        """Test decoding floats."""
        encoded = justcode.encode(3.14159)
        decoded = justcode.decode(encoded, target_type="float")
        assert abs(decoded - 3.14159) < 1e-6

    def test_decode_bytes(self):
        """Test decoding bytes."""
        original = b"hello world"
        encoded = justcode.encode(original)
        decoded = justcode.decode(encoded, target_type="bytes")
        assert decoded == original

    def test_decode_auto_detect_int(self):
        """Test auto-detection of integer type."""
        encoded = justcode.encode(42)
        decoded = justcode.decode(encoded)
        assert decoded == 42

    def test_decode_auto_detect_string(self):
        """Test auto-detection of string type."""
        encoded = justcode.encode("hello")
        decoded = justcode.decode(encoded)
        assert decoded == "hello"

    def test_decode_auto_detect_bool(self):
        """Test auto-detection of boolean type."""
        encoded = justcode.encode(True)
        decoded = justcode.decode(encoded)
        assert decoded is True

    def test_decode_with_config(self):
        """Test decoding with custom config."""
        config = justcode.PyConfig(size_limit=1024)
        encoded = justcode.encode(42)
        decoded = justcode.decode(encoded, config=config, target_type="int")
        assert decoded == 42

    def test_decode_invalid_bytes(self):
        """Test decoding invalid bytes raises error."""
        with pytest.raises(ValueError):
            justcode.decode(b"invalid", target_type="int")

    def test_decode_invalid_target_type(self):
        """Test decoding with invalid target type raises error."""
        encoded = justcode.encode(42)
        with pytest.raises(ValueError):
            justcode.decode(encoded, target_type="invalid_type")


class TestRoundTrip:
    """Tests for encode/decode round-trip operations."""

    def test_roundtrip_int(self):
        """Test round-trip encoding/decoding of integers."""
        original = 12345
        encoded = justcode.encode(original)
        decoded = justcode.decode(encoded, target_type="int")
        assert decoded == original

    def test_roundtrip_negative_int(self):
        """Test round-trip encoding/decoding of negative integers."""
        original = -12345
        encoded = justcode.encode(original)
        decoded = justcode.decode(encoded, target_type="int")
        assert decoded == original

    def test_roundtrip_string(self):
        """Test round-trip encoding/decoding of strings."""
        original = "test string"
        encoded = justcode.encode(original)
        decoded = justcode.decode(encoded, target_type="str")
        assert decoded == original

    def test_roundtrip_unicode_string(self):
        """Test round-trip encoding/decoding of Unicode strings."""
        original = "hello 世界 🌍"
        encoded = justcode.encode(original)
        decoded = justcode.decode(encoded, target_type="str")
        assert decoded == original

    def test_roundtrip_bool(self):
        """Test round-trip encoding/decoding of booleans."""
        for original in [True, False]:
            encoded = justcode.encode(original)
            decoded = justcode.decode(encoded, target_type="bool")
            assert decoded == original

    def test_roundtrip_float(self):
        """Test round-trip encoding/decoding of floats."""
        original = 3.14159
        encoded = justcode.encode(original)
        decoded = justcode.decode(encoded, target_type="float")
        assert abs(decoded - original) < 1e-6

    def test_roundtrip_bytes(self):
        """Test round-trip encoding/decoding of bytes."""
        original = b"hello world"
        encoded = justcode.encode(original)
        decoded = justcode.decode(encoded, target_type="bytes")
        assert decoded == original

    def test_roundtrip_with_config(self):
        """Test round-trip with custom configuration."""
        config = justcode.PyConfig(size_limit=1024, variable_int_encoding=False)
        original = 42
        encoded = justcode.encode(original, config=config)
        decoded = justcode.decode(encoded, config=config, target_type="int")
        assert decoded == original


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_encode_zero(self):
        """Test encoding zero."""
        encoded = justcode.encode(0)
        decoded = justcode.decode(encoded, target_type="int")
        assert decoded == 0

    def test_encode_one(self):
        """Test encoding one."""
        encoded = justcode.encode(1)
        decoded = justcode.decode(encoded, target_type="int")
        assert decoded == 1

    def test_encode_minus_one(self):
        """Test encoding minus one."""
        encoded = justcode.encode(-1)
        decoded = justcode.decode(encoded, target_type="int")
        assert decoded == -1

    def test_decode_empty_bytes(self):
        """Test decoding empty bytes raises error."""
        with pytest.raises(ValueError):
            justcode.decode(b"", target_type="int")

    def test_decode_wrong_type(self):
        """Test decoding with wrong target type raises error."""
        encoded = justcode.encode(42)
        with pytest.raises(ValueError):
            justcode.decode(encoded, target_type="str")


class TestVersion:
    """Tests for module version."""

    def test_version_exists(self):
        """Test that __version__ exists."""
        assert hasattr(justcode, "__version__")
        assert isinstance(justcode.__version__, str)
        assert justcode.__version__ == "0.3.0"


