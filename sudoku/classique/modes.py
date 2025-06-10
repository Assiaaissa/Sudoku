# Dans classique/modes.py
from classique.grille import Grille

def facile():
    """Renvoie une grille facile avec environ 35 cases vides."""
    complete = Grille.grille_aleatoire_complete()
    grille = complete.creuser(35)
    return complete.matrice, grille.matrice 

def moyen():
    """Renvoie une grille moyenne avec environ 45 cases vides."""
    complete = Grille.grille_aleatoire_complete()
    grille = complete.creuser(45)
    return complete.matrice, grille.matrice 
def difficile():
    """Renvoie une grille difficile avec environ 55 cases vides."""
    complete = Grille.grille_aleatoire_complete()
    grille = complete.creuser(55)
    return complete.matrice, grille.matrice 