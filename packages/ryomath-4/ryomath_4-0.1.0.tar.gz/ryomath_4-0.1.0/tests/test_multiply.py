from ryomath_4.multiply import multiply

def test_multiply_ints():
    assert multiply(2, 3) == 6

def test_multiply_floats():
    assert abs(multiply(2.0, 0.1) - 0.2) < 1e-8

def test_multiply_zero():
    assert multiply(10, 0) == 0
