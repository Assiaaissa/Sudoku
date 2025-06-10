import pygame
class Bouton:
    def __init__(self, x, y, largeur, hauteur, texte, couleur_normale=(200, 200, 200), couleur_survol=(160, 160, 160)):
        self.rect = pygame.Rect(x, y, largeur, hauteur)
        self.texte = texte
        self.couleur_normale = couleur_normale
        self.couleur_survol = couleur_survol
        self.couleur_actuelle = couleur_normale
        self.police = pygame.font.SysFont('Arial', 22)
    
    def dessiner(self, surface):
        pygame.draw.rect(surface, self.couleur_actuelle, self.rect, 0, 10)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2, 10)
        texte_surface = self.police.render(self.texte, True, (0, 0, 0))
        texte_rect = texte_surface.get_rect(center=self.rect.center)
        surface.blit(texte_surface, texte_rect)
    
    def verifier_survol(self, pos_souris):
        if self.rect.collidepoint(pos_souris):
            self.couleur_actuelle = self.couleur_survol
            return True
        else:
            self.couleur_actuelle = self.couleur_normale
            return False
    
    def verifier_clic(self, pos_souris, evenement):
        return self.rect.collidepoint(pos_souris) and evenement.type == pygame.MOUSEBUTTONDOWN