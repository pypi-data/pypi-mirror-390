"""
Performance Test Suite - Performance issues and anti-patterns
Tests: 20+ performance issues including NEW detections
"""

import re


# ==================== STRING CONCATENATION IN LOOPS ====================

def inefficient_string_concat_loop():
    result = ""
    for i in range(1000):
        result += str(i)  # Inefficient! Should use join()
        result += ", "
    return result

def string_concat_with_augmented():
    output = ""
    for item in large_list:
        output += item  # Inefficient string concatenation
        output += "\n"
    return output

def complex_string_building():
    html = ""
    for row in database_rows:
        html += "<tr>"
        html += f"<td>{row.id}</td>"
        html += f"<td>{row.name}</td>"
        html += "</tr>"
    return html


# ==================== NESTED LOOPS (O(n^3+) complexity) ====================

def triple_nested_loop():
    result = []
    for i in range(100):
        for j in range(100):
            for k in range(100):  # O(n^3) complexity!
                result.append(i * j * k)
    return result

def quadruple_nested_loop():
    count = 0
    for a in range(50):
        for b in range(50):
            for c in range(50):
                for d in range(50):  # O(n^4) complexity!
                    count += 1
    return count

def nested_loops_with_operations():
    matrix = []
    for i in range(n):
        row = []
        for j in range(m):
            cell = []
            for k in range(p):  # 3 levels deep
                cell.append(calculate(i, j, k))
            row.append(cell)
        matrix.append(row)
    return matrix


# ==================== REGEX COMPILATION IN LOOPS ====================

def regex_in_loop():
    results = []
    for line in lines:
        pattern = re.compile(r'\d+')  # Compiling in every iteration!
        matches = pattern.findall(line)
        results.extend(matches)
    return results

def regex_in_nested_loop():
    for file in files:
        for line in file:
            regex = re.compile(r'[A-Z]+')  # Compiling in nested loop!
            if regex.search(line):
                process(line)

def multiple_regex_in_loop():
    for text in texts:
        email_pattern = re.compile(r'\w+@\w+\.\w+')  # Should be outside
        url_pattern = re.compile(r'https?://\S+')   # Should be outside
        
        emails = email_pattern.findall(text)
        urls = url_pattern.findall(text)


# ==================== LIST APPEND IN LOOPS (List Comprehension) ====================

def simple_append_loop():
    result = []
    for i in range(100):
        result.append(i * 2)  # Could use list comprehension
    return result

def filter_and_append():
    filtered = []
    for item in items:
        if item.is_valid():
            filtered.append(item)  # Could use list comprehension with filter
    return filtered

def transformation_loop():
    transformed = []
    for record in records:
        transformed.append(record.to_dict())  # Could use list comprehension
    return transformed


# ==================== N+1 QUERY PATTERNS ====================

def n_plus_one_query():
    users = db.query("SELECT * FROM users")
    for user in users:
        # N+1 query problem!
        orders = db.query(f"SELECT * FROM orders WHERE user_id = {user.id}")
        user.orders = orders
    return users

def nested_n_plus_one():
    posts = Post.objects.all()
    for post in posts:
        # First N+1
        post.author = User.objects.get(id=post.author_id)
        
        # Second N+1
        comments = Comment.objects.filter(post_id=post.id)
        for comment in comments:
            # Third N+1!
            comment.user = User.objects.get(id=comment.user_id)


# ==================== REPEATED CALCULATIONS ====================

def repeated_calculation_in_loop():
    for i in range(1000):
        # Expensive calculation repeated every iteration
        threshold = calculate_threshold(config)  # Should be outside loop
        if values[i] > threshold:
            process(values[i])

def repeated_function_calls():
    for item in collection:
        max_val = get_max_value()  # Called every iteration
        min_val = get_min_value()  # Called every iteration
        if min_val < item < max_val:
            process_item(item)

def nested_repeated_calc():
    for i in range(n):
        for j in range(m):
            constant = expensive_compute()  # Recomputed for each i,j pair
            result[i][j] = constant * matrix[i][j]


# ==================== UNNECESSARY LIST CONVERSIONS ====================

def unnecessary_list_conversion():
    # Converting to list when not needed
    for item in list(generator_function()):  # Unnecessary list()
        process(item)

def double_conversion():
    data = set(my_list)  # First conversion
    result = list(data)  # Second conversion
    for item in list(result):  # Third unnecessary conversion!
        handle(item)


# ==================== INEFFICIENT DATA STRUCTURES ====================

def linear_search_repeated():
    for query in queries:
        for item in large_list:  # O(n*m) - should use dict/set
            if item.id == query.id:
                results.append(item)
                break

def membership_test_in_list():
    valid_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # Should be a set
    for record in records:
        if record.id in valid_ids:  # O(n) check, should be O(1) with set
            process(record)


# ==================== MISSING CACHING OPPORTUNITIES ====================

def repeated_expensive_call():
    for i in range(100):
        config = load_config_from_disk()  # Expensive, should cache
        process_with_config(i, config)

def repeated_database_lookup():
    for order in orders:
        # Same customer fetched multiple times
        customer = db.get_customer(order.customer_id)  # Should cache
        send_email(customer.email, order.details)


# ==================== COMBINED PERFORMANCE ISSUES ====================

def multiple_performance_problems():
    # Issue 1: String concatenation in loop
    output = ""
    
    # Issue 2: Regex compilation in loop
    for record in records:
        pattern = re.compile(r'\d+')
        
        # Issue 3: Nested loops (3 levels)
        for field in record.fields:
            for value in field.values:
                # Issue 4: Repeated calculation
                max_len = calculate_max_length()
                
                # String concat
                output += str(value)
                
                # Issue 5: N+1 query
                meta = db.query(f"SELECT * FROM metadata WHERE id = {value.id}")

def deeply_nested_with_inefficiencies():
    result = ""
    for a in range(10):
        for b in range(10):
            for c in range(10):
                for d in range(10):  # 4 levels deep!
                    # Regex compilation
                    pattern = re.compile(r'test')
                    
                    # String concatenation
                    result += f"{a},{b},{c},{d};"
                    
                    # Repeated expensive call
                    config = load_full_config()
                    
                    # Database call
                    data = db.query(f"SELECT * FROM data WHERE id = {d}")


# ==================== ADDITIONAL PATTERNS ====================

def inefficient_dict_building():
    result = {}
    for key in keys:
        for value in values:
            result[key] = result.get(key, [])  # Inefficient dict access
            result[key].append(value)

def repeated_len_in_loop():
    for i in range(len(items)):  # len() called every iteration
        for j in range(len(other_items)):  # Another len() every time
            if i < len(items) - 1:  # And another len()!
                process(items[i], other_items[j])

def string_join_in_loop():
    parts = []
    for item in items:
        # Building intermediate strings
        temp = ", ".join([str(item.a), str(item.b), str(item.c)])
        parts.append(temp)
    return ";".join(parts)  # Could be optimized

