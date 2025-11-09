"""
Comprehensive Test Suite - All categories combined
Tests: 70+ issues across all categories for end-to-end validation
"""

import os
import hashlib
import pickle
import random
import re
import subprocess


# ==================== SECURITY + LOGICAL ERRORS ====================

def insecure_auth_with_logic_errors(username, password):
    # Security: Weak hashing
    pwd_hash = hashlib.md5(password.encode()).hexdigest()
    
    # Security: SQL injection
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{pwd_hash}'"
    
    # Logical: Constant condition (assume username is always "admin")
    if username == "admin":
        admin_mode = True
    
    # Logical: Division by zero
    attempts = 0
    rate_limit = 100 / attempts  # Division by zero!
    
    # Security: Logging sensitive data
    logging.info(f"Login: {username} with password {password}")
    
    return db.execute(query)


# ==================== SECURITY + PERFORMANCE ====================

def insecure_data_processing(user_inputs):
    # Performance: String concatenation in loop
    output = ""
    
    for user_input in user_inputs:
        # Security: Command injection
        os.system(f"process {user_input}")
        
        # Performance: Regex compilation in loop
        pattern = re.compile(r'\d+')
        
        # Security: eval() usage
        result = eval(user_input)
        
        # Performance: String concat
        output += str(result)
    
    return output


# ==================== LOGICAL + PERFORMANCE ====================

def inefficient_validation_with_bugs(items):
    # Logical: Missing augmented operator
    count = 0
    count = count + 1
    
    # Performance: Triple nested loops
    for i in range(len(items)):
        for j in range(len(items[i])):
            for k in range(len(items[i][j])):
                # Logical: Constant condition
                if k > 0:  # Assume k is always 0
                    pass
                
                # Logical: Potential division by zero
                value = items[i][j][k]
                divisor = value - value  # Always 0!
                result = 100 / divisor
    
    return count


# ==================== ALL THREE CATEGORIES ====================

def vulnerable_processor(data_list, user_id):
    # SECURITY: Hardcoded secret
    api_key = "sk-1234567890abcdefghijklmnopqrstuvwxyz"
    
    # LOGICAL: Unused variable
    unused_config = load_config()
    
    # PERFORMANCE: String concatenation
    html_output = ""
    
    # PERFORMANCE: Triple nested loops
    for data in data_list:
        for item in data.items:
            for field in item.fields:
                # SECURITY: SQL injection
                query = f"SELECT * FROM fields WHERE id = {field.id}"
                result = db.execute(query)
                
                # LOGICAL: Division by zero
                zero_val = 0
                calc = 100 / zero_val
                
                # PERFORMANCE: Regex in loop
                pattern = re.compile(r'\w+')
                matches = pattern.findall(field.value)
                
                # SECURITY: Weak crypto
                field_hash = hashlib.md5(field.value.encode()).hexdigest()
                
                # LOGICAL: Unreachable code
                if field.is_valid:
                    return field_hash
                    print("This won't execute")
                
                # PERFORMANCE: String concat
                html_output += f"<div>{field.value}</div>"
    
    # SECURITY: Insecure random for token
    session_token = str(random.randint(1000, 9999))
    
    # LOGICAL: Constant condition
    if user_id > 0:  # Assume user_id is always positive
        process_user(user_id)
    
    return html_output


# ==================== COMPLEX SECURITY SCENARIO ====================

def complex_security_issues(filename, query, code):
    # Hardcoded credentials
    db_password = "production_db_pass_2024"
    api_token = "ghp_abcdef1234567890ghijklmnopqr"
    
    # Path traversal
    with open(f"/var/data/{filename}") as f:
        content = f.read()
    
    # SQL injection
    sql = f"SELECT * FROM files WHERE name = '{filename}' AND query = '{query}'"
    
    # Command injection
    subprocess.run(f"grep '{query}' {filename}", shell=True)
    
    # Eval usage
    result = eval(code)
    
    # Unsafe pickle
    data = pickle.loads(content)
    
    # Insecure random for security
    nonce = str(random.random())
    
    return result


# ==================== COMPLEX LOGICAL ERRORS ====================

def complex_logical_errors(x, y, z):
    # Contradictory condition
    if x > 100 and x < 50:
        return "impossible1"
    
    # Duplicate conditions
    if y > 10:
        return "case1"
    elif y < 5:
        return "case2"
    elif y > 10:  # Duplicate!
        return "case3"
    
    # Division by zero
    denominator = x - x  # Always 0
    result = 100 / denominator
    
    # Missing augmented operators
    z = z + 1
    z = z * 2
    z = z - 3
    
    # Infinite loop
    i = 0
    while i < 10:  # i never changes
        process(i)
    
    # Unreachable after return
    return result
    cleanup()
    log_result()
    
    # Unused variables
    unused1 = calculate()
    unused2 = fetch_data()


# ==================== COMPLEX PERFORMANCE ISSUES ====================

def complex_performance_issues(records):
    # String concatenation
    output = ""
    
    # Quadruple nested loops!
    for r in records:
        for s in r.sections:
            for i in s.items:
                for v in i.values:
                    # Regex compilation in deep loop
                    pattern = re.compile(r'[A-Z]+')
                    
                    # Repeated calculation
                    max_len = calculate_max_length()
                    
                    # N+1 query
                    metadata = db.query(f"SELECT * FROM meta WHERE value_id = {v.id}")
                    
                    # String concat
                    output += f"{v.data},"
    
    return output


# ==================== REAL-WORLD SCENARIO 1: User Upload ====================

def handle_user_upload(filename, content, user_id):
    # SECURITY: Path traversal
    file_path = f"/uploads/{filename}"
    
    # LOGICAL: No error handling
    with open(file_path, 'w') as f:  # Also missing encoding
        f.write(content)
    
    # SECURITY: SQL injection
    query = f"INSERT INTO files (name, user_id) VALUES ('{filename}', {user_id})"
    db.execute(query)
    
    # SECURITY: Weak hashing
    file_hash = hashlib.md5(content.encode()).hexdigest()
    
    # LOGICAL: Division by zero
    zero = 0
    priority = 100 / zero
    
    # PERFORMANCE: String concatenation in loop
    log_message = ""
    for char in filename:
        log_message += char
    
    # SECURITY: Logging sensitive info
    logging.info(f"User {user_id} uploaded file with content: {content[:100]}")
    
    return file_hash


# ==================== REAL-WORLD SCENARIO 2: API Handler ====================

def api_request_handler(api_key, endpoint, params):
    # SECURITY: Hardcoded URL
    base_url = "https://prod-api.internal.company.com"
    
    # LOGICAL: Constant condition
    if len(api_key) > 0:  # Always true if function is called
        authorized = True
    
    # PERFORMANCE: Nested loops
    formatted_params = ""
    for key in params.keys():
        for value in params[key]:
            for item in value:
                # PERFORMANCE: String concat
                formatted_params += f"{key}={item}&"
                
                # PERFORMANCE: Regex in loop
                validator = re.compile(r'\w+')
                if not validator.match(str(item)):
                    continue
    
    # SECURITY: Command injection
    os.system(f"curl {base_url}/{endpoint}?{formatted_params}")
    
    # LOGICAL: Unreachable
    return formatted_params
    cleanup_params()


# ==================== REAL-WORLD SCENARIO 3: Data Migration ====================

def migrate_user_data(old_db, new_db):
    # SECURITY: Hardcoded credentials
    old_conn = "mysql://root:oldpass123@10.0.1.50/olddb"
    new_conn = "postgresql://admin:newpass456@10.0.1.51/newdb"
    
    # PERFORMANCE: N+1 queries
    users = old_db.query("SELECT * FROM users")
    for user in users:
        # N+1 problem
        profile = old_db.query(f"SELECT * FROM profiles WHERE user_id = {user.id}")
        posts = old_db.query(f"SELECT * FROM posts WHERE user_id = {user.id}")
        
        # SECURITY: SQL injection in new_db
        new_db.execute(f"INSERT INTO users (name, email) VALUES ('{user.name}', '{user.email}')")
        
        # LOGICAL: Missing augmented operator
        migrated_count = 0
        migrated_count = migrated_count + 1
        
        # LOGICAL: Division by zero
        success_rate = 100 / (total_users - total_users)
    
    # LOGICAL: Infinite loop
    retry_count = 0
    while retry_count < 5:  # retry_count never increments
        attempt_migration()


# ==================== EDGE CASE COMBINATIONS ====================

def edge_case_nightmare(input_data):
    # Multiple constant conditions
    if input_data > 5:  # Assume input_data is 10
        if input_data < 20:  # Also constant
            if input_data == 10:  # Also constant
                # Multiple divisions by zero
                a = 0
                b = 0
                c = 0
                r1 = 10 / a
                r2 = 20 / b
                r3 = 30 / c
                
                # Nested infinite loops
                i = 0
                while i < 10:  # i never changes
                    j = 0
                    while j < 10:  # j never changes
                        # String concatenation
                        output = ""
                        for k in range(100):
                            output += str(k)
                            
                            # Regex in nested position
                            pattern = re.compile(r'\d+')
                            
                            # Command injection
                            os.system(f"echo {k}")
                            
                            # eval
                            eval(f"k * {k}")

