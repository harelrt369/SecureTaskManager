import socket
import security
from cryptography.hazmat.primitives import serialization

HOST = '192.168.1.135'
PORT = 50000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()
print(f"[*] השרת הופעל ומאזין בכתובת {HOST} על פורט {PORT}...")

client_socket, client_address = server_socket.accept()
print(f"[+] לקוח התחבר בהצלחה מכתובת: {client_address}")

print("[*] מתחיל החלפת מפתחות הצפנה...")
server_priv_key, server_pub_key = security.generate_rsa_keys()

pub_key_bytes = server_pub_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)
client_socket.send(pub_key_bytes)

encrypted_aes_key = client_socket.recv(1024)
aes_key = security.rsa_decrypt(server_priv_key, encrypted_aes_key)
print("[+] מפתח ה-AES חולץ בהצלחה! התקשורת מאובטחת.")

tasks = []

while True:
    try:
        encrypted_data = client_socket.recv(1024)
        if not encrypted_data:
            break

        client_message = security.aes_decrypt(aes_key, encrypted_data).decode('utf-8')
        print(f"[פקודה שהתקבלה מהלקוח]: {client_message}")

        if client_message.startswith("תוסיף:"):
            new_task = client_message.split("תוסיף:")[1]
            tasks.append(new_task)
            response = f"המשימה '{new_task}' הוספה בהצלחה!"

        elif client_message.strip() == "תראה":
            if len(tasks) == 0:
                # הזזנו את הנקודה לתחילת המשפט כדי שתוצג נכון בעברית
                response = ".הרשימה ריקה"
            else:
                response = "\n".join(tasks)
        else:
            response = "שגיאה: פקודה לא מוכרת."

        encrypted_response = security.aes_encrypt(aes_key, response.encode('utf-8'))
        client_socket.send(encrypted_response)

    except ConnectionResetError:
        break

print("[-] הלקוח התנתק.")
client_socket.close()
server_socket.close()