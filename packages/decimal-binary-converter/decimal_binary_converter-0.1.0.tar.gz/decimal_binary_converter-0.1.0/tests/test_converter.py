import pytest
from dec_bi_conv.converter import decimal_to_binary, binary_to_decimal

def test_decimal_to_binary():
    assert decimal_to_binary(0) == '0'
    assert decimal_to_binary(10) == '1010'
    assert decimal_to_binary(255) == '11111111'

def test_decimal_to_binary_invalid():
    try:
        decimal_to_binary(-5)
    except ValueError:
        assert True
    else:
        assert False
    try:
        decimal_to_binary('abc')
    except ValueError:
        assert True
    else:
        assert False

def test_binary_to_decimal():
    assert binary_to_decimal('0') == 0
    assert binary_to_decimal('1010') == 10
    assert binary_to_decimal('11111111') == 255

def test_binary_to_decimal_invalid():
    try:
        binary_to_decimal('102')
    except ValueError:
        assert True
    else:
        assert False
    try:
        binary_to_decimal('abc')
    except ValueError:
        assert True
    else:
        assert False
