import snap7

# Create a new client instance
client = snap7.client.Client()

try:
    # Attempt to connect to the PLC / Tenter de se connecter au PLC
    client.connect("192.168.0.12", 0, 2)

    # Retrieve and print a list of blocks in the PLC / Récupérer et afficher une liste des blocs dans le PLC
    print("List of Blocks:")
    print(client.list_blocks())

    # Get CPU information / Obtenir les informations sur le CPU
    cpu_info = str(client.get_cpu_info())
    cpu_tab = cpu_info.split("'")

    # Iterate through the CPU information and print details / Parcourir les informations sur le CPU et afficher les détails
    l = len(cpu_tab)
    for i in range(l):
        if i % 2 == 0:
            pass
        if i % 2 != 0:
            # Print CPU details / Afficher les détails du CPU
            print(cpu_tab[i - 1], " ==> ", cpu_tab[i])
            pass
except Exception as e:
    # Handle connection errors / Gérer les erreurs de connexion
    print("Connection error\nPartner not found")
