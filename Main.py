import tkinter as tk

# Importation de la classe principale de l'interface depuis interface.py
from interface import FloydWarshallApp

if __name__ == "__main__":
    root = tk.Tk()
    app = FloydWarshallApp(root)
    root.mainloop()

