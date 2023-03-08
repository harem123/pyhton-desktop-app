#from cgitb import text
from tkinter import CENTER, IntVar, ttk, Toplevel
from tkinter.constants import SUNKEN
from pubsub import pub

PADX_BASE = 20
PADY_BASE = 5

class ConnectionPanel(ttk.Labelframe):
    def __init__(self, root):
        super().__init__(root)

        # Settings
        self.lbl_tittle_frame = ttk.Label(self, text="Conexión")
        self.configure(height=130, width=480, relief="groove" , borderwidth=2, 
                       labelwidget=self.lbl_tittle_frame)
        self.grid_propagate(0)

        # Widgets
        # Baud
        lbl_baud = ttk.Label(self, text="Baud", width=8, anchor="e")
        lbl_baud.grid(row=0, column=0, padx=PADX_BASE, pady=PADY_BASE)
        self.entry_baud = ttk.Entry(self, width=7)
        self.entry_baud.grid(row=0, column=1, padx=PADX_BASE, pady=PADY_BASE, 
                             sticky="w")
        # Port
        lbl_port = ttk.Label(self, text="Port", width=8, anchor="e")
        lbl_port.grid(row=1, column=0, padx=PADX_BASE, pady=PADY_BASE)
        self.cbo_port = ttk.Combobox(self, width=16, 
                                     postcommand=self.cbo_port_clicked)
        self.cbo_port.grid(row=1, column=1, padx=PADX_BASE, pady=PADY_BASE)

        # Connect button
        btn_connect = ttk.Button(self, text="Set", 
                                 command=self.btn_connect_clicked)
        btn_connect.grid(row=0, column=2, padx=PADX_BASE, pady=PADY_BASE)

        # Disconnect button
        btn_disconnect = ttk.Button(self, text="Desconectar", 
                                    command=self.btn_disconnect_clicked) 
        btn_disconnect.grid(row=1, column=2, padx=PADX_BASE, pady=PADY_BASE)

        # Message output
        self.lbl_message = ttk.Label(self, width=38, anchor=CENTER)                           
        self.lbl_message.grid(row=2, column=0, columnspan=3, padx=PADX_BASE, 
                              pady=PADY_BASE, sticky="w")
        # Topics
        self.topics_to_pubsub()

    def cbo_port_clicked(self):
        pub.sendMessage('get-available-ports')

    def set_cbo_port(self, ports):
        self.cbo_port["values"] = ports

    def btn_connect_clicked(self):
        baud = self.entry_baud.get()
        port = self.cbo_port.get()
        if not baud.isnumeric():
            self.lbl_message['text'] = "Baud debe ser numerico"
            return None
        if not port:
            self.lbl_message['text'] = "Seleccione un puerto serial"
            return None
        pub.sendMessage('set-serial-port', port=port, baud=baud)
                        
    def btn_disconnect_clicked(self):
        pub.sendMessage('disconnect-serial-port', show_msg=True)

    def show_message(self, msg):
        self.lbl_message['text'] = msg

    def topics_to_pubsub(self):
        pub.subscribe(self.set_cbo_port, 'show-available-ports')
        pub.subscribe(self.show_message, 'connection-panel-msg')
        

class UserPanel(ttk.Labelframe):
    def __init__(self, root):
        super().__init__(root)
        self._root = root
        
        # Settings
        self.lbl_tittle_frame = ttk.Label(self, text="Usuario")
        self.configure(height=130, width=480, relief="groove", borderwidth=2, 
                        labelwidget=self.lbl_tittle_frame)
        self.grid_propagate(0)

        # Widgets
        # User Id
        lbl_user_id = ttk.Label(self, text="ID", width=8, anchor="e")
        lbl_user_id.grid(row=0, column=0, padx=PADX_BASE, pady=PADY_BASE,
                         sticky="e" )
        self.entry_user_id = ttk.Entry(self, width=17)
        self.entry_user_id.grid(row=0, column=1, padx=PADX_BASE, 
                                pady=PADY_BASE)
        # Username
        lbl_user = ttk.Label(self, text="Nombre", width=8, anchor="e")
        lbl_user.grid(row=1, column=0, padx=PADX_BASE, pady=PADY_BASE,
                      sticky="e" )
        self.lbl_user_ = ttk.Label(self, width=17, background="#ffffff",
                                   relief=SUNKEN)
        self.lbl_user_.grid(row=1, column=1, padx=PADX_BASE, pady=PADY_BASE)

        # Validate button
        btn_validate = ttk.Button(self, text="Verificar", 
                                  command=self.btn_validate_clicked )
        btn_validate.grid(row=0, column=2, padx=PADX_BASE, pady=PADY_BASE)
        
        # Register button
        btn_register = ttk.Button(self, text="Registrar", 
                                  command=self.btn_register_clicked )
        btn_register.grid(row=1, column=2, padx=PADX_BASE, pady=PADY_BASE)
        
        # Message output
        self.lbl_message = ttk.Label(self, width=38, anchor=CENTER)                           
        self.lbl_message.grid(row=2, column=0, columnspan=3, padx=PADX_BASE, 
                              pady=PADY_BASE, sticky="w")
        # Topics
        self.topics_to_pubsub()

    def btn_register_clicked(self):
        user_registration_window = UserRegistrationWindow(self._root)

    def btn_validate_clicked(self):
        user_id = self.entry_user_id.get()
        if not user_id:
            self.lbl_message['text'] = "Escriba un ID de usuario"
            return None
        self.lbl_user_['text'] = ""
        self.lbl_message['text'] = ""
        pub.sendMessage('verify-user', id=self.entry_user_id.get())

    def show_user_data(self, name):
        self.lbl_user_['text'] = name
        self.lbl_message['text'] = "Validación exitosa"

    def show_message(self, msg):
        self.lbl_message['text'] = msg

    def topics_to_pubsub(self):
        pub.subscribe(self.show_user_data, 'show-user-data')
        pub.subscribe(self.show_message, 'user-panel-msg')

class ConfigurationPanel(ttk.Labelframe):
    def __init__(self, root):
        super().__init__(root)
        
        # Settings
        self.lbl_tittle_frame = ttk.Label(self, text="Configuración")
        self.configure(height=120, width=480, relief="groove", 
                       borderwidth=2, labelwidget=self.lbl_tittle_frame)
        self.grid_propagate(0)

        # Widgets
        # Time
        lbl_time = ttk.Label(self, text="Tiempo Celda (s)")
        lbl_time.grid(row=0, column=0, padx=PADX_BASE, pady=PADY_BASE, 
                      sticky="e")
        self.entry_time = ttk.Entry(self, width=5)
        self.entry_time.grid(row=0, column=1, padx=PADX_BASE, pady=PADY_BASE) 
        
        # Shots
        lbl_shots = ttk.Label(self, text="Tiros")
        lbl_shots.grid(row=1, column=0, padx=PADX_BASE, pady=PADY_BASE, 
                       sticky="e")
        self.entry_shots = ttk.Entry(self, width=5)
        self.entry_shots.grid(row=1, column=1, padx=PADX_BASE, pady=PADY_BASE)
        
        # Right PWM
        lbl_right_pwm = ttk.Label(self, text="PWM D")
        lbl_right_pwm.grid(row=0, column=2, padx=PADX_BASE, pady=PADY_BASE, 
                           sticky="e")
        self.entry_right_pwm = ttk.Entry(self, width=5)
        self.entry_right_pwm.grid(row=0, column=3, padx=PADX_BASE, 
                                  pady=PADY_BASE) 
        # Left PWM
        lbl_left_pwm = ttk.Label(self, text="PWM I")
        lbl_left_pwm.grid(row=1, column=2, padx=PADX_BASE, pady=PADY_BASE, 
                          sticky="e")
        self.entry_left_pwm = ttk.Entry(self, width=5)
        self.entry_left_pwm.grid(row=1, column=3, padx=PADX_BASE, 
                                 pady=PADY_BASE)
        # Message output
        self.lbl_message = ttk.Label(self, width=38, anchor=CENTER)                           
        self.lbl_message.grid(row=2, column=0, columnspan=4, padx=PADX_BASE, 
                              pady=PADY_BASE, sticky="w")
        # Topics
        self.topics_to_pubsub()

    def send_configuration_data(self):
        base_time = self.entry_time.get()
        shots = self.entry_shots.get()
        right_pwm = self.entry_right_pwm.get()
        left_pwm = self.entry_left_pwm.get()

        correct_fields = base_time.isnumeric() and shots.isnumeric() and \
                         right_pwm.isnumeric() and left_pwm.isnumeric()
        if not correct_fields:
            self.lbl_message['text'] = "Hay campos vacios y/o no numericos"
            return None
        self.lbl_message['text'] = ""
        pub.sendMessage('start-game', base_time=base_time, shots=shots, 
                        right_pwm=right_pwm, left_pwm=left_pwm)

    def topics_to_pubsub(self):
        pub.subscribe(self.send_configuration_data, 'get-configuration-data')


class StartPanel(ttk.Labelframe):
    def __init__(self, root):
        super().__init__(root)

        # Settings
        self.lbl_tittle_frame = ttk.Label(self, text="Lanzamiento")
        self.configure(height=130, width=480, relief="groove" , borderwidth=2, 
                       labelwidget=self.lbl_tittle_frame)
        self.grid_propagate(0)

        # Widgets
        # Start button
        btn_start = ttk.Button(self, text="Iniciar", 
                                    command=self.btn_start_clicked)
        btn_start.grid(row=0, column=0, padx=PADX_BASE, pady=PADY_BASE)

        # Stop button
        btn_stop = ttk.Button(self, text="Detener", 
                                   command=self.btn_stop_clicked)
        btn_stop.grid(row=1, column=0, padx=PADX_BASE, pady=PADY_BASE)

        # Shot score
        lbl_shot_score_ = ttk.Label(self, width=18, text="Puntaje anotación", 
                                    anchor="e")
        lbl_shot_score_.grid(row=0, column=1, padx=PADX_BASE, pady=PADY_BASE, 
                             sticky="e")
        self.lbl_shot_score = ttk.Label(self, width=6, background="#ffffff", 
                                        relief=SUNKEN)
        self.lbl_shot_score.grid(row=0, column=2, padx=PADX_BASE, 
                                 pady=PADY_BASE, sticky="e")
        # Total score
        lbl_total_score_ = ttk.Label(self, width=18, text="Puntaje total", 
                                     anchor="e")
        lbl_total_score_.grid(row=1, column=1, padx=PADX_BASE, pady=PADY_BASE, 
                              sticky="e")
        self.lbl_total_score = ttk.Label(self, width=6, background="#ffffff", 
                                         relief=SUNKEN)
        self.lbl_total_score.grid(row=1, column=2, padx=PADX_BASE, 
                                  pady=PADY_BASE, sticky="e")
        # Message output
        self.lbl_message = ttk.Label(self, width=40, anchor=CENTER)                           
        self.lbl_message.grid(row=2, column=0, columnspan=3, padx=PADX_BASE, 
                              pady=PADY_BASE, sticky="w")
        # Topics
        self.topics_to_pubsub()

    def btn_start_clicked(self):
        pub.sendMessage('get-configuration-data')

    def btn_stop_clicked(self):
        pub.sendMessage('stop-game')
    
    def show_shot_score(self, shot_score):
        self.lbl_shot_score['text'] = shot_score

    def show_total_score(self, total_score):
        self.lbl_total_score['text'] = total_score

    def show_message(self, msg):
        self.lbl_message['text'] = msg

    def topics_to_pubsub(self):
        pub.subscribe(self.show_shot_score, 'show-shot-score')
        pub.subscribe(self.show_total_score, 'show-total-score')
        pub.subscribe(self.show_message, 'start-panel-msg')


class UserRegistrationWindow(Toplevel):
    def __init__(self, root):
        super().__init__(root)

        # Settings
        self.minsize(500, 200)
        self.maxsize(500, 200)
        self.title('Registro de Usuario')
        self.configure(background="#eff0f1", pady=40) 
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        style = ttk.Style(self)
        style.configure('TLabel', background='#eff0f1') 
        style.configure('TButton', background='#dcdcdc') 

        # Widgets
        # User Id
        lbl_user_id = ttk.Label(self, text = "Usuario ID", anchor="e", 
                                width=18)
        lbl_user_id.grid(row=0, column=0, padx=PADX_BASE, pady=PADY_BASE, 
                         sticky="e")
        self.entry_user_id = ttk.Entry(self, width=20)
        self.entry_user_id.grid(row=0, column=1, padx=PADX_BASE, 
                                pady=PADY_BASE)
        # User name
        lbl_user_name = ttk.Label(self, text = "Nombre")                           
        lbl_user_name.grid(row=1, column=0, padx=PADX_BASE, pady=PADY_BASE, 
                           sticky="e")
        self.entry_user_name = ttk.Entry(self, width=20)
        self.entry_user_name.grid(row=1, column=1, padx=PADX_BASE, 
                                  pady=PADY_BASE)
        # Register button
        btn_register = ttk.Button(self, text="Registrar", 
                      command=self.btn_register_clicked)
        btn_register.grid(row=2, column=0, padx=PADX_BASE, pady=PADY_BASE, 
                          sticky="e")
        # Message output
        self.lbl_message = ttk.Label(self, width=38, anchor=CENTER)                           
        self.lbl_message.grid(row=3, column=0, columnspan=2, padx=PADX_BASE, 
                              pady=PADY_BASE, sticky="e")
        # Topics
        self.topics_to_pubsub()

    def btn_register_clicked(self):
        user_id = self.entry_user_id.get()
        user_name = self.entry_user_name.get()
        if not user_id:
            self.lbl_message['text'] = "Escriba un ID de usuario"
            return None
        if not user_name:
            self.lbl_message['text'] = "Escriba un nombre de usuario"
            return None
        pub.sendMessage('register-user', id=user_id, name=user_name)

    def show_message(self, msg):
        self.lbl_message['text'] = msg

    def on_closing(self):
        pub.unsubscribe(self.show_message, 'registration-panel-msg')
        self.destroy()

    def topics_to_pubsub(self):
        pub.subscribe(self.show_message, 'registration-panel-msg')