from madcubapy.visualization import get_input
import pytest

def test_invalid_object_type_get_input():
    with pytest.raises(TypeError):
        get_input("string")
    with pytest.raises(TypeError):
        get_input(999)