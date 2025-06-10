from datetime import datetime

class ActualisationSudoku:
    def __init__(self, difficulte="moyen"):
        self.historique = []
        self.difficulte = difficulte
        self.scores_initiaux = {
            "facile": 100,
            "moyen": 70,
            "difficile": 30
        }
        self.score = self.scores_initiaux.get(difficulte, 70)
        self.aides_utilisees = 0
        self.temps_debut = None
        self.temps_fin = None
    def reinitialiser(self):
        """Réinitialise le score et le timer"""
        self.score = self.scores_initiaux.get(self.difficulte, 70)
        self.aides_utilisees = 0
        self.temps_debut = None
    def actualiser_cellule(self, ligne, colonne, ancienne_valeur, nouvelle_valeur):
        self.historique.append({
            "ligne": ligne,
            "colonne": colonne,
            "avant": ancienne_valeur,
            "apres": nouvelle_valeur
        })
        return self.historique[-1]

    def appliquer_penalite_aide(self):
    #Applique la pénalité seulement si le score est positif"""
      if self.score > 0:
        self.score = max(0, self.score - 10)  # Garantit que le score ne devient pas négatif
        self.aides_utilisees += 1
        return True
      return False 

    def demarrer_timer(self):
        self.temps_debut = datetime.now()

    def arreter_timer(self):
        self.temps_fin = datetime.now()

    def calculer_score_final(self):
        if self.temps_fin and self.temps_debut:
            temps_ecoule = (self.temps_fin - self.temps_debut).total_seconds()
            self.score = max(0, self.score - int(temps_ecoule / 5))
        return self.score

    def actualiser_progression(self, grille):
        total = 81
        remplis = sum(cell != 0 for row in grille for cell in row)
        return round((remplis / total) * 100, 1)

    def generer_rapport(self, grille, nb_erreurs):
        progression = self.actualiser_progression(grille)
        temps_jeu = (datetime.now() - self.temps_debut).total_seconds() if self.temps_debut else 0
        return {
            "temps": temps_jeu,
            "erreurs": nb_erreurs,
            "progression": progression,
            "score": self.score,
            "aides": self.aides_utilisees,
            "difficulte": self.difficulte
        }

    def effacer_historique(self):
        self.historique = []
