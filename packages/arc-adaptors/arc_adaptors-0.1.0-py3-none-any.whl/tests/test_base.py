"""
Tests for the base adaptor class
"""

import pytest
from arc_adaptors.base import BaseAdaptor


class TestBaseAdaptor:
    """Tests for the BaseAdaptor class"""
    
    def test_base_adaptor_is_abstract(self):
        """Test that BaseAdaptor cannot be instantiated directly"""
        with pytest.raises(TypeError):
            BaseAdaptor()
