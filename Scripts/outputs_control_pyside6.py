from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QMessageBox, QCheckBox
from snap7.types import S7CpuInfo
import snap7.util
import snap7.client
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Siemens x Python")
        self.setMinimumSize(800, 400)
        self.db_number = 1 #index of DB / index de la base de données 
        self.client = snap7.client.Client()
        self.connected = False

        self.label_IPadress = QLabel("Adresse IP CPU", self)
        self.label_IPadress.move(10, 5)
        self.entry_IPadress = QLineEdit(self)
        self.entry_IPadress.move(10, 30)

        self.label_Rack = QLabel("Rack", self)
        self.label_Rack.move(230, 5)
        self.entry_Rack = QLineEdit(self)
        self.entry_Rack.move(200, 30)

        self.label_Slot = QLabel("Slot", self)
        self.label_Slot.move(425, 5)
        self.entry_Slot = QLineEdit(self)
        self.entry_Slot.move(390, 30)

        self.btn_connect = QPushButton("Connecter", self)
        self.btn_connect.clicked.connect(self.toggle_connection)
        self.btn_connect.move(10, 70)

        self.status_label = QLabel(self)
        self.status_label.setGeometry(100, 70, 15, 15)
        self.status_label.setStyleSheet("background-color: #D60000; border-radius: 7px; border: 0.5px solid black;")  # Set style

        self.checkbox_layout = []
        self.checkbox_color_labels = []

        for x in range(4):
            for i in range(8):
                checkbox = QCheckBox(f"Q{x}.{i}", self)
                checkbox.move(10 + i * 100, 100 + x * 50)
                checkbox.stateChanged.connect(self.toggle_color)
                self.checkbox_layout.append(checkbox)
                
                color_label = QLabel(self)
                color_label.setGeometry(50 + i * 100 + 20, 105 + x * 50 + 5, 10, 10)  # Adjust position
                color_label.setStyleSheet("background-color: black; border: 1px solid black;")  # Set style
                self.checkbox_color_labels.append(color_label)
            

        self.btn_set_all = QPushButton("SET ALL", self)
        self.btn_set_all.clicked.connect(self.set_all_checked)
        self.btn_set_all.move(10, 280)

        self.btn_reset_all = QPushButton("RESET ALL", self)
        self.btn_reset_all.clicked.connect(self.rst_all_checked)
        self.btn_reset_all.move(150, 280)
    

    # Function to verify if an IP address is valid / Fonction pour vérifier si l'adresse IP est valide
    def verifier_ip(self, ip):
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
    def connect(self):
        try:
            ip = self.entry_IPadress.text()
            rack = int(self.entry_Rack.text())
            slot = int(self.entry_Slot.text())

            if not self.verifier_ip(ip):
                QMessageBox.critical(self, "Erreur", "Adresse IP invalide")
                return

            self.client.connect(ip, rack, slot)
            cpu_info: S7CpuInfo = self.client.get_cpu_info()
            cpu_tab = str(cpu_info).split("'")
            QMessageBox.information(self, "Connecté", f"Connexion réussie : {cpu_tab[1]}")
            self.connected = True
            self.update_button_color()
            print(self.client.list_blocks())
        except Exception as e:
            print("Connexion CPU impossible:", e)
            QMessageBox.critical(self, "Erreur de connexion", "La tentative de connexion à la CPU a échoué. "
                                                               "Veuillez vérifier votre adresse!")
            self.connected = False
            self.update_button_color()

    # Function to write a boolean value to a PLC address / Fonction pour écrire une valeur booléenne à une adresse PLC
    def writeBool(self, db_number, start_offset, bit_offset, value):
        reading = self.client.db_read(db_number, start_offset, 1)
        snap7.util.set_bool(reading, 0, bit_offset, value)
        self.client.db_write(db_number, start_offset, reading)

    # Function to toggle background color of checkboxes / Fonction pour basculer la couleur de fond des cases à cocher
    def toggle_color(self):
        for i, checkbox in enumerate(self.checkbox_layout):
            if checkbox.isChecked():
                self.checkbox_color_labels[i].setStyleSheet("background-color: green; border: 1px solid black;")
            else:
                self.checkbox_color_labels[i].setStyleSheet("background-color: black; border: 1px solid black;")
        self.read_write_Qx()

    # Function to set all checkboxes to True / Fonction pour définir toutes les cases à cocher à True
    def set_all_checked(self):
        for checkbox in self.checkbox_layout:
            checkbox.setChecked(True)
        self.toggle_color()

    # Function to set all checkboxes to False / Fonction pour définir toutes les cases à cocher à False
    def rst_all_checked(self):
        for checkbox in self.checkbox_layout:
            checkbox.setChecked(False)
        self.toggle_color()

    # Function to read or write to Qx variables / Fonction pour lire ou écrire dans les variables Qx
    def read_write_Qx(self):
        try:
            for x in range(4):
                for i in range(8):
                    checked = self.checkbox_layout[x * 8 + i].isChecked()
                    self.writeBool(self.db_number, x, i, checked)
                    print(f"Q{x}.{i}: {checked}")
        except Exception as e:
            print("Erreur lors de la lecture/écriture de la variable Qx:", e)

    # Function to update the button color based on connection status / Fonction pour mettre à jour la couleur du bouton en fonction de l'état de la connexion
    def update_button_color(self):
        if self.connected:
            self.status_label.setGeometry(100, 70, 15, 15)
            self.status_label.setStyleSheet("background-color: #36ED04 ; border-radius: 7px; border: 0.5px solid black;") 
        else:
            self.status_label.setGeometry(100, 70, 15, 15)
            self.status_label.setStyleSheet("background-color: #D60000; border-radius: 7px; border: 1px solid black;")  # Set style

    # Function to toggle connection / Fonction pour basculer la connexion
    def toggle_connection(self):
        if not self.connected:
            self.connect()
        else:
            # Add code here to close the connection / Ajouter du code ici pour fermer la connexion
            self.client.disconnect()
            self.connected = False
            self.update_button_color()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
