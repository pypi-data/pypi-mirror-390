import pytest
from madcubapy.operations.maps import measure_noise


def test_invalid_object_type_measure_noise():
    with pytest.raises(TypeError):
        measure_noise("string")
    with pytest.raises(TypeError):
        measure_noise(999)