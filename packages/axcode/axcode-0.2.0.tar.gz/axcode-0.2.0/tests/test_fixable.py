"""
Fixable Issues Test Suite - Tests auto-fix and preview features
Tests: 15+ fixable issues to demonstrate fix preview functionality
"""


# ==================== FIXABLE: AUGMENTED ASSIGNMENT OPERATORS ====================

def update_counter():
    count = 0
    count = count + 1  # FIX: count += 1
    count = count + 5  # FIX: count += 5
    return count

def calculate_totals():
    total = 100
    total = total - 10  # FIX: total -= 10
    total = total * 2   # FIX: total *= 2
    total = total / 4   # FIX: total /= 4
    return total

def accumulator_pattern():
    result = 1
    for i in range(10):
        result = result * i  # FIX: result *= i
    return result


# ==================== FIXABLE: NAMING CONVENTIONS ====================

def BadFunctionName():  # FIX: bad_function_name()
    return True

def AnotherBadName():  # FIX: another_bad_name()
    pass

class bad_class_name:  # FIX: BadClassName
    def AnotherMethod(self):  # FIX: another_method
        pass

MY_CONST = 42  # Correct (constants are uppercase)
myVariable = 10  # FIX: my_variable (snake_case for variables)


# ==================== FIXABLE: MISSING DOCSTRINGS ====================

def complex_calculation(x, y):  # FIX: Add docstring
    return x * y + x / y

class DataProcessor:  # FIX: Add docstring
    def process(self, data):  # FIX: Add docstring
        return data.strip().lower()


# ==================== FIXABLE: TYPE HINTS ====================

def add_numbers(a, b):  # FIX: Add type hints
    return a + b

def process_list(items):  # FIX: Add type hints
    return [item.upper() for item in items]

def get_user(user_id):  # FIX: Add type hints and return type
    return database.query(user_id)


# ==================== FIXABLE: REDUNDANT ELSE ====================

def check_value(x):
    if x > 10:
        return "high"
    else:  # FIX: Remove redundant else
        return "low"

def validate_input(value):
    if not value:
        return False
    else:  # FIX: Remove redundant else
        return True


# ==================== FIXABLE: IMPORT ISSUES ====================

import os, sys  # FIX: Split into separate imports
from pathlib import Path, os  # FIX: os should be separate import

import json
import re
# FIX: Imports should be sorted


# ==================== PARTIALLY FIXABLE: COMBINE WITH WARNINGS ====================

def mixed_issues_function(data, user_input):
    # FIXABLE: Augmented operator
    counter = 0
    counter = counter + 1
    
    # NON-FIXABLE: Security issue (just warning)
    os.system(f"process {user_input}")  # Command injection warning
    
    # FIXABLE: Augmented operator
    counter = counter + len(data)
    
    # NON-FIXABLE: Logical error (just warning)
    if counter > 5:  # If counter is known to be constant, this is a warning
        pass
    
    return counter


# ==================== DEMONSTRATION OF FIX PREVIEW ====================

def preview_test_function(x, y, z):
    """
    This function will show nice colored diffs in preview:
    - Red lines (removed)
    + Green lines (added)
    """
    # Multiple fixable issues in sequence
    total = 0
    total = total + x  # - total = total + x  /  + total += x
    total = total + y  # - total = total + y  /  + total += y
    total = total + z  # - total = total + z  /  + total += z
    
    multiplier = 1
    multiplier = multiplier * 2  # - multiplier = multiplier * 2  /  + multiplier *= 2
    multiplier = multiplier * 3  # - multiplier = multiplier * 3  /  + multiplier *= 3
    
    return total * multiplier


# ==================== MULTIPLE FIXABLE ISSUES IN ONE FILE ====================

class FixableClass:  # Could add docstring
    def MethodOne(self, value):  # FIX: method_one
        value = value + 1  # FIX: value += 1
        return value
    
    def MethodTwo(self, items):  # FIX: method_two
        count = 0
        for item in items:
            count = count + 1  # FIX: count += 1
        return count


# ==================== EASY TO FIX PATTERNS ====================

def simple_fixes():
    # All of these are straightforward fixes
    a = 10
    a = a + 1   # FIX: a += 1
    a = a - 2   # FIX: a -= 2
    a = a * 3   # FIX: a *= 3
    a = a / 4   # FIX: a /= 4
    a = a // 2  # FIX: a //= 2
    a = a % 5   # FIX: a %= 5
    a = a ** 2  # FIX: a **= 2
    
    return a


# ==================== LOOP WITH FIXABLE ISSUES ====================

def loop_fixes():
    result = 0
    for i in range(100):
        result = result + i  # FIX: result += i
        
        if i % 2 == 0:
            result = result * 2  # FIX: result *= 2
        else:
            result = result - 1  # FIX: result -= 1
    
    return result


# ==================== COMBINED FIXABLE AND WARNINGS ====================

def comprehensive_fix_test(x, y):
    # FIXABLE: Augmented operators (5 fixes)
    x = x + 1
    x = x * 2
    y = y + x
    y = y - 5
    result = 0
    result = result + x
    
    # NON-FIXABLE: Division by zero (warning only)
    zero = 0
    bad = 100 / zero
    
    # FIXABLE: More augmented operators (3 fixes)
    result = result + y
    result = result * 2
    result = result - bad
    
    return result

