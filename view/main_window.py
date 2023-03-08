import tkinter as tk
from tkinter import ttk 

from view import ConfigurationPanel, ConnectionPanel
from view import StartPanel, UserPanel


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.minsize(500, 520)
        self.title('GOAL LAB')
        self.configure(background="#eff0f1") 
        self.columnconfigure(0, weight=1)
        
        style = ttk.Style(self)
        style.configure('TLabelframe', background='#eff0f1') 
        style.configure('TLabel', background='#eff0f1') 
        style.configure('TButton', background='#dcdcdc') 

        connectionPanel = ConnectionPanel(self)
        connectionPanel.grid(row=0, column=0, padx=10, pady=10)

        userPanel = UserPanel(self)
        userPanel.grid(row=1, column=0, padx=10, pady=10)

        configurationPanel = ConfigurationPanel(self)
        configurationPanel.grid(row=2, column=0, padx=10, pady=10)

        startPanel = StartPanel(self)
        startPanel.grid(row=3, column=0, padx=10, pady=10)