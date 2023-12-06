import socket
import tkinter as tk
from tkinter import ttk
from pynput.mouse import Button, Controller, Listener
from threading import Thread, Event
from datetime import datetime, timedelta
import time
import os

class ClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cliente ClickMapper")
        self.root.configure(background="#1C1C1C")
        self.root.geometry("870x550")
        self.root.resizable(False, False)

        # Frame esquerdo
        self.left_frame = tk.Frame(root, bg="#1C1C1C")
        self.left_frame.pack(side=tk.LEFT, padx=20, pady=20)

        self.host_label = tk.Label(self.left_frame, text="Host:", bg="#1C1C1C", fg="white", font=("Arial", 12))
        self.host_label.pack(pady=5)
        self.host_entry = tk.Entry(self.left_frame, font=("Arial", 12))
        self.host_entry.pack(pady=5)

        self.port_label = tk.Label(self.left_frame, text="Porta:", bg="#1C1C1C", fg="white", font=("Arial", 12))
        self.port_label.pack(pady=5)
        self.port_entry = tk.Entry(self.left_frame, font=("Arial", 12))
        self.port_entry.pack(pady=5)

        self.connect_button = tk.Button(self.left_frame, text="Conectar", command=self.connect_to_server, bg="#007ACC", fg="white", font=("Arial", 12))
        self.connect_button.pack(pady=10)

        self.get_coords_button = tk.Button(self.left_frame, text="Capturar Coordenadas", command=self.delayed_get_coordinates, bg="#007ACC", fg="white", font=("Arial", 12))
        self.get_coords_button.pack(pady=10)

        # Frame direito
        self.right_frame = tk.Frame(root, bg="#1C1C1C")
        self.right_frame.pack(side=tk.LEFT, padx=20, pady=20)

        self.table_frame = ttk.Frame(self.right_frame)
        self.table_frame.pack(pady=5)

        self.tree = ttk.Treeview(self.table_frame, columns=("ID", "Compra", "Venda"), show="headings")
        self.tree.heading("ID", text="ID", anchor=tk.CENTER)
        self.tree.heading("Compra", text="Compra", anchor=tk.CENTER)
        self.tree.heading("Venda", text="Venda", anchor=tk.CENTER)
        self.tree.column("ID", width=50, anchor=tk.CENTER)
        self.tree.column("Compra", width=100, anchor=tk.CENTER)
        self.tree.column("Venda", width=100, anchor=tk.CENTER)
        self.tree.pack()

        self.intervalo_label = tk.Label(self.right_frame, text="Intervalo (segundos):", bg="#1C1C1C", fg="white", font=("Arial", 12))
        self.intervalo_label.pack(pady=5)
        self.intervalo_entry = tk.Entry(self.right_frame, font=("Arial", 12))
        self.intervalo_entry.pack(pady=5)
        self.intervalo_entry.insert(1, "1")

        # Log
        self.log_frame = tk.Frame(root, bg="#1C1C1C")
        self.log_frame.pack(side=tk.TOP, pady=20, padx=20)

        self.log_label = tk.Label(self.log_frame, text="Log:", bg="#1C1C1C", fg="white", font=("Arial", 12))
        self.log_label.pack()

        self.log_text = tk.Text(self.log_frame, height=10, width=40, font=("Arial", 12))
        self.log_text.pack()

        self.time_frame = tk.Frame(root, bg="#1C1C1C")
        self.time_frame.pack(side=tk.TOP, pady=20, padx=20)

        self.adjust_time_frame = tk.Frame(root, bg="#1C1C1C")
        self.adjust_time_frame.pack(side=tk.TOP, pady=0, padx=20)

        # Label e Entry para ajuste manual
        self.adjust_time_label = tk.Label(self.adjust_time_frame, text="Ajuste Manual (segundos):", bg="#1C1C1C", fg="white", font=("Arial", 12))
        self.adjust_time_label.grid(row=0, column=0, padx=10, pady=5)

        self.adjust_time_entry = tk.Entry(self.adjust_time_frame, font=("Arial", 12))
        self.adjust_time_entry.grid(row=0, column=1, padx=10, pady=5)
        self.adjust_time_entry.insert(0, "0")  # Definindo o padrão como 0

        # Botão para aplicar ajuste manual
        self.apply_adjustment_button = tk.Button(self.adjust_time_frame, text="Aplicar Ajuste", command=self.apply_time_adjustment, bg="#007ACC", fg="white", font=("Arial", 12))
        self.apply_adjustment_button.grid(row=0, column=2, padx=10, pady=5)

        # Frame do horário
        self.time_frame = tk.Frame(root, bg="#1C1C1C")
        self.time_frame.pack(side=tk.TOP, pady=0, padx=20)

        # Horário do computador
        self.computer_time_label = tk.Label(self.time_frame, text="Horário do computador:", bg="#1C1C1C", fg="white", font=("Arial", 12))
        self.computer_time_label.grid(row=0, column=0, padx=10, pady=5)

        self.computer_time_value = tk.Label(self.time_frame, text="", bg="#1C1C1C", fg="white", font=("Arial", 12))
        self.computer_time_value.grid(row=0, column=1, padx=10, pady=5)

        # Horário da corretora
        self.exchange_time_label = tk.Label(self.time_frame, text="Horário da corretora:", bg="#1C1C1C", fg="white", font=("Arial", 12))
        self.exchange_time_label.grid(row=1, column=0, padx=10, pady=5)

        self.exchange_time_value = tk.Label(self.time_frame, text="", bg="#1C1C1C", fg="white", font=("Arial", 12))
        self.exchange_time_value.grid(row=1, column=1, padx=10, pady=5)

        self.exchange_time_value = tk.Label(self.time_frame, text="", bg="#1C1C1C", fg="white", font=("Arial", 12))
        self.exchange_time_value.grid(row=1, column=1, padx=10, pady=5)

        # Variável de controle para a Checkbox
        self.show_click_settings_var = tk.BooleanVar()
        self.show_click_settings_var.set(False)  # Inicia não exibindo o frame

        # Checkbox para mostrar/esconder configurações de clique
        self.show_click_settings_checkbox = tk.Checkbutton(self.time_frame, text="Ignorar clique do segundo:", variable=self.show_click_settings_var, bg="#1C1C1C", fg="white", font=("Arial", 12), command=self.toggle_click_settings_frame, selectcolor="#1C1C1C")
        self.show_click_settings_checkbox.grid(row=2, column=0, columnspan=2, pady=20)

        # Frame de configurações de clique
        self.click_settings_frame = tk.Frame(root, bg="#1C1C1C")

        # Configurações para ignorar cliques
        self.ignore_click_label = tk.Label(self.click_settings_frame, text="Ignorar clique do segundo:", bg="#1C1C1C", fg="white", font=("Arial", 12))
        self.ignore_click_label.grid(row=0, column=0, pady=5)

        # Configuração do segundo para ignorar
        self.ignore_second_a_entry = tk.Entry(self.click_settings_frame, font=("Arial", 12), width=5)
        self.ignore_second_a_entry.grid(row=0, column=1, pady=5)

        tk.Label(self.click_settings_frame, text="a", bg="#1C1C1C", fg="white", font=("Arial", 12)).grid(row=0, column=2, pady=5)

        self.ignore_second_b_entry = tk.Entry(self.click_settings_frame, font=("Arial", 12), width=5)
        self.ignore_second_b_entry.grid(row=0, column=3, pady=5)

        # Empacote o frame após ajustar a visibilidade
        self.click_settings_frame.pack(side=tk.TOP, pady=0, padx=20)

        # Chamada para ajustar a visibilidade
        self.toggle_click_settings_frame()


        # Variáveis
        self.client_socket = None
        self.coordinates_mapping = {}
        self.counter = 1
        self.event = Event()
        self.left_click_captured = False
        self.mapping_in_progress = False

        self.compra_coordinates = []  # Lista para armazenar as coordenadas de compra
        self.venda_coordinates = []  # Lista para armazenar as coordenadas de venda

    def update_times(self):
        computer_time = datetime.now().strftime("%H:%M:%S")
        exchange_time = ""  # Atualize com o horário da corretora, se disponível

        # Obtém o valor da entrada para o ajuste manual
        manual_adjustment_text = self.adjust_time_entry.get()

        try:
            # Tente converter o valor da entrada para um número inteiro
            manual_adjustment = int(manual_adjustment_text) if manual_adjustment_text else 0
        except ValueError:
            # Se houver um erro ao converter, considere como 0
            manual_adjustment = 0

        # Garante que o ajuste seja apenas negativo
        manual_adjustment = max(manual_adjustment, 0)

        # Calcula o tempo ajustado sem causar OverflowError
        adjusted_time = datetime.now() - timedelta(seconds=manual_adjustment % (2**31))

        # Atualiza os rótulos com os horários
        self.computer_time_value.config(text=computer_time)
        self.exchange_time_value.config(text=exchange_time)

        # Atualiza o rótulo com o horário ajustado
        adjusted_time_str = adjusted_time.strftime("%H:%M:%S")
        self.computer_time_value.config(text=adjusted_time_str)

        # Chama recursivamente a função após 1000 milissegundos (1 segundo)
        self.root.after(1000, self.update_times)

    def apply_time_adjustment(self):
        try:
            manual_adjustment = int(self.adjust_time_entry.get())
        except ValueError:
            self.log("Erro: Insira um valor válido para o ajuste manual.")
            return

        self.log(f"Ajuste manual aplicado: {manual_adjustment} segundos.")

    
    def get_adjusted_time(self):
        # Obtém o valor da entrada para o ajuste manual
        manual_adjustment_text = self.adjust_time_entry.get()

        try:
            # Tente converter o valor da entrada para um número inteiro
            manual_adjustment = int(manual_adjustment_text) if manual_adjustment_text else 0
        except ValueError:
            # Se houver um erro ao converter, considere como 0
            manual_adjustment = 0

        # Garante que o ajuste seja apenas negativo
        manual_adjustment = max(manual_adjustment, 0)

        # Calcula o tempo ajustado sem causar OverflowError
        adjusted_time = datetime.now() - timedelta(seconds=manual_adjustment % (2**31))

        return adjusted_time

    def connect_to_server(self):
        host = self.host_entry.get()
        port = int(self.port_entry.get())
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        receive_thread = Thread(target=self.receive_messages)
        receive_thread.start()

    def delayed_get_coordinates(self):
        if not self.mapping_in_progress:
            self.mapping_in_progress = True
            # Desabilita temporariamente o botão
            self.get_coords_button.config(state=tk.DISABLED)
            # Agendando a execução da função get_coordinates após um atraso de 500 milissegundos (0,5 segundos)
            self.root.after(500, self.get_coordinates)

    def get_coordinates(self):
        self.log("Aguardando cliques do usuário...")
        # Define que o mapeamento está em andamento
        self.mapping_in_progress = True
        # Inicia um thread separado para capturar cliques do mouse fora da janela
        Thread(target=self.listen_for_clicks).start()

    def listen_for_clicks(self):
        with Listener(on_click=self.on_click) as listener:
            listener.join()

    def on_click(self, x, y, button, pressed):
        if pressed and self.mapping_in_progress:
            if button == Button.left and not self.left_click_captured:
                self.capture_coordinates("compra", x, y)
                self.left_click_captured = True
            elif button == Button.right and self.left_click_captured:
                self.capture_coordinates("venda", x, y)

    def capture_coordinates(self, tipo, x, y):
        if tipo in self.coordinates_mapping:
            return

        self.coordinates_mapping[tipo] = (x, y)
        self.log(f"Coordenadas {tipo.capitalize()}: ({x}, {y})")

        if len(self.coordinates_mapping) == 2:
            # Adicione a entrada na tabela
            id_ = f"{self.counter}"
            compra = str(self.coordinates_mapping["compra"])
            venda = str(self.coordinates_mapping["venda"])
            self.tree.insert("", "end", values=(id_, compra, venda))
            self.counter += 1
            self.compra_coordinates.append(self.coordinates_mapping["compra"])
            self.venda_coordinates.append(self.coordinates_mapping["venda"])

            print(self.compra_coordinates, self.venda_coordinates)

            # Reinicie o mapeamento
            self.mapping_in_progress = False
            self.left_click_captured = False
            self.coordinates_mapping = {}
            # Habilita o botão novamente
            self.get_coords_button.config(state=tk.NORMAL)

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                if message == "compra":
                    Thread(target=self.handle_compra_message).start()
                elif message == "venda":
                    Thread(target=self.handle_venda_message).start()
                else:
                    # Lida com outras mensagens recebidas do servidor
                    pass
            except Exception as e:
                print("Erro ao receber mensagem do servidor:", str(e))
                break

    def handle_compra_message(self):
        intervalo = int(self.intervalo_entry.get())
        self.intervalo = intervalo
        
        # Obtenha os valores dos campos de entrada
        ignore_second_a_text = self.ignore_second_a_entry.get()
        ignore_second_b_text = self.ignore_second_b_entry.get()

        # Verifica se os campos não estão vazios
        if ignore_second_a_text and ignore_second_b_text:
            ignore_second_a = int(ignore_second_a_text)
            ignore_second_b = int(ignore_second_b_text)
        else:
            # Define valores padrão se os campos estiverem vazios
            ignore_second_a = 0
            ignore_second_b = 0

        # Obtenha o valor ajustado do tempo
        adjusted_time = self.get_adjusted_time()

        for coord in self.compra_coordinates:
            # Obtém o segundo atual do tempo ajustado
            current_second = adjusted_time.second

            # Verifica se o segundo atual está fora do intervalo de ignoração
            if not ignore_second_a <= current_second <= ignore_second_b:
                mouse = Controller()
                mouse.position = coord
                mouse.click(Button.left)
                time.sleep(intervalo)


    def handle_venda_message(self):
        intervalo = int(self.intervalo_entry.get())
        self.intervalo = intervalo
        
        # Obtenha os valores dos campos de entrada
        ignore_second_a_text = self.ignore_second_a_entry.get()
        ignore_second_b_text = self.ignore_second_b_entry.get()

        # Verifica se os campos não estão vazios
        if ignore_second_a_text and ignore_second_b_text:
            ignore_second_a = int(ignore_second_a_text)
            ignore_second_b = int(ignore_second_b_text)
        else:
            # Define valores padrão se os campos estiverem vazios
            ignore_second_a = 0
            ignore_second_b = 0

        adjusted_time = self.get_adjusted_time()

        for coord in self.venda_coordinates:
            # Verifica se o segundo atual está fora do intervalo de ignoração
            current_second = adjusted_time.second
            if not ignore_second_a <= current_second <= ignore_second_b:
                mouse = Controller()
                mouse.position = coord
                mouse.click(Button.left)
                time.sleep(intervalo)


    def toggle_click_settings_frame(self):
        if self.show_click_settings_var.get():
            self.click_settings_frame.pack(side=tk.TOP, pady=20, padx=20)
        else:
            self.click_settings_frame.pack_forget()
            self.ignore_second_a_entry.delete(0, tk.END)
            self.ignore_second_a_entry.insert(0, '0')

            self.ignore_second_b_entry.delete(0, tk.END)
            self.ignore_second_b_entry.insert(0, '0')

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def on_closing(self):
        # Encerra a conexão com o servidor
        if self.client_socket:
            self.client_socket.close()
        root.destroy()
        os._exit(0)

root = tk.Tk()
client_gui = ClientGUI(root)
root.protocol("WM_DELETE_WINDOW", client_gui.on_closing)
client_gui.update_times()  # Inicie a atualização dos horários
root.mainloop()