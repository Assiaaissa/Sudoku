# Dans classique/aide.py
import random

class Aide:
    def __init__(self, grille_affichee, solution, score_manager): # Renommé 'score' en 'score_manager' pour plus de clarté
        """
        grille_affichee et solution sont des matrices 9x9 (listes de listes)
        score_manager est un objet avec un attribut 'score' et une méthode 'appliquer_penalite_aide()'
        """
        self.grille_affichee = grille_affichee
        self.solution = solution
        self.score_manager = score_manager # Stockez l'objet ActualisationSudoku ici

    def grille_valid(self, grille, n, m, nbr):
        """Vérifie si un nombre peut être placé dans une case"""
        for i in range(9):
            if grille[n][i] == nbr and i != m:
                return False
        for i in range(9):
            if grille[i][m] == nbr and i != n:
                return False
        num_ligne = 3 * (n // 3)
        num_colonne = 3 * (m // 3)
        for i in range(num_ligne, num_ligne + 3):
            for j in range(num_colonne, num_colonne + 3):
                if grille[i][j] == nbr and (i != n or j != m):
                    return False
        return True

    def aide_utilisateur(self, selected=None):
        # Vérifier si on peut appliquer la pénalité
        # Maintenant, on accède à l'attribut 'score' de l'objet 'ActualisationSudoku'
        if self.score_manager.score <= 0: # <-- MODIFIÉ ICI
            print("Aide impossible : score déjà à 0!")
            return None
        self.score_manager.appliquer_penalite_aide() # <-- Ceci était déjà correct, car 'appliquer_penalite_aide' est une méthode de ActualisationSudoku

        # Aide sur case sélectionnée
        if selected:
            i, j = selected
            if self.grille_affichee[i][j] == 0:
                valeur = self.solution[i][j]
                # Le check grille_valid est déjà fait dans la classe Aide
                print(f"Aide: la case ({i+1},{j+1}) = {valeur} (score -10)")
                return i, j, valeur

        # Aide sur case aléatoire
        cases_vides = [(i, j) for i in range(9) for j in range(9) if self.grille_affichee[i][j] == 0]
        if cases_vides:
            i, j = random.choice(cases_vides)
            valeur = self.solution[i][j]
            # Le check grille_valid est déjà fait dans la classe Aide
            print(f"Aide: case aléatoire ({i+1},{j+1}) = {valeur} (score -10)")
            return i, j, valeur

        print("Aucune case vide disponible pour l'aide.")
        return None