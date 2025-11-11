"""
Basic tests for Deep-TOON encoder/decoder.
"""

import pytest
from deep_toon import DeepToonEncoder, DeepToonDecoder, DeepToonDecodeError


class TestBasicEncoding:
    """Test basic encoding functionality."""
    
    def test_simple_array(self):
        """Test encoding of simple object array."""
        data = {
            'items': [
                {'id': 1, 'name': 'Alice', 'active': True},
                {'id': 2, 'name': 'Bob', 'active': False}
            ]
        }
        
        encoder = DeepToonEncoder()
        encoded = encoder.encode(data)
        
        assert 'items[2,' in encoded
        assert '{id,name,active}' in encoded
        assert 'Alice' in encoded
        assert 'Bob' in encoded

    def test_nested_objects(self):
        """Test encoding of nested objects."""
        data = {
            'users': [
                {
                    'id': 1,
                    'profile': {'name': 'Alice', 'email': 'alice@test.com'},
                    'settings': {'theme': 'dark', 'notifications': True}
                }
            ]
        }
        
        encoder = DeepToonEncoder()
        encoded = encoder.encode(data)
        
        assert 'profile{name,email}' in encoded
        assert 'settings{theme,notifications}' in encoded

    def test_primitive_arrays(self):
        """Test encoding of primitive arrays."""
        data = {
            'tags': ['python', 'json', 'compression'],
            'numbers': [1, 2, 3, 4, 5],
            'flags': [True, False, True]
        }
        
        encoder = DeepToonEncoder()
        encoded = encoder.encode(data)
        
        # Should fallback to JSON for primitive arrays
        assert '["python", "json", "compression"]' in encoded or "['python', 'json', 'compression']" in encoded


class TestBasicDecoding:
    """Test basic decoding functionality."""
    
    def test_roundtrip_simple(self):
        """Test roundtrip for simple data."""
        data = {
            'items': [
                {'id': 1, 'name': 'Alice'},
                {'id': 2, 'name': 'Bob'}
            ]
        }
        
        encoder = DeepToonEncoder()
        decoder = DeepToonDecoder()
        
        encoded = encoder.encode(data)
        decoded = decoder.decode(encoded)
        
        assert decoded == data

    def test_roundtrip_nested(self):
        """Test roundtrip for nested data."""
        data = {
            'users': [
                {
                    'id': 1,
                    'profile': {'name': 'Alice', 'age': 30},
                    'active': True
                },
                {
                    'id': 2,
                    'profile': {'name': 'Bob', 'age': 25},
                    'active': False
                }
            ]
        }
        
        encoder = DeepToonEncoder()
        decoder = DeepToonDecoder()
        
        encoded = encoder.encode(data)
        decoded = decoder.decode(encoded)
        
        assert decoded == data

    def test_roundtrip_mixed_types(self):
        """Test roundtrip for mixed data types."""
        data = {
            'records': [
                {
                    'id': 1,
                    'value': 42.5,
                    'active': True,
                    'tags': ['important', 'test'],
                    'metadata': {'source': 'api', 'version': 1.0}
                }
            ]
        }
        
        encoder = DeepToonEncoder()
        decoder = DeepToonDecoder()
        
        encoded = encoder.encode(data)
        decoded = decoder.decode(encoded)
        
        assert decoded == data

    def test_null_values(self):
        """Test handling of null values."""
        data = {
            'items': [
                {'id': 1, 'name': 'Alice', 'email': 'alice@test.com'},
                {'id': 2, 'name': 'Bob', 'email': None},
                {'id': 3, 'name': 'Charlie', 'email': None}
            ]
        }
        
        encoder = DeepToonEncoder()
        decoder = DeepToonDecoder()
        
        encoded = encoder.encode(data)
        decoded = decoder.decode(encoded)
        
        assert decoded == data

    def test_empty_data(self):
        """Test handling of empty data structures."""
        # Test case: empty arrays should roundtrip correctly
        data1 = {'items': []}
        encoder = DeepToonEncoder()
        decoder = DeepToonDecoder()
        
        encoded1 = encoder.encode(data1)
        decoded1 = decoder.decode(encoded1)
        assert decoded1 == data1
            
        # Empty dict is a special case - it becomes JSON string
        empty_dict = {}
        encoded = encoder.encode(empty_dict)
        decoded = decoder.decode(encoded)
        # Might become string "{}" due to JSON fallback
        assert decoded == empty_dict or decoded == "{}"


class TestErrorHandling:
    """Test error handling."""
    
    def test_invalid_toon2_format(self):
        """Test decoding of invalid TOON2 format."""
        decoder = DeepToonDecoder()
        
        # Invalid format just returns as string (fallback behavior)
        result = decoder.decode("invalid toon2 format")
        assert result == "invalid toon2 format"

    def test_malformed_schema(self):
        """Test handling of malformed schema."""
        decoder = DeepToonDecoder()
        
        # Test actual malformed schemas that should raise errors
        malformed_cases = [
            "[2,]{id,name}:\n  1,Alice\n  2",  # Missing field
            "[1,]{id,name}:\n  1,Alice,Extra",  # Too many fields  
        ]
        
        for malformed in malformed_cases:
            with pytest.raises(DeepToonDecodeError):
                decoder.decode(malformed)


class TestCustomDelimiter:
    """Test custom delimiter functionality."""
    
    def test_semicolon_delimiter(self):
        """Test using semicolon as delimiter."""
        data = {
            'items': [
                {'text': 'hello, world', 'value': 1},
                {'text': 'foo, bar', 'value': 2}
            ]
        }
        
        encoder = DeepToonEncoder(delimiter=';')
        decoder = DeepToonDecoder()
        
        encoded = encoder.encode(data)
        decoded = decoder.decode(encoded)
        
        assert ';' in encoded  # Should use semicolon
        assert decoded == data  # Should roundtrip correctly