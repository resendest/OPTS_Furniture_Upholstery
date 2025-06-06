# backend/tests/test_order_processing.py

import pytest
from backend.order_processing import build_item_code

def test_build_item_code_piece():
    assert build_item_code("1", "piece") == "0001"
    assert build_item_code("42", "piece") == "0042"
    with pytest.raises(ValueError):
        build_item_code("ABC", "piece")

def test_build_item_code_fabric():
    assert build_item_code("01", "fabric") == "FAB01"
    assert build_item_code("FAB12", "fabric") == "FAB12"
    with pytest.raises(ValueError):
        build_item_code("FAB", "fabric")  # too short after "FAB"
