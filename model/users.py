import firebase_admin
from datetime import datetime
from firebase_admin import credentials
from firebase_admin import firestore

# Firebase connection
CRED = credentials.Certificate('credentials.json')
firebase_admin.initialize_app(CRED)
DB = firestore.client()

# Models
class User():
    def __init__(self, id: str, name: str = None):
        self.id = id
        self.name = name

    @staticmethod
    def find_by_id(id: str) -> dict:
        doc_ref = DB.collection('registro').document(id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        else: 
            return None

    def save(self) -> dict:	
        doc_ref = DB.collection('registro').document(self.id)
        response = doc_ref.set({
            'nombre': self.name,
        })
        print(response)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict() 
        return None

class Result():
    def __init__(self, id: int, total_score: int, total_blue: int, 
                 total_red: int, total_green: int, total_white: int, 
                 average_time: int, average_total: int, sesion_id: int):
        self.id = id
        self.total_score = total_score
        self.total_blue = total_blue
        self.total_red = total_red
        self.total_green = total_green
        self.total_white = total_white
        self.average_time = average_time
        self.average_total = average_total
        self.sesion_id = sesion_id
        self.timestamp = datetime.now().timestamp()

    def save(self):
        self.timestamp = datetime.now().timestamp()
        doc_ref = DB.collection('usuarios').document(self.id)\
                  .collection("stats").document()
        response = doc_ref.set({
            'id':self.id,
            'score': self.total_score,
            'tblue': self.total_blue,
            'tred': self.total_red,
            'tgreen': self.total_green,
            'twhite': self.total_white,
            'taverages': self.average_time,
            'taveragetotal': self.average_total,
            'timestamp': self.timestamp,
            'idSesion': self.sesion_id
        })
        print(response)

    def __str__(self) -> str:
        data = {
            'id':self.id,
            'score': self.total_score,
            'tblue': self.total_blue,
            'tred': self.total_red,
            'tgreen': self.total_green,
            'twhite': self.total_white,
            'taverages': self.average_time,
            'taveragetotal': self.average_total,
            'timestamp': self.timestamp,
            'idSesion': self.sesion_id
        }
        return str(data)