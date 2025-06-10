class GestionnaireErreurs:
    def __init__(self):
        self.erreurs = 0
    
    def ajouter_erreur(self, type_erreur, position, valeur):
        self.erreurs += 1
    
    def reinitialiser(self):
        self.erreurs = 0
    
    def nombre_erreurs(self):
        return self.erreurs