import tkinter as tk
from tkinter import ttk
import psutil # Debes instalarlo: pip install psutil

class App:
    def __init__(self, root):
        root.title("Monitor & Simulador SO - Equipo XX")
        root.geometry("800x600")
        
        self.label = tk.Label(root, text="Procesos Reales del Sistema", font=('Arial', 14, 'bold'))
        self.label.pack(pady=10)

        # Tabla para mostrar procesos
        self.tree = ttk.Treeview(root, columns=("PID", "Nombre", "CPU %"), show='headings')
        self.tree.heading("PID", text="PID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("CPU %", text="CPU %")
        self.tree.pack(fill='both', expand=True)

        self.actualizar_procesos()

    def actualizar_procesos(self):
        # Limpiar tabla
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        # Obtener procesos reales
        for proc in list(psutil.process_iter(['pid', 'name', 'cpu_percent']))[:15]:
            self.tree.insert("", "end", values=(proc.info['pid'], proc.info['name'], proc.info['cpu_percent']))
        
        # Refrescar cada 5 segundos
        root.after(5000, self.actualizar_procesos)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()