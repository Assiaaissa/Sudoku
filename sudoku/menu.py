import pygame
import sys
from main import main as jeu_principal
from classique.modes import facile, moyen, difficile
from classique.sauvegarde import Sauvegarde
from multijoueur.mode import lancer_mode_multijoueur
from classique.grille import Grille


from AI.remplir_grille import RemplirGrille
from AI.ia_solve import SudokuSolverAI

class MenuSudoku:
    """Classe principale pour gérer le menu du jeu Sudoku"""
    
    # Constantes de classe
    WIDTH, HEIGHT = 750, 750
    
    # Couleurs
    MAUVE = (186, 85, 211)
    LIGHT_BLUE = (173, 216, 230)
    DARK_BLUE = (0, 0, 139)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    HOVER_COLOR = (135, 206, 250)
    
    def __init__(self):
        """Initialise le menu Sudoku"""
        self.init_pygame()
        
        # État du menu
        self.clock = pygame.time.Clock()
        self.running = True
        self.show_difficulties = False
        self.animation_done = False
        self.action_requested = None
        
        # Gestionnaire de sauvegarde
        self.sauvegarde_manager = Sauvegarde()
        
        # Initialisation des boutons
        self._init_buttons()
    
    def init_pygame(self):
        """Initialise ou réinitialise pygame"""
        if not pygame.get_init():
            pygame.init()
        
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Menu Sudoku")
        
        # Polices
        self.font = pygame.font.SysFont("comicsans", 32)
        self.title_font = pygame.font.SysFont("comicsans", 50)
        self.petite_font = pygame.font.SysFont("comicsans", 20)
    
    def _init_buttons(self):
        """Initialise les boutons du menu"""
        # Boutons principaux
        self.buttons = [
            {"text": "Nouveau Jeu", "rect": pygame.Rect(400, 200, 250, 50)},  
            {"text": "Jouer avec IA", "rect": pygame.Rect(400, 270, 250, 50)},
            {"text": "Reprendre", "rect": pygame.Rect(400, 340, 200, 50)},
            {"text": "Jeu Multijoueur", "rect": pygame.Rect(400, 410, 250, 50)},
        ]
        
        # Boutons de difficulté
        self.difficulty_buttons = [
            {"text": "Facile", "rect": pygame.Rect(400, 200, 100, 40)},  
            {"text": "Moyen", "rect": pygame.Rect(400, 250, 100, 40)},
            {"text": "Difficile", "rect": pygame.Rect(400, 300, 130, 40)},
        ]
        
        # Bouton retour accueil
        self.bouton_retour_accueil = pygame.Rect(20, 10, 150, 30)
    
    def draw_gradient(self):
        """Dessine le dégradé de fond"""
        for y in range(self.HEIGHT):
            r = self.MAUVE[0] + (self.LIGHT_BLUE[0] - self.MAUVE[0]) * y // self.HEIGHT
            g = self.MAUVE[1] + (self.LIGHT_BLUE[1] - self.MAUVE[1]) * y // self.HEIGHT
            b = self.MAUVE[2] + (self.LIGHT_BLUE[2] - self.MAUVE[2]) * y // self.HEIGHT
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.WIDTH, y))
    
    def draw_buttons(self):
        """Dessine les boutons principaux"""
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            color = self.HOVER_COLOR if btn["rect"].collidepoint(mouse_pos) else self.LIGHT_BLUE
            pygame.draw.rect(self.screen, color, btn["rect"], border_radius=10)
            pygame.draw.rect(self.screen, self.DARK_BLUE, btn["rect"], 2, border_radius=10)
            text_surface = self.font.render(btn["text"], True, self.BLACK)
            text_rect = text_surface.get_rect(center=btn["rect"].center)
            self.screen.blit(text_surface, text_rect)
    
    def draw_difficulty_buttons(self):
        """Dessine les boutons de difficulté"""
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.difficulty_buttons:
            color = self.HOVER_COLOR if btn["rect"].collidepoint(mouse_pos) else self.LIGHT_BLUE
            pygame.draw.rect(self.screen, color, btn["rect"], border_radius=10)
            pygame.draw.rect(self.screen, self.DARK_BLUE, btn["rect"], 2, border_radius=10)
            text_surface = self.font.render(btn["text"], True, self.BLACK)
            text_rect = text_surface.get_rect(center=btn["rect"].center)
            self.screen.blit(text_surface, text_rect)
    
    def draw_title(self):
        """Dessine le titre"""
        title_text = self.title_font.render("SUDOKU", True, self.BLACK)
        self.screen.blit(title_text, (self.WIDTH // 2 - title_text.get_width() // 2 + 30, 50))
    
    def draw_return_button(self):
        """Dessine le bouton de retour à l'accueil"""
        pygame.draw.rect(self.screen, self.LIGHT_BLUE, self.bouton_retour_accueil, border_radius=10)
        pygame.draw.rect(self.screen, self.DARK_BLUE, self.bouton_retour_accueil, 2, border_radius=10)
        texte = self.petite_font.render("Retour Accueil", True, self.BLACK)
        texte_rect = texte.get_rect(center=self.bouton_retour_accueil.center)
        self.screen.blit(texte, texte_rect)
    
    def handle_animation(self):
        """Gère l'animation du bouton 'Nouveau Jeu'"""
        if self.show_difficulties and not self.animation_done:
            if self.buttons[0]["rect"].x > 50:
                self.buttons[0]["rect"].x -= 5
            else:
                self.animation_done = True
    
    def handle_return_button_click(self):
        """Gère le clic sur le bouton retour accueil"""
        self.action_requested = "retour_accueil"
        self.running = False
    
    def handle_nouveau_jeu_click(self):
        """Gère le clic sur 'Nouveau Jeu'"""
        if not self.show_difficulties:
            self.show_difficulties = True
            self.buttons = [self.buttons[0]]
    
    def handle_jouer_ia_click(self):
        """Gère le clic sur 'Jouer avec IA'"""
        self.action_requested = "jouer_ia"
        self.running = False
    
    def handle_reprendre_click(self):
        """Gère le clic sur 'Reprendre'"""
        initial, modifiee, solution = self.sauvegarde_manager.charger()
        if initial and modifiee:
            self.action_requested = ("reprendre", initial, modifiee, solution)
            self.running = False
        else:
            print("Impossible de reprendre la partie : aucune sauvegarde valide trouvée.")
    
    def handle_multijoueur_click(self):
        """Gère le clic sur 'Jeu Multijoueur'"""
        self.action_requested = "multijoueur"
        self.running = False
    
    def handle_difficulty_click(self, btn_text):
        """Gère le clic sur un bouton de difficulté"""
        grille_complete = None
        grille_trous = None
        difficulte = "moyen"
        
        if btn_text == "Facile":
            grille_complete, grille_trous = facile()
            difficulte = "facile"
        elif btn_text == "Moyen":
            grille_complete, grille_trous = moyen()
            difficulte = "moyen"
        elif btn_text == "Difficile":
            grille_complete, grille_trous = difficile()
            difficulte = "difficile"
        
        if grille_complete is not None and grille_trous is not None:
            self.action_requested = ("nouveau_jeu", grille_complete, grille_trous, difficulte)
            self.running = False
    
    def handle_mouse_click(self, pos):
        """Gère tous les clics de souris"""
        # Bouton retour accueil
        if self.bouton_retour_accueil.collidepoint(pos):
            self.handle_return_button_click()
            return
        
        # Boutons principaux (si pas en mode difficulté)
        if not self.show_difficulties:
            if self.buttons[0]["rect"].collidepoint(pos):
                self.handle_nouveau_jeu_click()
            elif len(self.buttons) > 1 and self.buttons[1]["rect"].collidepoint(pos):
                self.handle_jouer_ia_click()
            elif len(self.buttons) > 2 and self.buttons[2]["rect"].collidepoint(pos):
                self.handle_reprendre_click()
            elif len(self.buttons) > 3 and self.buttons[3]["rect"].collidepoint(pos):
                self.handle_multijoueur_click()
        
        # Boutons de difficulté (si affichés et animation terminée)
        elif self.show_difficulties and self.animation_done:
            for btn in self.difficulty_buttons:
                if btn["rect"].collidepoint(pos):
                    self.handle_difficulty_click(btn["text"])
                    break
    
    def handle_events(self):
        """Gère tous les événements pygame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_click(event.pos)
    
    def render(self):
        """Effectue le rendu complet du menu"""
        self.screen.fill(self.WHITE)
        self.draw_gradient()
        self.draw_title()
        
        if not self.show_difficulties:
            self.draw_buttons()
        else:
            self.handle_animation()
            self.draw_buttons()
            if self.animation_done:
                self.draw_difficulty_buttons()
        
        self.draw_return_button()
        pygame.display.flip()
    
    def reset_menu_state(self):
        """Remet le menu dans son état initial"""
        self.show_difficulties = False
        self.animation_done = False
        self.action_requested = None
        self._init_buttons()
    
    def execute_action(self):
        """Exécute l'action demandée et retourne le résultat"""
        if self.action_requested == "retour_accueil":
            # Fermer pygame temporairement pour l'accueil
            pygame.quit()
            
            try:
                import accueil
                retour = accueil.lancer_accueil()
                
                if retour:
                    # Relancer le menu
                    self.init_pygame()
                    return True
                else:
                    return False
            except Exception as e:
                print(f"Erreur lors du lancement de l'accueil: {e}")
                # Réinitialiser pygame en cas d'erreur
                self.init_pygame()
                return True
                
        elif self.action_requested == "jouer_ia":
            try:
                
                remplir_grille_app = RemplirGrille()
                retour_remplir_grille = remplir_grille_app.run()
                
                
                self.init_pygame() # Réinitialiser Pygame
                return retour_remplir_grille # Indique si le menu doit continuer
            except Exception as e:
                print(f"Erreur lors du lancement de l'interface de remplissage de grille: {e}")
                self.init_pygame() # Réinitialiser Pygame
                return True # Continuer le menu en cas d'erreur
                
        elif self.action_requested == "multijoueur":
            try:
                lancer_mode_multijoueur()
                self.init_pygame() # Réinitialiser Pygame après le mode multijoueur
                return True
            except Exception as e:
                print(f"Erreur lors du lancement du multijoueur: {e}")
                self.init_pygame() # Réinitialiser Pygame
                return True
                
        elif isinstance(self.action_requested, tuple):
            if self.action_requested[0] == "reprendre":
                _, initial, modifiee, solution = self.action_requested
                retour_menu = jeu_principal(initial, modifiee, "reprendre", solution)
                self.init_pygame() # Réinitialiser Pygame après le jeu principal
                return retour_menu
                
            elif self.action_requested[0] == "nouveau_jeu":
                _, grille_complete, grille_trous, difficulte = self.action_requested
                retour_menu = jeu_principal(grille_complete, grille_trous, difficulte)
                self.init_pygame() # Réinitialiser Pygame après le jeu principal
                return retour_menu
        
        return True
    
    def run(self):
        """Lance la boucle principale du menu"""
        while True:
            self.reset_menu_state()
            self.running = True
            
            # Boucle d'affichage du menu
            while self.running:
                self.render()
                self.handle_events()
                self.clock.tick(60)
            
            # Exécuter l'action demandée
            if self.action_requested:
                continue_menu = self.execute_action()
                if not continue_menu:
                    break
            else:
                break
        
        pygame.quit()
        sys.exit()


def main():
    """Fonction principale pour lancer le menu"""
    menu = MenuSudoku()
    return menu.run()


if __name__ == "__main__":
    main()