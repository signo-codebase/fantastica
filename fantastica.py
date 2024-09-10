import argparse
import os
from colorama import init, Fore, Back, Style
from fantastica_module import FantaAllenatore, FantaCalciatore, Lega, load_data

# Initialize colorama
init(autoreset=True)

# Global variable to keep the league in memory
lega = None

def initialize_league():
    """Initialize a new league and set the global `lega` variable."""
    global lega
    print(Fore.CYAN + "Inserisci il nome della lega: " + Style.RESET_ALL, end="")
    nome_lega = input()
    print(Fore.CYAN + "Quanti allenatori ci sono? " + Style.RESET_ALL, end="")
    numero_allenatori = 0
    while numero_allenatori < 2 or numero_allenatori > 12:
        numero_allenatori = int(input())
        
    allenatori = []
    for i in range(numero_allenatori):
        print(Fore.CYAN + f"Inserisci il nome dell'allenatore {i+1}: " + Style.RESET_ALL, end="")
        nome_allenatore = input()
        allenatori.append(nome_allenatore)

    print(Fore.CYAN + f"Inserisci il nome del file excel: " + Style.RESET_ALL, end="")
    lega = Lega(nome=nome_lega, allenatori=allenatori)
    lega.inizia_fantacalcio()  # Initialize FantaAllenatori objects
    print(Fore.GREEN + "Lega inizializzata." + Style.RESET_ALL)

def process_command(command):
    """Process a single command from the user."""
    global lega  # Declare that we are using the global `lega` variable

    parts = command.split(maxsplit=4)
    if not parts:
        return

    if len(parts) > 1 and parts[1] in ["compra", "svincola", "rimuove"]:
        action = parts[1]
    else:
        action = parts[0]

#---------------------------------INIT------------------------------------------#

    if action == "init":
        initialize_league()
        return

    if action == "save":
        if lega is None:
            print(Fore.RED + "Non ci sono leghe da salvare. Crea una lega prima di salvarla." + Style.RESET_ALL)
        else:
            lega.save()
            print(Fore.GREEN + f"Lega salvata in {lega.nome}.pkl" + Style.RESET_ALL)
        return
    
#---------------------------------LOAD------------------------------------------#

    if action == "load":
        if len(parts) < 2:
            print(Fore.RED + "Devi specificare un nome di file." + Style.RESET_ALL)
            return
        filename = parts[1] + ".pkl"
        if not os.path.isfile(filename):
            print(Fore.RED + "File non trovato." + Style.RESET_ALL)
            return
        lega = Lega.load(filename)
        if lega is not None:
            print(Fore.GREEN + f"Lega caricata da {filename}." + Style.RESET_ALL)
        else:
            print(Fore.RED + "Impossibile caricare la lega." + Style.RESET_ALL)
        return

    # Ensure the league is initialized
    if lega is None:
        print(Fore.RED + "Devi inizializzare una lega prima di eseguire azioni." + Style.RESET_ALL)
        return


#------------------------------------INFO------------------------------------------#


    # Handle info action
    if action == "info":
        
        # controllo
        if len(parts) < 2:
            print(Fore.RED + "Opzioni: allenatore, lega, svincolati, calciatore" + Style.RESET_ALL)
            return


        # info allenatore
        if parts[1] in [a.nome for a in lega.allenatori]:
            print(Fore.CYAN + lega.get_allenatore(parts[1]) + Style.RESET_ALL)
            return
        

        # info lega
        elif parts[1] == "lega":
            print(Fore.CYAN + lega.dettagli() + Style.RESET_ALL)


        # info svincolati
        elif parts[1] == "svincolati":

            if len(parts) == 2:
                print(Fore.CYAN + lega.display_svincolati() + Style.RESET_ALL)
                print("\n")
                return
            
            if len(parts) == 3:
                ruoli = ["porta", "difesa", "centrocampo", "attacco",
                         "P", "D", "C", "A"]
                if parts[2] not in ruoli:
                    print(Fore.RED + f"Ruolo non valido" + Style.RESET_ALL)
                    return
                print(Fore.CYAN + lega.display_svincolati(ruolo=parts[2]) + Style.RESET_ALL)
                print("\n")
            else:
                print(Fore.RED + f"Troppi argomenti" + Style.RESET_ALL)
            return
        

        # info giocatore
        else:
            calciatore_nome = ' '.join(parts[1:])  # Join the rest of the parts to handle multi-word names
            if calciatore_nome in lega.df['Nome'].values:
                dati_calciatore = lega.df[lega.df['Nome'] == calciatore_nome].iloc[0]
                calciatore = FantaCalciatore(
                    Nome=dati_calciatore['Nome'],
                    lega=lega,
                    ruolo=dati_calciatore['Ruolo'],
                    fascia=dati_calciatore.get('Fascia', None),
                    quotazione=dati_calciatore['FM/500']
                )
                print(Fore.CYAN + str(calciatore) + Style.RESET_ALL)
            else:
                print(Fore.RED + f"Calciatore {calciatore_nome} non trovato." + Style.RESET_ALL)
        return


#------------------------------------MERCATO------------------------------------------#


    # Handle compra, svincola, rimuove actions
    if action in ["compra", "svincola", "rimuove"]:
        if len(parts) < 3:
            print(Fore.RED + "Devi specificare il nome dell'allenatore e il nome del calciatore." + Style.RESET_ALL)
            return

        allenatore_nome = parts[0]
        calciatore_nome_parts = parts[2:]

        # Separate the price if it is present in the command
        prezzo = None
        if calciatore_nome_parts[-1].isdigit():
            prezzo = int(calciatore_nome_parts.pop())
        
        calciatore_nome = ' '.join(calciatore_nome_parts)

        allenatore = next((a for a in lega.allenatori if a.nome == allenatore_nome), None)

        if allenatore is None:
            print(Fore.RED + f"Allenatore {allenatore_nome} non trovato." + Style.RESET_ALL)
            return

        try:
            calciatore = FantaCalciatore(Nome=calciatore_nome, lega=lega)
        except ValueError as e:
            print(Fore.RED + str(e) + Style.RESET_ALL)
            return

        if action == "compra":
            if prezzo is None:
                print(Fore.RED + "Devi specificare il prezzo per l'acquisto." + Style.RESET_ALL)
                return
            esito = allenatore.compra(calciatore, prezzo, lega)
            lega.save()
            match esito:
                case 1:
                    print(Back.GREEN + f"FLASH NEWS ---> {allenatore_nome} ha comprato {calciatore_nome} per {prezzo} fm!" + Style.RESET_ALL)
                case 2:
                    print(Back.RED + f"Non hai abbastanza fm!" + Style.RESET_ALL)
                case 3:
                    print(f"{calciatore_nome} non è disponibile per l'acquisto.")
            return
        elif action == "svincola":
            esito = allenatore.svincola(calciatore, lega)
            lega.save()
            if esito is None:
                print(Back.RED + f"Calciatore non presente nella rosa di {allenatore_nome}" + Style.RESET_ALL)
            else:
                print(Back.MAGENTA + f"FLASH NEWS ---> {allenatore_nome} ha svincolato {calciatore_nome} recuperando {esito} fm" + Style.RESET_ALL)
                return
        elif action == "rimuove":
            esito = allenatore.rimuovi(calciatore, lega)
            lega.save()
            match esito:
                case 1:
                    print(Back.CYAN + f"FLASH NEWS ---> {allenatore_nome} ha rimosso {calciatore_nome}" + Style.RESET_ALL)
                case 2:
                    print(Back.RED + f"Giocatore non presente nella rosa di {allenatore_nome}" + Style.RESET_ALL)
            return

        # Save the league after performing any of these actions

def main():
    global lega

    # Check for command-line arguments
    parser = argparse.ArgumentParser(description="Gestione Fantacalcio")
    parser.add_argument("--file", help="Nome del file per caricare la lega all'avvio")
    args = parser.parse_args()

    if args.file:
        if os.path.isfile(args.file):
            lega = Lega.load(args.file)
            if lega is not None:
                print(Fore.GREEN + f"Lega caricata da {args.file}." + Style.RESET_ALL)
            else:
                print(Fore.RED + "Impossibile caricare la lega." + Style.RESET_ALL)
        else:
            print(Fore.RED + "File non trovato." + Style.RESET_ALL)

    print(Fore.GREEN + "Benvenuto nel gestore di Fantacalcio." + Style.RESET_ALL)
    print(Fore.CYAN + "Per iniziare a giocare, usa 'init'." + Style.RESET_ALL)
    print(Fore.CYAN + "Per eseguire altre azioni, usa comandi come 'compra', 'svincola', 'rimuovi', 'info', 'save', 'load'." + Style.RESET_ALL)
    print(Fore.CYAN + "Per uscire, usa 'exit' o 'quit'." + Style.RESET_ALL)

    while True:
        command = input(Fore.CYAN + "> " + Style.RESET_ALL)
        if command.lower() in ["exit", "quit"]:
            break
        process_command(command)

if __name__ == "__main__":
    main()
