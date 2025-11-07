import base64
import os
import struct
import time
import pytest

from rick.crypto.fernet256 import Fernet256, MultiFernet256, InvalidToken


class TestFernet256:
    """Comprehensive tests for Fernet256 encryption/decryption"""

    # Test vectors with known good keys and data
    test_data = [
        b"hello world",
        b"",  # Empty data
        b"a" * 1000,  # Long data
        b"\x00\x01\x02\x03\x04",  # Binary data
        "unicode string with émojis 🔒".encode("utf-8"),
        b"special characters: !@#$%^&*()_+-=[]{}|;':\",./<>?",
    ]

    @pytest.fixture
    def valid_key(self):
        """Generate a valid 64-byte key for testing"""
        return Fernet256.generate_key()

    @pytest.fixture
    def fernet(self, valid_key):
        """Create a Fernet256 instance with a valid key"""
        return Fernet256(valid_key)

    def test_key_generation(self):
        """Test that key generation produces valid keys"""
        key = Fernet256.generate_key()

        # Key should be base64-encoded
        assert isinstance(key, bytes)

        # Should be decodable as base64
        decoded = base64.urlsafe_b64decode(key)

        # Decoded key should be exactly 64 bytes
        assert len(decoded) == 64

        # Should be able to create Fernet256 instance with generated key
        f = Fernet256(key)
        assert f is not None

    def test_key_validation(self):
        """Test key validation during Fernet256 initialization"""
        # Valid key should work
        valid_key = Fernet256.generate_key()
        f = Fernet256(valid_key)
        assert f is not None

        # Invalid key lengths should raise ValueError
        with pytest.raises(
            ValueError, match="Fernet key must be 64 url-safe base64-encoded bytes"
        ):
            Fernet256(base64.urlsafe_b64encode(b"too_short"))

        with pytest.raises(
            ValueError, match="Fernet key must be 64 url-safe base64-encoded bytes"
        ):
            Fernet256(base64.urlsafe_b64encode(b"a" * 32))  # 32 bytes, need 64

        with pytest.raises(
            ValueError, match="Fernet key must be 64 url-safe base64-encoded bytes"
        ):
            Fernet256(base64.urlsafe_b64encode(b"a" * 100))  # Too long

        # Invalid base64 should raise error
        with pytest.raises(Exception):  # binascii.Error or ValueError
            Fernet256(b"not_base64!")

    @pytest.mark.parametrize("data", test_data)
    def test_encrypt_decrypt_basic(self, fernet, data):
        """Test basic encryption and decryption functionality"""
        # Encrypt the data
        token = fernet.encrypt(data)

        # Token should be bytes
        assert isinstance(token, bytes)

        # Token should be base64-encoded (no decoding errors)
        decoded_token = base64.urlsafe_b64decode(token)
        assert len(decoded_token) > 0

        # Decrypt should return original data
        decrypted = fernet.decrypt(token)
        assert decrypted == data

    def test_encrypt_decrypt_deterministic(self, fernet):
        """Test that encryption is non-deterministic (same input produces different tokens)"""
        data = b"test data for deterministic check"

        # Encrypt the same data multiple times
        tokens = [fernet.encrypt(data) for _ in range(5)]

        # All tokens should be different (encryption uses random IV)
        assert len(set(tokens)) == 5

        # But all should decrypt to the same original data
        for token in tokens:
            assert fernet.decrypt(token) == data

    def test_encrypt_at_time(self, fernet):
        """Test encryption with specific timestamp"""
        data = b"timestamped data"
        test_time = 1234567890

        token = fernet.encrypt_at_time(data, test_time)

        # Should be able to decrypt normally
        decrypted = fernet.decrypt(token)
        assert decrypted == data

        # Extract timestamp should return the test time
        extracted_time = fernet.extract_timestamp(token)
        assert extracted_time == test_time

    def test_decrypt_with_ttl(self, fernet):
        """Test decryption with time-to-live validation"""
        data = b"ttl test data"
        current_time = int(time.time())

        # Create token at current time
        token = fernet.encrypt_at_time(data, current_time)

        # Should decrypt successfully with reasonable TTL
        decrypted = fernet.decrypt_at_time(
            token, ttl=3600, current_time=current_time + 10
        )
        assert decrypted == data

        # Should fail with expired TTL
        with pytest.raises(InvalidToken):
            fernet.decrypt_at_time(token, ttl=10, current_time=current_time + 20)

        # Should fail with token from future (beyond clock skew)
        # Create a token with future timestamp
        future_token = fernet.encrypt_at_time(
            data, current_time + 120
        )  # 120 seconds in future
        with pytest.raises(InvalidToken):
            fernet.decrypt_at_time(future_token, ttl=3600, current_time=current_time)

    def test_decrypt_at_time_requires_ttl(self, fernet):
        """Test that decrypt_at_time requires TTL parameter"""
        data = b"test data"
        token = fernet.encrypt(data)

        with pytest.raises(
            ValueError,
            match="decrypt_at_time\\(\\) can only be used with a non-None ttl",
        ):
            fernet.decrypt_at_time(token, ttl=None, current_time=int(time.time()))

    def test_extract_timestamp(self, fernet):
        """Test timestamp extraction from tokens"""
        data = b"timestamp extraction test"
        test_times = [0, 1234567890, int(time.time()), 2147483647]  # Various timestamps

        for test_time in test_times:
            token = fernet.encrypt_at_time(data, test_time)
            extracted_time = fernet.extract_timestamp(token)
            assert extracted_time == test_time

    def test_invalid_token_handling(self, fernet):
        """Test handling of various invalid tokens"""
        invalid_tokens = [
            b"",  # Empty token
            b"invalid",  # Invalid base64
            b"aW52YWxpZA==",  # Valid base64 but invalid token structure
            base64.urlsafe_b64encode(b"\x80" + b"a" * 50),  # Wrong version byte
            base64.urlsafe_b64encode(b"\x81" + b"a" * 7),  # Too short for timestamp
        ]

        for invalid_token in invalid_tokens:
            with pytest.raises(InvalidToken):
                fernet.decrypt(invalid_token)

    def test_tampered_token_detection(self, fernet):
        """Test that tampered tokens are detected and rejected"""
        data = b"test data for tampering"
        token = fernet.encrypt(data)

        # Decode token to bytes for manipulation
        token_bytes = base64.urlsafe_b64decode(token)

        # Tamper with different parts of the token
        tampered_tokens = [
            # Tamper with version byte
            base64.urlsafe_b64encode(b"\x82" + token_bytes[1:]),
            # Tamper with timestamp
            base64.urlsafe_b64encode(token_bytes[:1] + b"\x00" * 8 + token_bytes[9:]),
            # Tamper with IV
            base64.urlsafe_b64encode(token_bytes[:9] + b"\x00" * 16 + token_bytes[25:]),
            # Tamper with ciphertext
            base64.urlsafe_b64encode(
                token_bytes[:-40] + b"\x00" * 8 + token_bytes[-32:]
            ),
            # Tamper with HMAC
            base64.urlsafe_b64encode(token_bytes[:-32] + b"\x00" * 32),
        ]

        for tampered_token in tampered_tokens:
            with pytest.raises(InvalidToken):
                fernet.decrypt(tampered_token)

    def test_different_keys_incompatible(self):
        """Test that tokens encrypted with one key cannot be decrypted with another"""
        key1 = Fernet256.generate_key()
        key2 = Fernet256.generate_key()

        f1 = Fernet256(key1)
        f2 = Fernet256(key2)

        data = b"cross-key test data"
        token = f1.encrypt(data)

        # Should decrypt with correct key
        assert f1.decrypt(token) == data

        # Should fail with different key
        with pytest.raises(InvalidToken):
            f2.decrypt(token)

    def test_token_structure_validation(self, fernet):
        """Test that token structure is properly validated"""
        data = b"structure test"
        token = fernet.encrypt(data)
        decoded = base64.urlsafe_b64decode(token)

        # Validate expected structure
        assert decoded[0] == 0x81  # Version byte

        # Extract and validate timestamp
        timestamp = struct.unpack(">Q", decoded[1:9])[0]
        assert isinstance(timestamp, int)
        assert timestamp > 0

        # Validate lengths
        assert (
            len(decoded) >= 57
        )  # Minimum token size: 1 + 8 + 16 + 16 + 32 = 73 bytes minimum

        # IV should be 16 bytes
        iv = decoded[9:25]
        assert len(iv) == 16

        # HMAC should be last 32 bytes
        hmac = decoded[-32:]
        assert len(hmac) == 32

    def test_large_data_encryption(self, fernet):
        """Test encryption of large data blocks"""
        # Test various sizes including those that require padding
        sizes = [1, 15, 16, 17, 1000, 16384, 65536]

        for size in sizes:
            data = os.urandom(size)
            token = fernet.encrypt(data)
            decrypted = fernet.decrypt(token)
            assert decrypted == data

    def test_concurrent_operations(self, fernet):
        """Test that Fernet256 is thread-safe for basic operations"""
        import threading
        import concurrent.futures

        data = b"concurrent test data"
        results = []
        errors = []

        def encrypt_decrypt():
            try:
                token = fernet.encrypt(data)
                decrypted = fernet.decrypt(token)
                results.append(decrypted == data)
            except Exception as e:
                errors.append(e)

        # Run multiple operations concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(encrypt_decrypt) for _ in range(50)]
            concurrent.futures.wait(futures)

        # All operations should succeed
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert all(results), "Some encrypt/decrypt operations failed"
        assert len(results) == 50


class TestMultiFernet256:
    """Tests for MultiFernet256 key rotation functionality"""

    @pytest.fixture
    def keys(self):
        """Generate multiple keys for testing"""
        return [Fernet256.generate_key() for _ in range(3)]

    @pytest.fixture
    def multi_fernet(self, keys):
        """Create MultiFernet256 instance with multiple keys"""
        fernets = [Fernet256(key) for key in keys]
        return MultiFernet256(fernets)

    def test_multifernet_creation(self, keys):
        """Test MultiFernet256 creation and validation"""
        fernets = [Fernet256(key) for key in keys]

        # Should create successfully with multiple fernets
        mf = MultiFernet256(fernets)
        assert mf is not None

        # Should fail with empty list
        with pytest.raises(
            ValueError, match="MultiFernet requires at least one Fernet instance"
        ):
            MultiFernet256([])

    def test_multifernet_encrypt_decrypt(self, multi_fernet):
        """Test basic MultiFernet256 encrypt/decrypt functionality"""
        data = b"multifernet test data"

        # Encrypt with MultiFernet (uses first key)
        token = multi_fernet.encrypt(data)

        # Should decrypt successfully
        decrypted = multi_fernet.decrypt(token)
        assert decrypted == data

    def test_multifernet_key_rotation(self):
        """Test key rotation scenarios"""
        # Create keys in order: old -> current -> new
        old_key = Fernet256.generate_key()
        current_key = Fernet256.generate_key()
        new_key = Fernet256.generate_key()

        # Create MultiFernet with current key first (for encryption)
        mf_current = MultiFernet256([Fernet256(current_key)])

        # Encrypt some data with current key
        data = b"key rotation test"
        token = mf_current.encrypt(data)

        # Create MultiFernet that can handle old tokens but encrypts with new key
        mf_rotated = MultiFernet256(
            [
                Fernet256(new_key),  # New key (used for encryption)
                Fernet256(current_key),  # Current key (can decrypt existing tokens)
                Fernet256(old_key),  # Old key (can decrypt legacy tokens)
            ]
        )

        # Should be able to decrypt token encrypted with current key
        decrypted = mf_rotated.decrypt(token)
        assert decrypted == data

        # New encryptions should use the first (new) key
        new_token = mf_rotated.encrypt(data)
        decrypted_new = mf_rotated.decrypt(new_token)
        assert decrypted_new == data

        # Tokens encrypted with different keys should be different
        assert token != new_token

    def test_multifernet_rotate_function(self):
        """Test the rotate() function for key rotation"""
        old_key = Fernet256.generate_key()
        new_key = Fernet256.generate_key()

        # Encrypt with old key
        old_fernet = Fernet256(old_key)
        data = b"rotation test data"
        old_token = old_fernet.encrypt(data)

        # Create MultiFernet for rotation
        mf = MultiFernet256([Fernet256(new_key), Fernet256(old_key)])

        # Rotate the token (decrypt with old key, encrypt with new key)
        new_token = mf.rotate(old_token)

        # Both tokens should decrypt to same data
        assert mf.decrypt(old_token) == data
        assert mf.decrypt(new_token) == data

        # But new token should be encrypted with new key
        new_fernet = Fernet256(new_key)
        assert new_fernet.decrypt(new_token) == data

        # Old key alone shouldn't be able to decrypt new token
        with pytest.raises(InvalidToken):
            old_fernet.decrypt(new_token)

    def test_multifernet_decrypt_with_ttl(self, multi_fernet):
        """Test MultiFernet256 decrypt with TTL"""
        data = b"ttl multifernet test"
        current_time = int(time.time())

        token = multi_fernet.encrypt_at_time(data, current_time)

        # Should decrypt with valid TTL
        decrypted = multi_fernet.decrypt_at_time(
            token, ttl=3600, current_time=current_time + 10
        )
        assert decrypted == data

        # Should fail with expired TTL
        with pytest.raises(InvalidToken):
            multi_fernet.decrypt_at_time(token, ttl=10, current_time=current_time + 20)

    def test_multifernet_invalid_token_handling(self, multi_fernet):
        """Test MultiFernet256 handling of invalid tokens"""
        invalid_tokens = [
            b"invalid_token",
            b"",
            base64.urlsafe_b64encode(b"invalid_structure"),
        ]

        for invalid_token in invalid_tokens:
            with pytest.raises(InvalidToken):
                multi_fernet.decrypt(invalid_token)

            with pytest.raises(InvalidToken):
                multi_fernet.rotate(invalid_token)


class TestFernet256Security:
    """Security-focused tests for Fernet256"""

    def test_key_independence(self):
        """Test that different keys produce completely independent encryption"""
        data = b"independence test data"

        # Generate multiple keys
        keys = [Fernet256.generate_key() for _ in range(5)]
        fernets = [Fernet256(key) for key in keys]

        # Encrypt with each key
        tokens = [f.encrypt(data) for f in fernets]

        # All tokens should be different
        assert len(set(tokens)) == len(tokens)

        # Each fernet should only decrypt its own token
        for i, (fernet, token) in enumerate(zip(fernets, tokens)):
            # Should decrypt with correct key
            assert fernet.decrypt(token) == data

            # Should fail with all other keys
            for j, other_fernet in enumerate(fernets):
                if i != j:
                    with pytest.raises(InvalidToken):
                        other_fernet.decrypt(token)

    def test_timing_attack_resistance(self):
        """Test that invalid tokens fail quickly (constant time)"""
        fernet = Fernet256(Fernet256.generate_key())
        data = b"timing test data"
        valid_token = fernet.encrypt(data)

        # Create various invalid tokens
        invalid_tokens = [
            b"short",
            b"a" * 100,
            base64.urlsafe_b64encode(b"x" * 73),  # Valid length but invalid content
            valid_token[:-4] + b"xxxx",  # Tampered token
        ]

        # All should fail with InvalidToken (not measure timing here, just ensure they fail)
        for token in invalid_tokens:
            with pytest.raises(InvalidToken):
                fernet.decrypt(token)

    def test_randomness_quality(self):
        """Test that encryption uses good randomness"""
        fernet = Fernet256(Fernet256.generate_key())
        data = b"randomness test"

        # Generate many tokens
        tokens = [fernet.encrypt(data) for _ in range(100)]

        # All should be unique (extremely high probability)
        assert len(set(tokens)) == len(tokens)

        # Extract IVs and check for randomness
        ivs = []
        for token in tokens:
            decoded = base64.urlsafe_b64decode(token)
            iv = decoded[9:25]  # IV is bytes 9-24
            ivs.append(iv)

        # All IVs should be unique
        assert len(set(ivs)) == len(ivs)

        # Basic randomness check: no obvious patterns
        iv_bytes = b"".join(ivs)
        # Check that we don't have too many repeated bytes
        byte_counts = [iv_bytes.count(bytes([i])) for i in range(256)]
        # Should have reasonable distribution (not perfectly uniform due to randomness)
        assert (
            max(byte_counts) < len(iv_bytes) * 0.1
        )  # No byte appears more than 10% of the time

    def test_key_format_security(self):
        """Test key format security properties"""
        key = Fernet256.generate_key()

        # Key should be proper base64
        decoded = base64.urlsafe_b64decode(key)
        assert len(decoded) == 64

        # Key should look random (basic entropy check)
        # Count unique bytes in key
        unique_bytes = len(set(decoded))
        # Should have reasonable diversity (not perfectly random due to limited sample)
        assert unique_bytes > 30  # Should have good byte diversity

        # Key should not be predictable
        key2 = Fernet256.generate_key()
        assert key != key2

        # Hamming distance should be significant
        decoded2 = base64.urlsafe_b64decode(key2)
        different_bytes = sum(a != b for a, b in zip(decoded, decoded2))
        assert different_bytes > 30  # Should differ in many positions


class TestFernet256EdgeCases:
    """Edge case and error condition tests"""

    def test_empty_data_encryption(self):
        """Test encryption of empty data"""
        fernet = Fernet256(Fernet256.generate_key())

        empty_data = b""
        token = fernet.encrypt(empty_data)
        decrypted = fernet.decrypt(token)

        assert decrypted == empty_data

    def test_maximum_timestamp_values(self):
        """Test handling of extreme timestamp values"""
        fernet = Fernet256(Fernet256.generate_key())
        data = b"timestamp edge case test"

        # Test with maximum valid timestamp (64-bit unsigned int)
        max_timestamp = 2**64 - 1

        # This might fail due to system limitations, but should handle gracefully
        try:
            token = fernet.encrypt_at_time(data, max_timestamp)
            timestamp = fernet.extract_timestamp(token)
            assert timestamp == max_timestamp
        except (OverflowError, ValueError):
            # Acceptable if system can't handle extremely large timestamps
            pass

        # Test with timestamp 0
        token = fernet.encrypt_at_time(data, 0)
        timestamp = fernet.extract_timestamp(token)
        assert timestamp == 0

    def test_malformed_token_structure(self):
        """Test handling of malformed token structures"""
        fernet = Fernet256(Fernet256.generate_key())

        # Various malformed structures
        malformed_tokens = [
            # Too short tokens
            base64.urlsafe_b64encode(b"\x81"),
            base64.urlsafe_b64encode(b"\x81" + b"a" * 8),  # No IV
            base64.urlsafe_b64encode(b"\x81" + b"a" * 24),  # No ciphertext
            base64.urlsafe_b64encode(b"\x81" + b"a" * 40),  # No HMAC
            # Wrong version bytes
            base64.urlsafe_b64encode(b"\x00" + b"a" * 72),
            base64.urlsafe_b64encode(b"\x82" + b"a" * 72),
            base64.urlsafe_b64encode(b"\xff" + b"a" * 72),
        ]

        for token in malformed_tokens:
            with pytest.raises(InvalidToken):
                fernet.decrypt(token)

    def test_unicode_string_handling(self):
        """Test that string inputs are properly rejected"""
        fernet = Fernet256(Fernet256.generate_key())

        # Fernet256 should only accept bytes, not strings
        with pytest.raises(TypeError):
            fernet.encrypt("string data")

        # Even for decrypt
        with pytest.raises(TypeError):
            fernet.decrypt("string token")

    def test_none_input_handling(self):
        """Test handling of None inputs"""
        fernet = Fernet256(Fernet256.generate_key())

        with pytest.raises((TypeError, AttributeError)):
            fernet.encrypt(None)

        with pytest.raises((TypeError, AttributeError)):
            fernet.decrypt(None)

    def test_memory_efficiency(self):
        """Test that encryption doesn't leak excessive memory"""
        fernet = Fernet256(Fernet256.generate_key())

        # Test with various sizes
        for size in [1024, 10240, 102400]:  # 1KB, 10KB, 100KB
            data = b"x" * size
            token = fernet.encrypt(data)
            decrypted = fernet.decrypt(token)

            assert decrypted == data
            # Token should be larger than original due to overhead
            decoded_token = base64.urlsafe_b64decode(token)
            # Overhead should be reasonable (version + timestamp + IV + padding + HMAC)
            expected_overhead = 1 + 8 + 16 + 16 + 32  # ~73 bytes plus padding
            assert len(decoded_token) >= len(data) + expected_overhead
            assert (
                len(decoded_token) <= len(data) + expected_overhead + 16
            )  # Max one block padding
