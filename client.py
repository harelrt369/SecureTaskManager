import socket
import security
import tkinter as tk
from tkinter import messagebox
from cryptography.hazmat.primitives import serialization

HOST = '127.0.0.1'
PORT = 50000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

pub_key_bytes = client_socket.recv(1024)
server_pub_key = serialization.load_pem_public_key(pub_key_bytes)
aes_key = security.generate_aes_key()
encrypted_aes_key = security.rsa_encrypt(server_pub_key, aes_key)
client_socket.send(encrypted_aes_key)


def send_to_server(command):
    encrypted_command = security.aes_encrypt(aes_key, command.encode('utf-8'))
    client_socket.send(encrypted_command)

    encrypted_response = client_socket.recv(1024)
    return security.aes_decrypt(aes_key, encrypted_response).decode('utf-8')


# הוספנו event=None כדי שנוכל להפעיל את הפונקציה גם בלחיצת כפתור וגם עם Enter
def add_task(event=None):
    task = task_entry.get()
    if task:
        response = send_to_server(f"תוסיף:{task}")
        messagebox.showinfo("אישור שרת", response)
        task_entry.delete(0, tk.END)
        refresh_tasks()


def refresh_tasks():
    response = send_to_server("תראה")
    task_list_box.delete(1.0, tk.END)
    task_list_box.insert(tk.END, response)
    task_list_box.tag_add("center", "1.0", "end")


def on_closing():
    try:
        client_socket.close()
    except:
        pass
    window.destroy()


bg_color = "#ffe6e6"
btn_color = "#ff9999"

window = tk.Tk()
window.title("מערכת ניהול משימות מאובטחת")
window.geometry("450x450")
window.configure(bg=bg_color)

# קישור מקש ה-Enter (Return) לפונקציית הוספת המשימה
window.bind('<Return>', add_task)

tk.Label(window, text=":הכנס משימה חדשה", font=("Arial", 12), bg=bg_color).pack(pady=10)
task_entry = tk.Entry(window, width=40, font=("Arial", 12), justify="center")
task_entry.pack(pady=5)

add_button = tk.Button(window, text="הוסף משימה", font=("Arial", 10, "bold"), bg=btn_color, command=add_task)
add_button.pack(pady=10)

tk.Label(window, text=":המשימות שלי", font=("Arial", 12, "bold"), bg=bg_color).pack(pady=10)
task_list_box = tk.Text(window, height=10, width=50, font=("Arial", 11))
task_list_box.tag_configure("center", justify="center")
task_list_box.pack(pady=5)

refresh_button = tk.Button(window, text="רענן רשימה", font=("Arial", 10), bg=btn_color, command=refresh_tasks)
refresh_button.pack(pady=10)

window.protocol("WM_DELETE_WINDOW", on_closing)
refresh_tasks()
window.mainloop()