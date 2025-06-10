import json

class Sauvegarde:
    def __init__(self, chemin_fichier="grille_utilisateur.json"):
        self.chemin_fichier = chemin_fichier

    def charger(self):
        try:
            with open(self.chemin_fichier, "r") as f:
                data = json.load(f)
            initial = data.get("initial")
            modifiee = data.get("modifiee")
            solution = data.get("solution", initial)

            if self._valide_grille(initial) and self._valide_grille(modifiee):
                return initial, modifiee, solution
            else:
                print("Grille invalide dans le fichier.")
                return None, None, None
        except Exception as e:
            print(f"Erreur lors du chargement: {e}")
            return None, None, None

    def sauvegarder(self, initial, modifiee, solution):
        try:
            data = {
                "initial": initial,
                "modifiee": modifiee,
                "solution": solution
            }
            with open(self.chemin_fichier, "w") as f:
                json.dump(data, f)
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            return False

    def _valide_grille(self, grille):
        return grille is not None and len(grille) == 9 and all(len(ligne) == 9 for ligne in grille)
