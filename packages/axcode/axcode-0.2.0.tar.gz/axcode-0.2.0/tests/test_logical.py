"""
Logical Errors Test Suite - Comprehensive logical error detection
Tests: 40+ logical errors including ALL new detections
"""


# ==================== DIVISION BY ZERO ====================

def constant_division_by_zero():
    x = 10
    y = 0
    result = x / y  # Constant division by zero!
    return result

def potential_division_by_zero(value):
    denominator = value - 10
    if value > 5:
        result = 100 / denominator  # Potential division by zero when value == 10
    return result

def complex_division_issue(a, b):
    c = a - b
    d = c * 0
    return 42 / d  # Division by zero (d is always 0)

def conditional_division_bug(x):
    divisor = x if x != 0 else 0
    return 100 / divisor  # Can still be zero!


# ==================== CONSTANT CONDITIONS ====================

def always_true_condition():
    x = 10
    if x > 5:  # Always true!
        return "always"

def always_false_condition():
    y = 3
    if y > 10:  # Always false!
        return "never executed"

def self_comparison():
    value = 42
    if value < value:  # Always false (self-comparison)
        return "impossible"

def identity_comparison():
    x = 100
    if x == x:  # Always true (self-comparison)
        return "always"

def redundant_check():
    status = True
    if status == True:  # Redundant True comparison
        do_something()

def literal_condition():
    if True:  # Constant condition
        execute()
    
    if False:  # Constant condition (dead code)
        never_runs()

def constant_in_expression():
    x = 10
    if x + 5 == 15:  # Constant expression, always true
        return "constant"


# ==================== DUPLICATE CONDITIONS ====================

def duplicate_if_elif(value):
    if value > 10:
        return "high"
    elif value < 5:
        return "low"
    elif value > 10:  # Duplicate condition!
        return "never reached"

def more_duplicates(status):
    if status == "pending":
        process_pending()
    elif status == "active":
        process_active()
    elif status == "pending":  # Duplicate!
        never_reached()

def complex_duplicate(x, y):
    if x > 5 and y < 10:
        return "A"
    elif x < 3:
        return "B"
    elif x > 5 and y < 10:  # Exact duplicate!
        return "C"


# ==================== CONTRADICTORY CONDITIONS ====================

def impossible_range(x):
    if x > 10 and x < 5:  # Impossible!
        return "never"

def contradictory_equality(value):
    if value == 10 and value == 20:  # Contradictory!
        return "impossible"

def mixed_contradiction(n):
    if n >= 100 and n < 50:  # Impossible range
        return "never"

def complex_contradiction(a, b):
    if a > b and a < b:  # Contradictory
        return "impossible"

def multiple_contradictions(x):
    if x > 100 and x < 50 and x == 75:  # Multiple contradictions
        return "never"


# ==================== AUGMENTED ASSIGNMENT OPERATORS ====================

def missing_augmented_add():
    count = 0
    count = count + 1  # Should use count += 1
    return count

def missing_augmented_subtract():
    total = 100
    total = total - 5  # Should use total -= 5
    return total

def missing_augmented_multiply():
    value = 2
    value = value * 3  # Should use value *= 3
    return value

def missing_augmented_divide():
    amount = 100
    amount = amount / 2  # Should use amount /= 2
    return amount

def loop_with_missing_augmented():
    result = 0
    for i in range(10):
        result = result + i  # Should use result += i
    return result


# ==================== UNREACHABLE CODE ====================

def code_after_return():
    x = calculate_value()
    return x
    print("This is unreachable!")  # Unreachable!
    y = x + 1
    return y

def code_after_continue():
    for i in range(10):
        if i % 2 == 0:
            continue
            print(f"Even: {i}")  # Unreachable!

def code_after_break():
    while True:
        break
        print("Never executes")  # Unreachable!

def code_after_raise():
    if error_condition():
        raise ValueError("Error")
        cleanup()  # Unreachable!


# ==================== INFINITE LOOPS ====================

def infinite_while_loop():
    i = 0
    while i < 10:  # Infinite! i never changes
        print(i)
        do_something()

def infinite_for_modification():
    for i in range(10):
        i = 0  # Modifying loop variable
        print(i)

def infinite_while_no_change():
    condition = True
    while condition:  # Infinite! condition never changes
        process_data()
        log_message()


# ==================== MISSING BREAK IN LOOPS ====================

def loop_with_conditional_return():
    for item in collection:
        if item.matches(criteria):
            return item  # Should probably have break, not return
        process(item)

def nested_loop_return():
    for i in range(10):
        for j in range(10):
            if i * j > 50:
                return True  # Might want break instead
            calculate(i, j)


# ==================== UNUSED VARIABLES ====================

def unused_variable():
    x = calculate_something()  # x is never used
    y = get_data()
    return y

def unused_in_loop():
    total = 0
    for i in range(10):
        value = expensive_computation(i)  # value computed but not used
        total += i
    return total

def multiple_unused():
    a = 1  # unused
    b = 2  # unused
    c = 3
    return c


# ==================== MISSING ERROR HANDLING ====================

def no_try_for_file():
    file = open('data.txt')  # Should be in try-except
    content = file.read()
    file.close()
    return content

def no_try_for_network():
    response = requests.get('http://api.example.com')  # Should be in try-except
    return response.json()

def no_try_for_json():
    data = json.loads(raw_string)  # Should be in try-except
    return data


# ==================== COMPLEX COMBINED ERRORS ====================

def multiple_issues(value):
    # 1. Constant condition
    if value > 5:  # Assume value is always 10
        pass
    
    # 2. Division by zero
    zero = 0
    result = 100 / zero
    
    # 3. Unreachable code
    return result
    print("Unreachable")
    
    # 4. Unused variable
    unused = calculate()

def nested_issues(x, y):
    # 1. Contradictory condition
    if x > 100 and x < 50:
        return "impossible"
    
    # 2. Duplicate condition
    if x > 10:
        return "high"
    elif x > 10:  # Duplicate
        return "never"
    
    # 3. Missing augmented operator
    x = x + 1
    
    # 4. Potential division by zero
    divisor = y - y  # Always 0!
    return x / divisor

def loop_with_multiple_errors():
    total = 0
    # 1. Infinite loop
    i = 0
    while i < 10:  # i never increments
        # 2. Missing augmented operator
        total = total + i
        
        # 3. Unused variable
        temp = expensive_call(i)
        
        # 4. Unreachable after continue
        if i % 2 == 0:
            continue
            print("unreachable")


# ==================== EDGE CASES ====================

def chained_comparisons_bug(n):
    if 5 < n < 3:  # Impossible range
        return True

def boolean_redundancy():
    flag = True
    if flag == True == True:  # Redundant
        return "yes"

def zero_multiplication_division():
    x = 10
    x = x * 0  # x becomes 0
    y = 100 / x  # Division by zero!
    return y

def self_assignment_bug():
    value = 42
    value = value  # Self-assignment, likely a bug
    return value


# ==================== ADDITIONAL PATTERNS ====================

def constant_loop_condition():
    while True:  # Infinite if no break inside
        process()
        log()
        # No break statement!

def double_division_by_zero():
    a = 0
    b = 0
    result1 = 10 / a  # First division by zero
    result2 = 20 / b  # Second division by zero
    return result1 + result2

def nested_constant_conditions(x):
    if x > 5:  # Assume x is 10
        if x < 20:  # Assume x is 10, always true
            if x == 10:  # Assume x is 10, always true
                return "all constant"

