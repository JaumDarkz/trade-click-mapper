import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

class ServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Servidor")
        self.log_text = scrolledtext.ScrolledText(root, width=40, height=20)
        self.log_text.pack(padx=10, pady=10)
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("localhost", 8080))
        self.server_socket.listen(5)
        
        self.log("Aguardando conexões...")
        
        self.accept_connections_thread = threading.Thread(target=self.accept_connections)
        self.accept_connections_thread.start()

    def accept_connections(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            self.log(f"Conexão recebida de {client_address}")
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
            client_thread.start()

    def handle_client(self, client_socket, client_address):
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            message = data.decode("utf-8")
            self.log(f"Mensagem de {client_address}: {message}")

        self.log(f"Conexão com {client_address} encerrada")
        client_socket.close()

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    server_gui = ServerGUI(root)
    root.mainloop()