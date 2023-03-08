import json
from json.decoder import JSONDecodeError
from serial import Serial
import time


class SerialPort(Serial):

    def __init__(self, port=None, baudrate=9600):
        super().__init__(None, baudrate)
        self.port = port

    def open(self):
        super().open()
        time.sleep(0.01)
        self.reset_input_buffer()
        print("successful connection to port", self.port, "baud", self.baudrate)

    # def readline_ascii(self) -> str:
    #     if self.is_open:
    #         data_received = self.readline()
    #         try:
    #             data_received.decode("ascii").strip("\n\r")
    #             return data_received
    #         except Exception as e:
    #             print("conversion from", data_received,
    #                     "to ASCII failed")
    #             print(e)
    #     return None

    def readline_ascii(self) -> str:
        if self.is_open:
            data_received = self.readline()
            try:
                data_received.decode("ascii").strip("\n\r")
                return data_received
            except Exception as e:
                print("conversion from", data_received,
                        "to ASCII failed")
                raise
        return None

    def readjson(self) -> json:
        data = ""
        json_data = None
        while not json_data:
            while not data:
                data = self.readline_ascii()
            try:
                json_data = json.loads(data)
                print("Json received:", json_data)
            except JSONDecodeError as e:
                print('String', data,'is not in json format')
                raise
        return json_data