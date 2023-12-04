import socket
import tkinter as tk
from tkinter import ttk
from pynput.mouse import Listener, Button
from threading import Thread, Event

class ClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cliente")

        self.host_label = tk.Label(root, text="Host:")
        self.host_label.pack()
        self.host_entry = tk.Entry(root)
        self.host_entry.pack()

        self.port_label = tk.Label(root, text="Porta:")
        self.port_label.pack()
        self.port_entry = tk.Entry(root)
        self.port_entry.pack()

        self.connect_button = tk.Button(root, text="Conectar", command=self.connect_to_server)
        self.connect_button.pack()

        self.get_coords_button = tk.Button(root, text="Capturar Coordenadas", command=self.delayed_get_coordinates)
        self.get_coords_button.pack()

        self.log_text = tk.Text(root, height=10, width=40)
        self.log_text.pack()

        # Inicializa a tabela
        self.table_frame = ttk.Frame(root)
        self.table_frame.pack(pady=10)

        self.tree = ttk.Treeview(self.table_frame, columns=("ID", "Compra", "Venda"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Compra", text="Compra")
        self.tree.heading("Venda", text="Venda")
        self.tree.pack()

        self.client_socket = None
        self.coordinates_mapping = {}  # Dicionário para mapear coordenadas
        self.counter = 1
        self.event = Event()
        self.left_click_captured = False
        self.listen_thread = None  # Variável de instância para armazenar a thread de escuta

    def connect_to_server(self):
        host = self.host_entry.get()
        port = int(self.port_entry.get())

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))

    def delayed_get_coordinates(self):
        # Desabilita temporariamente o botão
        self.get_coords_button.config(state=tk.DISABLED)

        # Agendando a execução da função get_coordinates após um atraso de 2000 milissegundos (2 segundos)
        self.root.after(2000, self.get_coordinates)

    def get_coordinates(self):
        self.log("Aguardando cliques do usuário...")

        # Inicia um thread separado para capturar cliques do mouse fora da janela
        self.listen_thread = Thread(target=self.listen_for_clicks)
        self.listen_thread.start()

    def listen_for_clicks(self):
        with Listener(on_click=self.on_click) as listener:
            listener.join()

    def on_click(self, x, y, button, pressed):
        if pressed:
            if button == Button.left and not self.left_click_captured:
                self.capture_coordinates("compra", x, y)
                self.left_click_captured = True
            elif button == Button.right and self.left_click_captured:
                self.capture_coordinates("venda", x, y)

    def capture_coordinates(self, label, x, y):
        # Adiciona a coordenada ao mapeamento
        self.coordinates_mapping[label] = (x, y)
        self.log(f"Coordenada de {label.capitalize()} capturada: {x}, {y}")

        # Atualiza o log com as coordenadas mapeadas
        self.log(f"Coordenadas Mapeadas: {self.coordinates_mapping}")

        # Se já capturou as duas coordenadas, adiciona à tabela e reinicia
        if "compra" in self.coordinates_mapping and "venda" in self.coordinates_mapping:
            self.tree.insert("", "end", values=(self.counter, self.coordinates_mapping["compra"], self.coordinates_mapping["venda"]))
            self.counter += 1

            # Limpa o mapeamento de coordenadas
            self.coordinates_mapping = {}
            self.left_click_captured = False

            # Reabilita o botão
            self.get_coords_button.config(state=tk.NORMAL)

            # Sinaliza o evento para encerrar o thread pynput
            self.event.set()

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    client_gui = ClientGUI(root)
    root.mainloop()
