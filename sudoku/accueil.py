import pygame
import menu
import sys
from bouton import Bouton

class EcranAccueil:
    def __init__(self):
        pygame.init()
        self.ecran = pygame.display.set_mode((750, 750))
        pygame.display.set_caption("Sudoku - Accueil")
        
        # Définition des couleurs
        self.DARKER_BLUE = (0, 0, 139)
        self.BLANC = (255, 255, 255)
        self.MARRON = (139, 69, 19)

        # Définition de la fenêtre
        self.largeur, self.hauteur = 750, 750
        
        # Utilisation d'une police système
        self.police = pygame.font.SysFont("Comic Sans MS", 80)

        # Variables pour l'effet de transition de couleur
        self.intensite = 0
        self.incrementation = 1

        # Initialiser les surfaces de texte et l'icône
        self.texte_su = None
        self.texte_ku = None
        self.play_icon = None
        self.rect_su = None
        self.rect_ku = None
        self.rect_play = None
        
        # État de l'application
        self.running = True
        
        self._initialiser_elements()
    
    def _initialiser_elements(self):
        """Initialise les éléments graphiques de l'écran d'accueil"""
        # Charger l'icône Play
        try:
            self.play_icon = pygame.image.load("play_icon.png")
            self.play_icon = pygame.transform.scale(self.play_icon, (90, 90))
        except:
            self.play_icon = pygame.Surface((90, 90))
            self.play_icon.fill((100, 100, 100))

        # Position du texte et icône
        self.texte_su = self.police.render("SUD", True, self.DARKER_BLUE)
        self.texte_ku = self.police.render("KU", True, self.DARKER_BLUE)
        self.rect_su = self.texte_su.get_rect(midright=(self.largeur//2 - 30, self.hauteur//2))
        self.rect_ku = self.texte_ku.get_rect(midleft=(self.largeur//2 + 30, self.hauteur//2))
        self.rect_play = self.play_icon.get_rect(center=(self.largeur//2, self.hauteur//2))
    
    def _mettre_a_jour_couleur(self):
        """Met à jour la couleur pour l'effet de transition"""
        # Mise à jour de la couleur pour l'effet de transition
        couleur_actuelle = (abs(self.intensite), abs(self.intensite), 255)  # Transition du bleu
        self.texte_su = self.police.render("SUD", True, couleur_actuelle)
        self.texte_ku = self.police.render("KU", True, couleur_actuelle)

        # Ajustement progressif de la couleur
        self.intensite += self.incrementation
        if self.intensite > 139 or self.intensite < 0:
            self.incrementation *= -1  # Inverse le changement de couleur
    
    def _dessiner_elements(self):
        """Dessine tous les éléments sur l'écran"""
        self.ecran.fill(self.BLANC)
        
        # Dessin des éléments
        self.ecran.blit(self.texte_su, self.rect_su)
        self.ecran.blit(self.texte_ku, self.rect_ku)
        self.ecran.blit(self.play_icon, self.rect_play)
    
    def _gerer_evenements(self):
        """Gère les événements pygame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect_play.collidepoint(event.pos):
                    self.running = False
        return True
    
    def lancer(self):
        """Lance la boucle principale de l'écran d'accueil"""
        # Boucle d'affichage
        while self.running:
            # Mettre à jour la couleur
            self._mettre_a_jour_couleur()
            
            # Dessiner les éléments
            self._dessiner_elements()
            
            # Gérer les événements
            if not self._gerer_evenements():
                return False
            
            pygame.display.flip()
            pygame.time.delay(30)

        return True


def lancer_accueil():
    """Fonction de compatibilité avec l'ancien code"""
    ecran_accueil = EcranAccueil()
    return ecran_accueil.lancer()