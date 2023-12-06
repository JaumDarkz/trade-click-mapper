import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
import os

class ServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Servidor ClickMapper")
        self.root.configure(background="#1C1C1C")
        self.root.resizable(False, False) 
        
        self.log_text = scrolledtext.ScrolledText(root, width=40, height=20, font=("Arial", 12))
        self.log_text.pack(padx=20, pady=20)
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("localhost", 8080))
        self.server_socket.listen(5)
        
        self.log("Aguardando conexões...")
        
        self.closing_flag = False  # Flag para indicar o fechamento da aplicação

        self.accept_connections_thread = threading.Thread(target=self.accept_connections)
        self.accept_connections_thread.start()

        # Botões de "Clique de Compra" e "Clique de Venda"
        self.compra_button = tk.Button(root, text="Clique de Compra", command=self.send_compra_click, bg="#007ACC", fg="white", font=("Arial", 12))
        self.compra_button.pack(pady=10)

        self.venda_button = tk.Button(root, text="Clique de Venda", command=self.send_venda_click, bg="#007ACC", fg="white", font=("Arial", 12))
        self.venda_button.pack(pady=10)

        # Lista para armazenar os sockets dos clientes conectados
        self.client_sockets = []

    def on_closing(self):
        # Define a flag de fechamento como True
        self.closing_flag = True

        # Encerra a conexão com o servidor
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception as e:
                # Lida com exceções durante o fechamento do socket do servidor, se necessário
                pass

        # Desconecta todos os clientes
        for client_socket in self.client_sockets:
            try:
                client_socket.close()
            except Exception as e:
                # Lida com exceções durante o fechamento do socket do cliente, se necessário
                pass

        # Aguarda todas as threads de clientes serem encerradas
        for client_thread in threading.enumerate():
            if client_thread != threading.current_thread():
                try:
                    client_thread.join(timeout=10)  # Aumente o tempo de espera, se necessário
                except Exception as e:
                    # Lida com exceções durante o encerramento da thread do cliente, se necessário
                    pass

        # Adicionalmente, aguarda a conclusão da thread de aceitação de conexões
        if self.accept_connections_thread:
            try:
                self.accept_connections_thread.join(timeout=10)  # Aumente o tempo de espera, se necessário
            except Exception as e:
                # Lida com exceções durante o encerramento da thread de aceitação de conexões, se necessário
                pass

        self.log("Servidor encerrado")

        # Força a saída do processo
        os._exit(0)

    def accept_connections(self):
        while not self.closing_flag:
            try:
                client_socket, client_address = self.server_socket.accept()
                self.log(f"Conexão recebida de {client_address}")
                # Adicionar o novo socket à lista de sockets dos clientes conectados
                self.client_sockets.append(client_socket)
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                client_thread.start() 
            except socket.error as e:
                # Verifica se a exceção é devido ao fechamento do socket
                if self.closing_flag and isinstance(e, socket.error) and e.errno == 10038:
                    break
                else:
                    raise

    def handle_client(self, client_socket, client_address):
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                message = data.decode("utf-8")
                self.log(f"Mensagem de {client_address}: {message}")

                # Verificar a mensagem recebida e executar o clique correspondente
                if message == "compra":
                    self.log("Enviando clique de compra para o cliente...")
                    try:
                        client_socket.sendall(b"compra")
                    except ConnectionResetError:
                        self.log(f"Conexão com {client_address} encerrada abruptamente")
                        self.client_sockets.remove(client_socket)
                        client_socket.close()
                elif message == "venda":
                    self.log("Enviando clique de venda para o cliente...")
                    try:
                        client_socket.sendall(b"venda")
                    except ConnectionResetError:
                        self.log(f"Conexão com {client_address} encerrada abruptamente")
                        self.client_sockets.remove(client_socket)
                        client_socket.close()

        except ConnectionResetError:
            self.log(f"Conexão com {client_address} encerrada pelo cliente")
        finally:
            self.log(f"Conexão com {client_address} encerrada")
            self.client_sockets.remove(client_socket)
            client_socket.close()

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def send_compra_click(self):
        for client_socket in self.client_sockets:
            try:
                client_socket.sendall(b"compra")
            except ConnectionResetError:
                client_address = client_socket.getpeername()
                self.log(f"Conexão com {client_address} encerrada abruptamente")
                self.client_sockets.remove(client_socket)
                client_socket.close()

    def send_venda_click(self):
        for client_socket in self.client_sockets:
            try:
                client_socket.sendall(b"venda")
            except ConnectionResetError:
                client_address = client_socket.getpeername()
                self.log(f"Conexão com {client_address} encerrada abruptamente")
                self.client_sockets.remove(client_socket)
                client_socket.close()


root = tk.Tk()
server_gui = ServerGUI(root)
root.protocol("WM_DELETE_WINDOW", server_gui.on_closing)
root.mainloop()