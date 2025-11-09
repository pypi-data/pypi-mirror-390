"""
Security Test Suite - Comprehensive security vulnerability detection
Tests: 60+ security issues including NEW detections
"""

import os
import sys
import pickle
import hashlib
import random
import subprocess
import yaml
import logging
import re


# ==================== HARDCODED SECRETS (30+ patterns) ====================

# API Keys
OPENAI_KEY = "sk-proj-abcdefghijklmnop12345678901234567890"
ANTHROPIC_KEY = "sk-ant-api03-1234567890abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz"
GITHUB_TOKEN = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# Passwords and tokens
DB_PASSWORD = "MyDatabasePassword123!"
API_SECRET = "super_secret_api_key_12345"
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
OAUTH_SECRET = "oauth_client_secret_1234567890"
ENCRYPTION_KEY = "aes256_encryption_key_secret"

# Connection strings with credentials
MONGO_URI = "mongodb://admin:secretpass@prod-db.company.com:27017/maindb"
POSTGRES_URL = "postgresql://dbuser:dbpass123@database.internal:5432/production"
MYSQL_CONN = "mysql://root:rootpassword@10.0.1.50:3306/app_db"

# Private keys
RSA_KEY = "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA..."
PRIVATE_KEY_DATA = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBg..."


# ==================== NEW: HARDCODED URLs and IPs ====================

# These should be in config files, not hardcoded
API_ENDPOINT = "https://api.production.company.com/v1"
DATABASE_HOST = "192.168.1.100"
REDIS_SERVER = "10.0.2.50"
EXTERNAL_SERVICE = "http://third-party-api.example.org/endpoint"


# ==================== SQL INJECTION (All Variants) ====================

def get_user_by_id(user_id):
    # F-string injection
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query)

def search_products(keyword):
    # .format() injection
    query = "SELECT * FROM products WHERE name LIKE '%{}%'".format(keyword)
    return db.execute(query)

def delete_record(table, record_id):
    # % formatting injection
    query = "DELETE FROM %s WHERE id = %s" % (table, record_id)
    return db.execute(query)

def authenticate(username, password):
    # String concatenation injection
    query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
    return db.execute(query)

def complex_query(status, date, limit):
    # Multiline with multiple injections
    query = f"""
        SELECT o.id, o.total, u.email
        FROM orders o
        JOIN users u ON o.user_id = u.id
        WHERE o.status = '{status}'
        AND o.created_at > '{date}'
        LIMIT {limit}
    """
    return db.execute(query)


# ==================== COMMAND INJECTION ====================

def cleanup_files(filename):
    os.system(f"rm -rf /tmp/{filename}")  # Dangerous!

def backup_database(db_name):
    os.popen(f"pg_dump {db_name} > backup.sql")  # Dangerous!

def run_script(script_name):
    subprocess.run(f"bash scripts/{script_name}", shell=True)  # Dangerous!

def execute_command(cmd):
    subprocess.call(cmd, shell=True)  # Dangerous!


# ==================== NEW: User Input with Shell Commands ====================

def process_user_file():
    filename = input("Enter filename: ")
    os.system(f"cat {filename}")  # CRITICAL: User input in shell command!

def run_user_command():
    user_cmd = input("Enter command: ")
    os.popen(user_cmd)  # CRITICAL: Direct user input execution!


# ==================== EVAL/EXEC/COMPILE ====================

def calculate_user_expression(expr):
    return eval(expr)  # Dangerous!

def execute_dynamic_code(code):
    exec(code)  # Dangerous!

def compile_user_code(source):
    return compile(source, '<string>', 'exec')  # Dangerous!

def dynamic_import(module):
    return __import__(module)  # Risky!


# ==================== WEAK CRYPTOGRAPHY ====================

def hash_password_md5(password):
    return hashlib.md5(password.encode()).hexdigest()  # Weak!

def hash_data_sha1(data):
    return hashlib.sha1(data.encode()).hexdigest()  # Weak!

def hash_with_new_md5(text):
    return hashlib.new('md5', text.encode()).hexdigest()  # Weak!

def verify_password_weak(input_pwd, stored_hash):
    return hashlib.md5(input_pwd.encode()).hexdigest() == stored_hash


# ==================== INSECURE RANDOM (Security Context) ====================

def generate_session_token():
    return str(random.randint(100000, 999999))  # Insecure!

def create_api_key():
    return f"api-{random.randint(1000, 9999)}"  # Insecure!

def generate_password_reset_token():
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.choice(chars) for _ in range(32))  # Insecure!

def create_encryption_nonce():
    return random.randbytes(16)  # Insecure for crypto!

def generate_oauth_state():
    return str(random.random())  # Insecure!


# ==================== UNSAFE DESERIALIZATION ====================

def load_user_data(file_path):
    with open(file_path, 'rb') as f:
        return pickle.load(f)  # Dangerous!

def deserialize_session(data):
    return pickle.loads(data)  # Dangerous!


# ==================== NEW: UNSAFE YAML ====================

def load_config(config_file):
    with open(config_file) as f:
        return yaml.load(f)  # Dangerous! Missing Loader parameter

def parse_yaml_data(yaml_string):
    return yaml.load(yaml_string)  # Should use yaml.safe_load()


# ==================== PATH TRAVERSAL ====================

def read_user_file(filename):
    with open(f"/var/data/uploads/{filename}") as f:  # Path traversal risk
        return f.read()

def serve_static_file(path):
    full_path = os.path.join("/var/www/static", path)
    with open(full_path) as f:
        return f.read()


# ==================== MISSING FILE ENCODING ====================

def read_config_file(path):
    with open(path, 'r') as f:  # Missing encoding!
        return f.read()

def write_log_file(path, message):
    with open(path, 'w') as f:  # Missing encoding!
        f.write(message)


# ==================== EMPTY EXCEPT BLOCKS ====================

def parse_json_silent(data):
    try:
        return json.loads(data)
    except:  # Silently swallowing all exceptions!
        pass

def network_call_no_logging(url):
    try:
        response = requests.get(url)
        return response.json()
    except Exception:  # No logging!
        pass


# ==================== NEW: SENSITIVE DATA IN LOGS ====================

def log_user_credentials(username, password):
    # Logging sensitive data!
    logging.info(f"User login attempt: {username}, password: {password}")

def debug_api_call(api_key, endpoint):
    # Logging API key!
    logging.debug(f"Calling API with key: {api_key} to {endpoint}")

def log_database_connection(db_password):
    # Logging database password!
    print(f"Connecting to database with password: {db_password}")

def log_token_refresh(refresh_token):
    # Logging refresh token!
    logger.info(f"Refreshing with token: {refresh_token}")


# ==================== COMBINED VULNERABILITIES ====================

def vulnerable_upload_handler(filename, content):
    # Multiple issues:
    # 1. Path traversal
    # 2. No validation
    # 3. Hardcoded path
    # 4. No encoding
    upload_path = f"/var/uploads/{filename}"  # Path traversal
    with open(upload_path, 'w') as f:  # No encoding
        f.write(content)
    
    # Log the upload (logging sensitive path)
    logging.info(f"File uploaded: {upload_path}")
    
    return upload_path

def insecure_authentication(username, password):
    # Multiple issues:
    # 1. SQL injection
    # 2. Weak hashing
    # 3. Logging sensitive data
    
    # Hash password with MD5 (weak!)
    pwd_hash = hashlib.md5(password.encode()).hexdigest()
    
    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE username = '{username}' AND password_hash = '{pwd_hash}'"
    
    # Log credentials (bad!)
    logging.info(f"Login attempt: {username} with hash {pwd_hash}")
    
    return db.execute(query)


# ==================== ADDITIONAL PATTERNS ====================

# Bearer tokens
AUTH_HEADER = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"

# More connection strings
RABBITMQ_URL = "amqp://admin:rabbit123@message-queue.internal:5672/"
ELASTICSEARCH_URL = "http://elastic:elastic123@search.internal:9200"

# SSL certificates
SSL_CERT_KEY = "-----BEGIN CERTIFICATE-----\nMIIDXTCCAkWgAwIBAgIJ..."

# More weak crypto
def hash_with_sha1_new(data):
    return hashlib.new('sha1', data.encode()).digest()

# Direct SQL without parameterization
def update_user_email(user_id, new_email):
    query = f"UPDATE users SET email = '{new_email}' WHERE id = {user_id}"
    db.execute(query)

