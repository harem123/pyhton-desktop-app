from func_timeout import func_timeout, FunctionTimedOut
from pubsub import pub
from random import randint, choice
from serial.tools import list_ports
import time
import threading

from model import User, Result
from .serial_port import SerialPort

class Machine():
    available_cells = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
    
    def __init__(self, serial_object: SerialPort):
        self.serial_object = serial_object
        self.green_cell = -1
        self.blue_cell = -1
        self.white_cell = -1
        self.left_red_cell = -1
        self.right_red_cell = -1
        self.right_pwm = 150
        self.left_pwm = 150
        self.base_time = 3
        self.wall = 0
        self.blue_cell_score = 1
        self.green_cell_score = 2
        self.white_cell_score = 3
        self.red_cell_score = -1
        self.red_hits = 0
        self.green_hits = 0
        self.blue_hits = 0
        self.white_hits = 0
        self.response_time = 0
        self.shot_order_time = 0

    def define_cells_to_turn_on(self, green_enable=False, blue_enable=False, 
                                white_enable=False):
        available_cells = self.available_cells[:]
 
        self.wall = randint(0, 3)
        if(green_enable):
            self.green_cell = choice([randint(1, 6)] + [randint(9, 14)])
            self.left_red_cell = self.green_cell - 1
            self.right_red_cell = self.green_cell + 1
            del available_cells[self.green_cell]
            del available_cells[available_cells.index(self.left_red_cell)]
            del available_cells[available_cells.index(self.right_red_cell)]
        if(blue_enable):
            cell_index = randint(0, len(available_cells) - 1)
            self.blue_cell = available_cells[cell_index]
            del available_cells[cell_index]
        if(white_enable):
            cell_index = randint(0, len(available_cells) - 1)
            self.white_cell = available_cells[cell_index]
            del available_cells[cell_index]

    def send_order_new_shot(self):
        self.define_cells_to_turn_on(True, True, True)
        # Uncomment next 3 lines to test defined cells
        # self.green_cell = 14
        # self.blue_cell = 5
        # self.white_cell = 7
        order_string = ('{"cmd":1,"lg":%d,"lb":%d,"lw":%d,"R":%d,"L":%d,'
                        '"t":%d,"w":%d}')%(self.green_cell, self.blue_cell,
                        self.white_cell, self.right_pwm, self.left_pwm, 
                        self.base_time, self.wall)
        print("Order to send:", order_string)
        self.serial_object.write(order_string.encode('utf_8'))
        self.shot_order_time = time.time()

    def send_order_stop_machine(self):
        order_string = '{"cmd":3}'
        print("Order to send", order_string)
        self.serial_object.write(order_string.encode('utf_8'))

    def set_scores_by_cell_color(self, green_cell_score, blue_cell_score,
                                 white_cell_score, red_cell_score):
        self.green_cell_score = green_cell_score
        self.blue_cell_score = blue_cell_score
        self.white_cell_score = white_cell_score
        self.red_cell_score = red_cell_score

    def get_score_by_cell_color(self, cell_color: str):
        scores_by_color = {
            "r": self.red_cell_score,
            "g": self.green_cell_score,
            "b": self.blue_cell_score,
            "w": self.white_cell_score,
        }
        if(cell_color not in scores_by_color):
            return 0
        return scores_by_color[cell_color]

    def count_shots_by_color(self, cell_color: str):
        if cell_color == 'r':
            self.red_hits = self.red_hits + 1
        if cell_color == 'g':
            self.green_hits = self.green_hits + 1
        if cell_color == 'b':
            self.blue_hits = self.blue_hits + 1
        if cell_color == 'w':
            self.white_hits = self.white_hits + 1

    def get_time_since_shot_order(self):
        self.response_time = time.time() - self.shot_order_time
        return self.response_time

class Game():
    def __init__(self):
        self.shots = 0
        self.shot_score = 0
        self.total_score = 0
        self.session_id = 0
        self.session_times = []
        self.game_started = False
        self.send_shot_order = False
        self.serial_object = SerialPort()
        self.machine: Machine = None
        self.user: User = None # user model
        self.topics_to_pubsub()
        self.start_threads()

    def start_threads(self):
        serial_thread = threading.Thread(target = self.read_serial_port_thread, 
                                         daemon=True)
        game_thread = threading.Thread(target = self.game_thread, daemon=True)
        serial_thread.start()
        game_thread.start()

    def get_serial_ports(self):
        available_serial_ports = []
        for port, desc, hwid in sorted(list_ports.comports()):
            available_serial_ports.append(port)
        pub.sendMessage('show-available-ports', ports=available_serial_ports)

    def connect_to_serial_port(self):
        try:    
            self.serial_object.open()
            pub.sendMessage('connection-panel-msg', msg="Conexión exitosa")
        except:
            pub.sendMessage('connection-panel-msg', msg="Conexión fallida")
            print ("Can't Open Specified Port")

    def set_serial_port(self, port, baud):
        self.serial_object.port = port
        self.serial_object.baudrate = baud
        self.connect_to_serial_port()
        self.disconnect_serial_port()

    def disconnect_serial_port(self, show_msg=False):
        self.serial_object.close()
        print("serial port closed")
        if show_msg:
            pub.sendMessage('connection-panel-msg', msg="Puerto desconectado")

    def read_serial_port_thread(self):
        while True:
            if self.serial_object.is_open:
                try:
                    if self.serial_object.inWaiting() > 0:
                        json_received = self.serial_object.readjson()
                        self.classify_commands_received(json_received)
                except Exception as e:
                    self.stop_game_by_exception(msg="Problema al leer puerto. " 
                        "Juego detenido", error=e)
            time.sleep(0.1)

    def classify_commands_received(self, json_command):
        if "err" in json_command:
            self.game_started = False
            self.disconnect_serial_port()
            pub.sendMessage('start-panel-msg', 
                        msg="Error de comunicación. Juego detenido")
            print("Communication error")
            return
        command_id = json_command['cmd']
        if command_id == 4:
            cell_collor_sensed = json_command["c"]
            self.session_times.append(self.machine.get_time_since_shot_order())
            self.machine.count_shots_by_color(cell_collor_sensed)
            self.shot_score = self.machine.get_score_by_cell_color(
                                                        cell_collor_sensed)
            self.send_shot_order = True

    def try_write(self, func):
        """Validate in a try block if the received function can 
        write correctly to the serial port 

        Args:
            func (_type_): function that write in serial port
        """
        try:
            func()
        except Exception as e:
            self.stop_game_by_exception(msg="Problema al escribir puerto. "
                "Juego detenido", error=e)

    def start_game(self, base_time, shots, right_pwm, left_pwm):
        self.shots = int(shots)
        
        # Validate serial communication
        self.connect_to_serial_port()
        if not self.serial_object.is_open:
            pub.sendMessage('start-panel-msg', 
                            msg="Comunicación serial no configurada")
            return None

        # Configure machine
        self.machine = Machine(self.serial_object)
        self.machine.base_time = int(base_time)
        self.machine.right_pwm = int(right_pwm)
        self.machine.left_pwm = int(left_pwm)
        self.machine.set_scores_by_cell_color(3, 1, 5, -1)
        
        # start game
        self.session_id = 0 # TODO define session id
        self.session_times = []
        print("Game started")
        self.game_started = True
        pub.sendMessage('start-panel-msg', msg="Juego en curso")

    def game_thread(self):
        while True:
            counter_shots = 0
            self.shot_score = 0
            self.total_score = 0
            self.send_shot_order = True 
            while self.game_started:
                if self.send_shot_order:
                    # Last shot scores
                    self.total_score = self.shot_score + self.total_score
                    pub.sendMessage('show-shot-score', 
                                    shot_score=self.shot_score)
                    pub.sendMessage('show-total-score', 
                                        total_score=self.total_score)
                    # Verifiy if game is completed
                    if counter_shots == self.shots:
                        self.game_started = False
                        print("Shots completed")
                        self.disconnect_serial_port()
                        pub.sendMessage('start-panel-msg', 
                                        msg="Tiros completados")
                        self.save_stats() # save to database
                        continue

                    # New shot
                    time.sleep(0.5)
                    self.try_write(self.machine.send_order_new_shot)
                    self.send_shot_order = False
                    counter_shots = counter_shots + 1
                time.sleep(0.01)
            time.sleep(0.1)

    def save_stats(self):
        pub.sendMessage('start-panel-msg', msg="Guardando resultados...")
        if not self.user:
            pub.sendMessage('start-panel-msg', 
                        msg="Resultados no guardados. Usuario no configurado")
            return None

        average_time_by_hit = sum(self.session_times) / \
                                len(self.session_times)
        avarage_score_by_hit = self.total_score / len(self.session_times)
        result = Result(self.user.id, self.total_score,
                        self.machine.blue_hits, self.machine.red_hits,
                        self.machine.green_hits, self.machine.white_hits,
                        average_time_by_hit, avarage_score_by_hit, 
                        self.session_id)
        try:
            func_timeout(10, result.save)
            print("stats saved")
            msg = "Datos del usuario " + self.user.id + " guardados"
            pub.sendMessage('start-panel-msg', msg=msg)
        except FunctionTimedOut:
            print("Connection to firebase is lost")
            pub.sendMessage('start-panel-msg', 
                    msg="Error al guardar. El servicio tardó en responder")
        print(result)

    def stop_game(self):
        self.game_started = False
        if self.machine and self.serial_object.is_open:
            self.try_write(self.machine.send_order_stop_machine)
        pub.sendMessage('start-panel-msg', msg="Juego detenido")
        print("Game stopped")

    def stop_game_by_exception(self, msg: str = None, error: Exception = None):
        """Execute the necessary actions when the game is 
        stopped by an exception

        Args:
            msg (str, optional): message to send to game panel. 
            Defaults to None.
            error (Exception, optional): error details to print to console. 
            Defaults to None.
        """
        self.game_started = False
        self.disconnect_serial_port(True)
        print("Error: Game stopped")
        if msg:
            pub.sendMessage('start-panel-msg', msg=msg)
        if error:
            print("Error details:", error)
        
    def get_user_by_id(self, id: str) -> tuple[User, Exception]:
        id_ = str(id)
        try:
            user = func_timeout(5, User.find_by_id, args=(id_,))
            return user, None
        except FunctionTimedOut as err:
            return None, err

    def verify_user(self, id: str):
        id = str(id)
        self.user = None
        user, err = self.get_user_by_id(id)
        if err:
            pub.sendMessage('user-panel-msg', 
                             msg="Error, el servicio tardó en responder")
            print("Connection to firebase is lost")
            return None

        if user:
            self.user = User(id, user['nombre'])
            pub.sendMessage('show-user-data', name=user['nombre'])
            print("User validated")
        else:
            pub.sendMessage('user-panel-msg', msg="Usuario no existe")
            print("User doesn't exist")

    def register_user(self, id: str, name: str):
        user, err = self.get_user_by_id(id)
        if err:
            pub.sendMessage('registration-panel-msg', 
                             msg="Error, el servicio tardó en responder")
            print("Connection to firebase is lost")
            return None
        if user:
            pub.sendMessage('registration-panel-msg', msg="Usuario ya existe")
            print("User already exists")
            return None

        user = User(id, name)
        try:
            response = func_timeout(10, user.save)
            if response:
                pub.sendMessage('registration-panel-msg', 
                                msg="Registro exitoso")
                print("Successful registration")
            else:
                pub.sendMessage('registration-panel-msg', 
                                msg="Registro fallido")
                print("Error in registration")
        except FunctionTimedOut:
            pub.sendMessage('registration-panel-msg', 
                        msg="Registro fallido, el servicio tardó en responder")
            print("Connection to firebase is lost")

    # Events
    def topics_to_pubsub(self):
        pub.subscribe(self.get_serial_ports, 'get-available-ports')
        pub.subscribe(self.set_serial_port, 'set-serial-port')
        pub.subscribe(self.disconnect_serial_port, 'disconnect-serial-port')
        pub.subscribe(self.start_game, 'start-game')
        pub.subscribe(self.stop_game, 'stop-game')
        pub.subscribe(self.verify_user, 'verify-user')
        pub.subscribe(self.register_user, 'register-user')