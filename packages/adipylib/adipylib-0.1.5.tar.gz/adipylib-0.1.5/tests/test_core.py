# tests/test_core.py

import pytest
from adipylib import hello_adipylib, add_numbers

def test_hello_function():
    assert hello_adipylib() == "Hello from adipylib!"

def test_add_function():
    assert add_numbers(2, 3) == 5
    assert add_numbers(-1, 1) == 0