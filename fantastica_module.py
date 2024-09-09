import pandas as pd
import math
import os
import pickle

default_fm = 500  # TODO fare un modo per poter scegliere se 500 o 1000 fm di default

def load_data():
    current_directory = os.getcwd()
    filename = input() + ".xlsx"
    file_path = os.path.join(current_directory, filename)
    data = pd.read_excel(file_path)
    try:
        # gestioni delle quotazioni in base ai fm totali
        if default_fm == 500:
            if 'FVM' in data.columns:
                ruolo_column = 'Ruolo' if 'Ruolo' in data.columns else 'R'
                df = pd.DataFrame(data, columns=["Nome", ruolo_column, "FVM"])
                df['FVM'] = [math.floor(x * 0.5) for x in df['FVM']]
                df.rename(columns={'FVM': 'FM/500'}, inplace=True)
            elif 'FM/500' in data.columns:
                ruolo_column = 'Ruolo' if 'Ruolo' in data.columns else 'R'
                df = pd.DataFrame(data, columns=["Nome", ruolo_column, "FM/500"])
        elif default_fm == 1000:
            ruolo_column = 'Ruolo' if 'Ruolo' in data.columns else 'R'
            df = pd.DataFrame(data, columns=["Nome", ruolo_column, "FVM"])
            df.rename(columns={'FVM': 'FM/1000'}, inplace=True)

        if ruolo_column == 'R':
            df.rename(columns={'R': 'Ruolo'}, inplace=True)

        # importa data sulla fascia se presente nel file excel
        if 'Fascia' in data.columns:
            df['Fascia'] = data['Fascia'].apply(lambda x: x if x in [1, 2, 3, 4] else None)
        else:
            df['Fascia'] = None
        
        # importa data sui rigori se presente nel file excel
        if 'Rigorista' in data.columns:
            df['Rigorista'] = data['Rigorista']
        else:
            df['Rigorista'] = None
        
        # impostazioni di default su squadra e prezzo
        df['Stato'] = 'Svincolato' # crea lo stato di Svincolato default per ogni giocatore
        df['Prezzo'] = None # di default non si hanno dati sul prezzo

        return df
    
    except FileNotFoundError:
        print(f"File {filename} not found in {current_directory}.")
        return None


class FantaAllenatore:
    def __init__(self, nome, rosa=None, fm=default_fm, score=0):
        self.nome = nome
        self.fm = fm
        self.score = score
        self.rosa = rosa if rosa is not None else []

    def __str__(self):
        # Sort rosa based on role_order
        role_order = {"P": 1, "D": 2, "C": 3, "A": 4}
        sorted_rosa = sorted(self.rosa, key=lambda x: role_order.get(x.ruolo, 5))
        rosa_str = '\n'.join(f'   {calciatore.ruolo} - {calciatore.Nome} ({calciatore.prezzo} fm)' for calciatore in sorted_rosa)

        return (f'{self.nome}\n'
                f'FM: {self.fm}\n'
                f'Score: {self.score}\n'
                f'Rosa:\n{rosa_str}')

    def compra(self, calciatore, prezzo, lega):
        if calciatore.squadra != 'Svincolato':
            return 3  # Player already in a team
        elif self.fm < prezzo:
            return 2  # Not enough funds
        else:
            self.fm -= prezzo
            self.rosa.append(calciatore)
            calciatore.squadra = self.nome  # Update the player's team
            calciatore.prezzo = prezzo
            self.__aggiorna_score(calciatore, True)
            lega.aggiorna_calciatore(calciatore, self.nome, prezzo)  # Update the DataFrame
            return 1  # Purchase successful
    
    def __aggiorna_score(self, calciatore, compra=True):
        # Dictionary to map roles to their corresponding strategy
        role_strategy_map = {
            'P': PortiereScoreStrategy(),
            'D': DifensoreScoreStrategy(),
            'C': CentrocampistaScoreStrategy(),
            'A': AttaccanteScoreStrategy()
        }
        
        # Get the strategy based on the player's role
        strategy = role_strategy_map.get(calciatore.ruolo)

        if strategy:
            # Calculate the score based on fascia and rigori
            score = strategy.calculate_score(calciatore.fascia, calciatore.rigori)
            
            if calciatore.prezzo < calciatore.quotazione * 0.8:
                score += 2
            elif calciatore.prezzo > calciatore.quotazione * 1.3:
                score -= 2

            # Update the FantaAllenatore's score
            if compra is True:
                self.score += score
                print(f'+{score} di score per {calciatore.Nome}')
            elif compra is False:
                self.score -= score



    def rimuovi(self, calciatore, lega):
        match = next((c for c in self.rosa if c.Nome == calciatore.Nome), None)
        if match:
            self.rosa.remove(match)
            self.fm += match.prezzo
            match.squadra = None
            self.__aggiorna_score(calciatore, False)
            lega.aggiorna_calciatore(match, 'Svincolato')  # Update the DataFrame
            return 1
        else:
            # calciatore non in rosa
            return 2

    def svincola(self, calciatore, lega):
        match = next((c for c in self.rosa if c.Nome == calciatore.Nome), None)
        if match:
            self.rosa.remove(match)
            restituiti_fm = match.prezzo if match.prezzo == 1 else math.floor(match.prezzo * 0.5)
            self.fm += restituiti_fm
            match.squadra = None
            self.__aggiorna_score(calciatore, False)
            lega.aggiorna_calciatore(match, 'Svincolato')  # Update the DataFrame
            return restituiti_fm
        else:
            return None
        
class ScoreStrategy:
    def calculate_score(self, fascia, rigori):
        """Calculate score based on fascia and rigori"""
        raise NotImplementedError("This method should be overridden by subclasses")


class PortiereScoreStrategy(ScoreStrategy):
    def calculate_score(self, fascia, rigori):
        if fascia == 1:
            score = 2
        elif fascia == 2:
            score = 1
        else:
            score = 0

        return score


class DifensoreScoreStrategy(ScoreStrategy):
    def calculate_score(self, fascia, rigori):

        if fascia == 1:
            score = 4
        elif fascia == 2:
            score = 2
        elif fascia == 3:
            score = 1
        else:
            score = 0

        if rigori == "SI":
            score += 3

        return score


class CentrocampistaScoreStrategy(ScoreStrategy):
    def calculate_score(self, fascia, rigori):

        if fascia == 1:
            score = 7
        elif fascia == 2:
            score = 4
        elif fascia == 3:
            score = 2
        elif fascia == 4:
            score = 1
        else:
            score = 0
        
        if rigori == "SI":
            score += 5

        return score


class AttaccanteScoreStrategy(ScoreStrategy):
    def calculate_score(self, fascia, rigori):

        if fascia == 1:
            score = 10
        elif fascia == 2:
            score = 6
        elif fascia == 3:
            score = 4
        elif fascia == 4:
            score = 1
        else:
            score = 0
        
        if rigori == "SI":
            score += 4
        return score



class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if not args:
            return super().__call__(*args, **kwargs)
        
        # Assume the first argument is the player's name
        key = (args[0],)  # Assuming `args[0]` is the player's name

        if key not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[key] = instance
        return cls._instances[key]

class FantaCalciatore(metaclass=SingletonMeta):
    def __init__(self, Nome, lega, ruolo=None, fascia=None, quotazione=1, prezzo=None):
        # Check if the name exists in the DataFrame
        if Nome in lega.df['Nome'].values:
            # Get the row corresponding to the player's name
            dati_calciatore = lega.df[lega.df['Nome'] == Nome].iloc[0]

            # Initialize attributes from the DataFrame
            self.Nome = dati_calciatore['Nome']
            self.ruolo = dati_calciatore['Ruolo']
            self.fascia = dati_calciatore.get('Fascia', None)
            self.squadra = dati_calciatore['Stato']  # traccia la squadra o se è svincolato
            self.prezzo = dati_calciatore['Prezzo']  # prezzo se acquistato
            self.rigori = dati_calciatore.get('Rigorista', None)
            if default_fm == 500:
                self.quotazione = dati_calciatore['FM/500']
            elif default_fm == 1000:
                self.quotazione = dati_calciatore['FM/1000']
        else:
            # Raise an error if the name is not found
            raise ValueError(f"{Nome} not found in the DataFrame.")

    def __str__(self):

        if self.fascia is not None and not (isinstance(self.fascia, float) and math.isnan(self.fascia)):
            fascia_value = int(self.fascia)  # Convert to int if valid
        else:
            fascia_value = "Non specificata"  # Default value if it's None or NaN
    
        return (f'{self.Nome} ({self.ruolo}): quotazione {self.quotazione} fm\n'
                f'Fascia: {fascia_value}\n'
                f'Rigorista: {self.rigori}\n'
                f'Prezzo: {self.prezzo if self.prezzo is not None else "---"}\n'
                f'Squadra: {self.squadra}\n'
                )


class Lega:
    def __init__(self, nome, allenatori):
        self.nome = nome
        self.allenatori = allenatori
        self.df = load_data()

    def inizia_fantacalcio(self):
        for i, nome_allenatore in enumerate(self.allenatori):
            self.allenatori[i] = FantaAllenatore(nome_allenatore)

    def get_allenatore(self, nome_allenatore):
        for allenatore in self.allenatori:
            if allenatore.nome == nome_allenatore:
                return str(allenatore)
        return None
    
    def dettagli(self):
        info = f"Nome della lega: {self.nome}\n"
        info += "Partecipanti:\n"
        for i, allenatore in enumerate(self.allenatori, start=1):
            info += f"   {allenatore.nome} - Score: {allenatore.score}\n"  # i is the index, allenatore is the object
        return info

    def save(self):
        filename = f"{self.nome}.pkl"
        with open(filename, 'wb') as file:
            pickle.dump(self, file, protocol=pickle.HIGHEST_PROTOCOL)
        #print(f"Lega salvata in {filename}")

    @staticmethod
    def load(nome_lega):
        try:
            with open(nome_lega, 'rb') as file:
                lega = pickle.load(file)
            #print(f"Lega '{nome_lega}' caricata")
            return lega
        except FileNotFoundError:
            print(f"{nome_lega} non trovata come file lega.")
            return None
        except Exception as e:
            print(f"Errore nel caricamento del file: {e}")
            return None
        
    def aggiorna_calciatore(self, calciatore, nuovo_stato, prezzo=None):
        # Find the index of the player in the DataFrame
        index = self.df.index[self.df['Nome'] == calciatore.Nome].tolist()
    
        if index:
            # Update the player's status in the DataFrame
            self.df.at[index[0], 'Stato'] = nuovo_stato
            if nuovo_stato != 'Svincolato':
                self.df.at[index[0], 'Prezzo'] = prezzo
            else:
                self.df.at[index[0], 'Prezzo'] = None # caso in cui rimuovo o svincolo
            return 1  # Update successful
        else:
            print(f"Errore: Calciatore {calciatore.Nome} non trovato nel DataFrame.")
            return 2  # Player not found

# TODO creare il sistema di score dei FantaAllenatori, fare un sort by score, implica aggiungere fasce al df



#-------------------------------TEST-------------------------------#

#Fantacalcetto = gioca()

#Thuram = FantaCalciatore("Thuram", df)
#Chiesa = FantaCalciatore("Chiesa", df)
#Dimarco = FantaCalciatore("Dimarco", df)

#print(Dimarco)
#print(Chiesa)
#print(Thuram)

#me.compra(Thuram, Thuram.quotazione)
#me.compra(Chiesa, 45)
#me.compra(Dimarco, Dimarco.quotazione)

#print(me)

#print(Chiesa)

#me.rimuovi(Thuram)
#me.svincola(Chiesa)