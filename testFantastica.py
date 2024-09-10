import unittest
from unittest.mock import patch
import fantastica

class testParserFantastica(unittest.TestCase):

    input_init = [
            "LegaTest",  # League name
            "3",  # Number of managers
            "Palladino",  # First manager
            "Italiano",  # Second manager
            "Montella",
            "Quotazioni_Fantacalcio_Stagione_2024_25",  # Excel file name
        ]
     
    @patch('builtins.input', side_effect=input_init) # gli input saranno in ordine quelli della stringa
    @patch('builtins.print')  # Mock print to avoid actual output during tests
    def test_0_state_functions(self, mock_print, mock_input):
        fantastica.process_command("init")
        # quando chiede gli input, vengono passati gli elementi nella lista input_init
        self.assertIsNotNone(fantastica.lega)
        self.assertEqual(fantastica.lega.nome, "LegaTest")
        self.assertEqual(len(fantastica.lega.allenatori), 3)
        fantastica.process_command("save")
        fantastica.process_command("quit")
        fantastica.process_command("load LegaTest")
        self.assertIsNotNone(fantastica.lega)
        self.assertEqual(fantastica.lega.nome, "LegaTest")
        self.assertEqual(len(fantastica.lega.allenatori), 3)

# A SEGUIRE UNA SERIE DI TEST IN CUI VA TUTTO BENE

    def test_1_mercato(self):
        
        commands = [
        "Palladino compra Kean 100",
        "Montella compra Gonzalez N. 60",
        "Italiano compra Dallinga 20",
        "Palladino compra De Gea 1",
        "Italiano compra Terracciano 10",
        "Montella compra Pinamonti 3",
        "Montella compra Biraghi 120",
        "Palladino compra Gosens 230",
        "Italiano compra Posch 21",
        "Montella svincola Gonzalez N.",
        "Italiano rimuove Dallinga",
        "Palladino svincola De Gea",
        "Palladino compra Dallinga 1",
        "Italiano compra Sommer 1"
        ]

        fantastica.process_command("load LegaTest")

        while commands:
            fantastica.process_command(commands.pop(0))

    def test_2_info_rose(self):
        fantastica.process_command("load LegaTest")
        
        commands = [
            "info Palladino",
            "info Montella",
            "info Italiano"
        ]

        while commands:
            fantastica.process_command(commands.pop(0))
    

    def test_3_info_giocatori(self):

        commands = [
        "info Kean",
        "info De Gea",
        "info Terracciano",
        "info Gosens",
        "info Posch",
        "info Sommer",
        "info Thuram",
        "info Simeone",
        "info Vlahovic",
        "info Biraghi"
        ]

        while commands:
            fantastica.process_command(commands.pop(0))
    
    def test_4_info_svincolati(self):

        commands = [
        "info svincolati",
        "info svincolati porta",
        "info svincolati difesa",
        "info svincolati centrocampo",
        "info svincolati attacco",
        "info svincolati P",
        "info svincolati D",
        "info svincolati C",
        "info svincolati A",
        "info svincolati F"
        ]

        while commands:
            fantastica.process_command(commands.pop(0))

# TODO: A SEGUIRE UNA SERIE DI TEST IN CUI VA TUTTO MALE

if __name__ == "__main__":
    unittest.main()