"""
Comprehensive tests based on our original test suite.
"""

import pytest
from deep_toon import DeepToonEncoder, DeepToonDecoder


class TestComprehensiveScenarios:
    """Test comprehensive real-world scenarios."""
    
    def test_flat_object_array(self):
        """Test flat object array compression."""
        data = {
            'items': [
                {'id': 1, 'name': 'Alice', 'age': 25, 'active': True},
                {'id': 2, 'name': 'Bob', 'age': 30, 'active': False},
                {'id': 3, 'name': 'Charlie', 'age': 35, 'active': True}
            ]
        }
        
        encoder = DeepToonEncoder()
        decoder = DeepToonDecoder()
        
        encoded = encoder.encode(data)
        decoded = decoder.decode(encoded)
        
        assert decoded == data
        # Should achieve good compression
        import json
        original_size = len(json.dumps(data))
        toon2_size = len(encoded)
        assert toon2_size < original_size

    def test_single_level_nesting(self):
        """Test single level nested objects."""
        data = {
            'users': [
                {
                    'id': 1,
                    'profile': {'name': 'Alice', 'email': 'alice@test.com'},
                    'settings': {'theme': 'dark', 'notifications': True}
                },
                {
                    'id': 2, 
                    'profile': {'name': 'Bob', 'email': 'bob@test.com'},
                    'settings': {'theme': 'light', 'notifications': False}
                }
            ]
        }
        
        encoder = DeepToonEncoder()
        decoder = DeepToonDecoder()
        
        encoded = encoder.encode(data)
        decoded = decoder.decode(encoded)
        
        assert decoded == data

    def test_deep_nesting(self):
        """Test deep nesting structures."""
        data = {
            'company': [
                {
                    'id': 1,
                    'name': 'TechCorp',
                    'location': {
                        'address': {
                            'street': '123 Tech St',
                            'city': 'San Francisco',
                            'coordinates': {
                                'lat': 37.7749,
                                'lng': -122.4194
                            }
                        },
                        'timezone': 'PST'
                    }
                }
            ]
        }
        
        encoder = DeepToonEncoder()
        decoder = DeepToonDecoder()
        
        encoded = encoder.encode(data)
        decoded = decoder.decode(encoded)
        
        assert decoded == data

    def test_mixed_data_types(self):
        """Test mixed data types including arrays."""
        data = {
            'records': [
                {
                    'id': 1,
                    'timestamp': '2024-01-01T10:00:00Z',
                    'value': 42.5,
                    'tags': ['urgent', 'customer'],
                    'metadata': {
                        'source': 'api',
                        'version': 1.2,
                        'validated': True,
                        'errors': None
                    }
                },
                {
                    'id': 2,
                    'timestamp': '2024-01-01T11:00:00Z', 
                    'value': -15.8,
                    'tags': ['normal', 'internal'],
                    'metadata': {
                        'source': 'batch',
                        'version': 1.1,
                        'validated': False,
                        'errors': ['missing_field']
                    }
                }
            ]
        }
        
        encoder = DeepToonEncoder()
        decoder = DeepToonDecoder()
        
        encoded = encoder.encode(data)
        decoded = decoder.decode(encoded)
        
        assert decoded == data

    def test_sparse_data(self):
        """Test sparse data with many nulls."""
        data = {
            'entries': [
                {
                    'id': 1,
                    'name': 'Complete',
                    'email': 'complete@test.com',
                    'phone': '555-1234',
                    'address': {'street': '123 Main', 'city': 'NYC'}
                },
                {
                    'id': 2,
                    'name': 'Partial',
                    'email': None,
                    'phone': None,
                    'address': {'street': None, 'city': 'LA'}
                },
                {
                    'id': 3,
                    'name': 'Minimal', 
                    'email': None,
                    'phone': None,
                    'address': None
                }
            ]
        }
        
        encoder = DeepToonEncoder()
        decoder = DeepToonDecoder()
        
        encoded = encoder.encode(data)
        decoded = decoder.decode(encoded)
        
        assert decoded == data

    def test_array_of_primitives(self):
        """Test arrays of primitive types."""
        data = {
            'numbers': [1, 2, 3, 4, 5],
            'strings': ['apple', 'banana', 'cherry'],
            'booleans': [True, False, True],
            'mixed': [1, 'text', True, None, 3.14]
        }
        
        encoder = DeepToonEncoder()
        decoder = DeepToonDecoder()
        
        encoded = encoder.encode(data)
        decoded = decoder.decode(encoded)
        
        assert decoded == data

    def test_large_object_count(self):
        """Test large number of objects."""
        data = {
            'items': [
                {
                    'id': i,
                    'name': f'Item {i}',
                    'category': 'electronics' if i % 3 == 0 else 'books',
                    'price': round(10.0 + i * 1.5, 2),
                    'in_stock': i % 2 == 0,
                    'details': {
                        'weight': round(i * 0.1, 2),
                        'dimensions': {'l': i, 'w': i+1, 'h': i+2}
                    }
                }
                for i in range(1, 21)  # 20 items
            ]
        }
        
        encoder = DeepToonEncoder()
        decoder = DeepToonDecoder()
        
        encoded = encoder.encode(data)
        decoded = decoder.decode(encoded)
        
        assert decoded == data
        
        # Should achieve significant compression on large datasets
        import json
        original_size = len(json.dumps(data))
        toon2_size = len(encoded)
        compression_ratio = (original_size - toon2_size) / original_size
        assert compression_ratio > 0.3  # Expect at least 30% compression

    def test_deeply_nested_arrays(self):
        """Test deeply nested array structures."""
        data = {
            'matrix': [
                [
                    {'x': 0, 'y': 0, 'value': 1.0},
                    {'x': 0, 'y': 1, 'value': 0.5}
                ],
                [
                    {'x': 1, 'y': 0, 'value': 0.3},
                    {'x': 1, 'y': 1, 'value': 0.8}
                ]
            ]
        }
        
        encoder = DeepToonEncoder()
        decoder = DeepToonDecoder()
        
        encoded = encoder.encode(data)
        decoded = decoder.decode(encoded)
        
        assert decoded == data

    def test_ecommerce_order(self):
        """Test complex e-commerce order structure."""
        data = {
            'orders': [
                {
                    'id': 'ORD-001',
                    'customer': {
                        'id': 'CUST-123',
                        'name': 'John Doe',
                        'email': 'john@example.com',
                        'address': {
                            'billing': {
                                'street': '123 Main St',
                                'city': 'Springfield',
                                'state': 'IL',
                                'zip': '62701',
                                'country': 'US'
                            },
                            'shipping': {
                                'street': '456 Oak Ave',
                                'city': 'Springfield', 
                                'state': 'IL',
                                'zip': '62701',
                                'country': 'US'
                            }
                        }
                    },
                    'items': [
                        {
                            'sku': 'BOOK-001',
                            'name': 'Python Programming',
                            'price': 29.99,
                            'quantity': 2
                        }
                    ],
                    'payment': {
                        'method': 'credit_card',
                        'amount': {
                            'subtotal': 59.98,
                            'tax': 4.80,
                            'total': 64.78
                        }
                    }
                }
            ]
        }
        
        encoder = DeepToonEncoder()
        decoder = DeepToonDecoder()
        
        encoded = encoder.encode(data)
        decoded = decoder.decode(encoded)
        
        assert decoded == data


@pytest.mark.slow
class TestPerformance:
    """Performance-related tests."""
    
    def test_compression_ratio(self):
        """Test that compression ratios meet expectations."""
        # Test data with good compression potential
        data = {
            'users': [
                {
                    'id': i,
                    'name': f'User{i}',
                    'email': f'user{i}@test.com',
                    'profile': {
                        'age': 20 + (i % 50),
                        'location': 'City' + str(i % 10),
                        'preferences': {
                            'theme': 'dark' if i % 2 else 'light',
                            'notifications': bool(i % 2)
                        }
                    }
                }
                for i in range(100)
            ]
        }
        
        encoder = DeepToonEncoder()
        decoder = DeepToonDecoder()
        
        import json
        original_json = json.dumps(data)
        encoded_toon2 = encoder.encode(data)
        decoded_data = decoder.decode(encoded_toon2)
        
        # Verify roundtrip
        assert decoded_data == data
        
        # Check compression
        original_size = len(original_json)
        toon2_size = len(encoded_toon2)
        compression_ratio = (original_size - toon2_size) / original_size
        
        # Should achieve significant compression
        assert compression_ratio > 0.2  # At least 20% compression
        assert toon2_size < original_size