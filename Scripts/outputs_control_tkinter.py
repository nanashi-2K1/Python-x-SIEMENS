import snap7
from snap7.types import S7CpuInfo
import tkinter as tk
from tkinter import messagebox

root = tk.Tk()
root.title("Siemens x Python")
root.wm_minsize(600, 600)

# Default values for PLC connection
db_number = 1 # index of DB / index du bloc de données 
start_offset = 0
client = snap7.client.Client()

# Function to verify if an IP address is valid / Fonction pour vérifier si l'adresse IP est valide
def verifier_ip(ip):
    octets = ip.split(".")
    if len(octets) != 4:
        return False
    for octet in octets:
        try:
            octet = int(octet)
            if octet < 0 or octet > 255:
                return False
        except ValueError:
            return False
    return True

# Function to establish a connection to the PLC / Fonction pour établir une connexion au PLC
def connect():
    try:
        ip = entry_IPadress.get()
        rack = int(entry_Rack.get())
        slot = int(entry_Slot.get())

        if not verifier_ip(ip):
            messagebox.showerror("Erreur", "Adresse IP invalide")
            return

        client.connect(ip, rack, slot)
        cpu_info: S7CpuInfo = client.get_cpu_info()
        print(cpu_info)
        cpu_info = str(client.get_cpu_info())
        cpu_tab = cpu_info.split("'")
        messagebox.showinfo("Connecté", "Connexion réussie : " + str(cpu_tab[1]))
        print(client.list_blocks())
    except Exception as e:
        print("Connexion CPU impossible:", e)
        messagebox.showerror("Erreur de connexion", "La tentative de connexion à la CPU a échoué. "
                                                    "Veuillez vérifier votre adresse!")

# Function to write a boolean value to a PLC address / Fonction pour écrire une valeur booléenne à une adresse PLC
def writeBool(db_number, start_offset, bit_offset, value):
    reading = client.db_read(db_number, start_offset, 1)
    snap7.util.set_bool(reading, 0, bit_offset, value)
    client.db_write(db_number, start_offset, reading)
    return None

# Function to read a boolean value from a PLC address / Fonction pour lire une valeur booléenne à partir d'une adresse PLC
def readBool(db_number, start_offset, bit_offset):
    reading = client.db_read(db_number, start_offset, 1)
    a = snap7.util.get_bool(reading, 0, bit_offset)
    print('DB Number: ' + str(db_number) + ' Bit: ' + str(start_offset) + '.' + str(bit_offset) + ' Value: ' + str(a))
    return None

# Function to read or write to Qx variables / Fonction pour lire ou écrire dans les variables Qx
def read_write_Qx():
    try:
        for x in range(4):
            for i in range(8):
                variable = f"Q{x}.{i}"
                checked = var_list[x*8 + i].get()
                writeBool(db_number, x, i, bool(checked))
                print(f"{variable}: {bool(checked)}")
    except Exception as e:
        print("Erreur lors de la lecture/écriture de la variable Qx:", e)

# Function to toggle background color of checkboxes / Fonction pour basculer la couleur de fond des cases à cocher
def toggle_color():
    for i, var in enumerate(var_list):
        if var.get() == 1:
            checkboxes[i].configure(background="green")
        else:
            checkboxes[i].configure(background="white")
    read_write_Qx()

# Function to set all checkboxes to True / Fonction pour définir toutes les cases à cocher à True
def set_all_checked():
    for var in var_list:
        var.set(True)
    toggle_color()

# Function to set all checkboxes to False / Fonction pour définir toutes les cases à cocher à False
def rst_all_checked():
    for var in var_list:
        var.set(False)
    toggle_color()

# GUI components / Composants de l'interface graphique
label_IPadress = tk.Label(root, text="Adresse IP CPU ")
label_IPadress.grid(row=0, column=0, padx=10, pady=5)
entry_IPadress = tk.Entry(root)
entry_IPadress.grid(row=1, column=0, padx=10, pady=5)

label_Rack = tk.Label(root, text="Rack ")
label_Rack.grid(row=0, column=2, padx=10, pady=5)
entry_Rack = tk.Entry(root)
entry_Rack.grid(row=1, column=2, padx=10, pady=5)

label_Slot = tk.Label(root, text="Slot ")
label_Slot.grid(row=0, column=4, padx=10, pady=5)
entry_Slot = tk.Entry(root)
entry_Slot.grid(row=1, column=4, padx=10, pady=5)

var_list = []
checkboxes = []
for x in range(4):
    for i in range(8):
        var = tk.IntVar()
        checkbox = tk.Checkbutton(root, text=f"Q{x}.{i}", variable=var, command=toggle_color)
        checkbox.grid(row=5+x, column=i, padx=10, pady=10, sticky='w')
        var_list.append(var)
        checkboxes.append(checkbox)

btn_connect = tk.Button(root, text="Connecter", command=connect)
btn_connect.grid(row=10, column=3, columnspan=1, padx=5, pady=5)

btn_checked_all = tk.Button(root, text="SET ALL", command=set_all_checked)
btn_checked_all.grid(row=10, column=4, columnspan=1, padx=5, pady=5)

btn_checked_all = tk.Button(root, text="RESET ALL", command=rst_all_checked)
btn_checked_all.grid(row=10, column=2, columnspan=1, padx=5, pady=5)

root.mainloop()
