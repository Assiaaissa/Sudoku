import pygame
from pygame.locals import *
from classique.grille import Grille
from classique.chrono import Chronometre
from bouton import Bouton
from classique.actualisation import ActualisationSudoku
import json

# Importez la classe Aide depuis votre fichier aide.py
# En supposant que 'aide.py' est dans le répertoire 'classique' d'après votre 'from classique.grille import Grille'
from classique.aide import Aide # <--- AJOUTEZ CETTE LIGNE

def grille_valid(grille, r, c, val):
    # Cette fonction est redondante car Aide.grille_valid et Grille.est_valide_case existent.
    # Il est préférable d'utiliser celle de Grille ou Aide de manière cohérente.
    # Pour l'instant, nous la gardons telle quelle, mais envisagez de la supprimer si elle n'est pas strictement nécessaire.
    return Grille.est_valide_case(grille, r, c, val)

ACTUAL_WINDOW_WIDTH = 750
ACTUAL_WINDOW_HEIGHT = 750

CELL_SIZE = 60
GRID_N_CELLS = 9
GRID_WIDTH_PX = GRID_N_CELLS * CELL_SIZE

GRID_LEFT_MARGIN = (ACTUAL_WINDOW_WIDTH - GRID_WIDTH_PX) // 2

GRID_TOP = 50
GRID_BOTTOM = GRID_N_CELLS * CELL_SIZE + GRID_TOP
BUTTON_TOP = GRID_BOTTOM + 20

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 200, 0)
LIGHT_GRAY = (240, 240, 240)
ORANGE = (255, 165, 0)
DARK_RED = (139, 0, 0)
DARK_GREEN = (0, 100, 0)
DARK_BLUE = (0, 0, 100)
DARK_GRAY_TEXT = (50, 50, 50)

class GestionnaireErreurs:
    def __init__(self):
        self.erreurs = 0

    def ajouter_erreur(self):
        self.erreurs += 1

    def reinitialiser(self):
        self.erreurs = 0

    def nombre_erreurs(self):
        return self.erreurs

class SudokuGrid:
    def __init__(self, screen, grille_complete=None, grille_trous=None, difficulte="moyen"):
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 40)
        self.button_font = pygame.font.SysFont('Arial', 22)
        self.stats_font = pygame.font.SysFont('Arial', 16)
        self.victory_font = pygame.font.SysFont('Arial', 36)
        self.small_font = pygame.font.SysFont('Arial', 18)

        self.screen = screen
        self.grille_complete = grille_complete
        self.grille_trous = grille_trous
        self.difficulte = difficulte
        self.est_en_pause = False
        self.retour_menu = False
        self.partie_gagnee = False
        self.solved_automatically = False
        self.message_erreur = ""
        self.message_timer = 0
        self.couleur_message = BLACK

        self.bouton_retour = Bouton(10, 10, 120, 30, "Retour", GRAY, (160, 160, 160))
        self.bouton_pause = Bouton(ACTUAL_WINDOW_WIDTH - 130, 10, 120, 30, "Pause", GRAY, (160, 160, 160))

        button_group_width = 150 + 10 + 150 + 10 + 150
        button_start_x = (ACTUAL_WINDOW_WIDTH - button_group_width) // 2

        self.bouton_verifier = Bouton(button_start_x, BUTTON_TOP, 150, 40, "Vérifier", GREEN, (0, 150, 0))
        self.bouton_aide = Bouton(button_start_x + 160, BUTTON_TOP, 150, 40, "Aide (-10pts)", ORANGE, (200, 120, 0))
        self.bouton_resoudre = Bouton(button_start_x + 320, BUTTON_TOP, 150, 40, "Résoudre", RED, DARK_RED)

        self.bouton_nouveau = Bouton(ACTUAL_WINDOW_WIDTH//2 - 100, BUTTON_TOP + 50, 200, 40, "Réinitialiser", BLUE, (0, 0, 139))
        self.bouton_sauvegarder = Bouton(ACTUAL_WINDOW_WIDTH//2 - 100, BUTTON_TOP + 100, 200, 40, "Sauvegarder", ORANGE, (200, 120, 0))

        self.error_manager = GestionnaireErreurs()
        self.reset_game()

        # Initialisez l'instance de la classe Aide ici
        # Elle a besoin de self.grid (grille_affichee), self.solution, et self.actualisation (score_object)
        self.aide_instance = Aide(self.grid, self.solution, self.actualisation) # <--- AJOUTEZ/MODIFIEZ CETTE LIGNE

    def reset_game(self):
        # Réinitialisation des grilles
        if self.grille_complete is not None and self.grille_trous is not None:
            # Copie profonde de la solution complète
            self.solution = [row[:] for row in self.grille_complete]
            
            # Pour le mode "reprendre", on utilise la grille modifiée sauvegardée
            # Pour une nouvelle partie, on utilise la grille avec trous
            self.grid = [row[:] for row in self.grille_trous]
            
            # Déterminer quelles cases sont fixes (non modifiables)
            if self.difficulte == "reprendre":
                # En mode reprise, les cases initiales sont celles de la solution complète
                self.original = [[self.grille_complete[i][j] != 0 for j in range(9)] for i in range(9)]
            else:
                # Pour une nouvelle partie, les cases initiales sont celles fournies dans la grille avec trous
                self.original = [[self.grid[i][j] != 0 for j in range(9)] for i in range(9)]
        
        # Mise à jour du texte du bouton en fonction du mode
        self.bouton_nouveau.texte = "Réinitialiser" if self.difficulte == "reprendre" else "Nouvelle partie"
        
        # Réinitialisation de l'état du jeu
        self.selected = None
        self.error_cells = set()
        self.partie_gagnee = False
        self.solved_automatically = False
        self.message_erreur = ""
        self.message_timer = 0
        
        # Réinitialisation des systèmes de suivi
        self.error_manager.reinitialiser()
        
        # Recréation des instances pour éviter les problèmes de référence
        self.chrono = Chronometre()
        self.actualisation = ActualisationSudoku(self.difficulte)
        
        # Démarrage des timers
        self.chrono.demarrer()
        self.actualisation.demarrer_timer()
        
        # Si c'est une nouvelle partie (pas reprise), générer une nouvelle grille si nécessaire
        if self.difficulte != "reprendre" and (self.grille_complete is None or self.grille_trous is None):
            import generation
            grille_complete_gen = generation.grille_vide()
            self.solution = [row[:] for row in grille_complete_gen]
            
            # Déterminer le nombre de cases vides selon la difficulté
            nb_cases_vides = {
                "facile": 30,
                "moyen": 40,
                "difficile": 50
            }.get(self.difficulte, 40)
            
            self.grid = generation.grille_final(grille_complete_gen, nb_cases_vides)
            self.original = [[self.grid[i][j] != 0 for j in range(9)] for i in range(9)]
        
        # Assurez-vous que l'instance aide_instance est mise à jour avec la nouvelle grille et solution après le reset
        # C'est crucial si reset_game peut générer de nouvelles grilles.
        if hasattr(self, 'aide_instance'): # Vérifiez si elle est déjà initialisée
            self.aide_instance.grille_affichee = self.grid
            self.aide_instance.solution = self.solution
            self.aide_instance.score_object = self.actualisation # Assurez-vous que score_object est à jour
        else: # Initialisez si c'est le tout premier appel à reset_game depuis __init__
            self.aide_instance = Aide(self.grid, self.solution, self.actualisation)


    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            return self.handle_click(event.pos)
        elif event.type == pygame.KEYDOWN:
            self.handle_key(event.key)
        return False

    def handle_click(self, pos):
        x, y = pos

        # Toujours permettre le clic sur les boutons Retour et Pause
        if self.bouton_retour.verifier_clic(pos, pygame.event.Event(pygame.MOUSEBUTTONDOWN)):
            self.retour_menu = True
            return True
            
        if self.bouton_pause.verifier_clic(pos, pygame.event.Event(pygame.MOUSEBUTTONDOWN)):
            self.basculer_pause()
            return True

        # Traiter les autres clics uniquement si le jeu n'est PAS en pause et n'est PAS gagné
        if not self.est_en_pause and not self.partie_gagnee:
            # Bouton Vérifier
            if self.bouton_verifier.verifier_clic(pos, pygame.event.Event(pygame.MOUSEBUTTONDOWN)):
                self.verifier_grille()
                return True
                
            # Bouton Aide
            if self.bouton_aide.verifier_clic(pos, pygame.event.Event(pygame.MOUSEBUTTONDOWN)):
                self.aide_utilisateur() # <--- APPEL DE LA MÉTHODE D'INSTANCE ICI
                return True
                
            # Bouton Résoudre
            if self.bouton_resoudre.verifier_clic(pos, pygame.event.Event(pygame.MOUSEBUTTONDOWN)):
                self.resoudre_grille()
                return True
                
            # Bouton Réinitialiser/Nouvelle partie
            if self.bouton_nouveau.verifier_clic(pos, pygame.event.Event(pygame.MOUSEBUTTONDOWN)):
                if self.difficulte == "reprendre":
                    # Réinitialise seulement les cases modifiables
                    for i in range(9):
                        for j in range(9):
                            if not self.original[i][j]:  # Si la case est modifiable
                                self.grid[i][j] = 0
                    
                    self.error_cells = set()
                    self.error_manager.reinitialiser()
                    self.partie_gagnee = False
                    self.chrono.reinitialiser()
                    self.actualisation.reinitialiser()
                    
                    self.message_erreur = "Grille réinitialisée !"
                    self.couleur_message = GREEN
                    self.message_timer = 180
                else:
                    # Comportement normal - nouvelle partie
                    self.reset_game()
                return True
                
            # Bouton Sauvegarder
            if self.bouton_sauvegarder.verifier_clic(pos, pygame.event.Event(pygame.MOUSEBUTTONDOWN)):
                self.sauvegarder_grille()
                return True

            # Gestion du clic sur la grille
            if GRID_TOP <= y < GRID_BOTTOM and \
               GRID_LEFT_MARGIN <= x < GRID_LEFT_MARGIN + GRID_WIDTH_PX:
                row = (y - GRID_TOP) // CELL_SIZE
                col = (x - GRID_LEFT_MARGIN) // CELL_SIZE
                if not self.original[row][col]:  # Seulement si la case est modifiable
                    self.selected = (row, col)
                    return True

        # Si la partie est gagnée, seul le bouton Retour est actif
        # Si le jeu est en pause, seuls les boutons Retour et Pause sont actifs
        return False

    def handle_key(self, key):
        if not self.selected or self.est_en_pause or self.partie_gagnee:
            return

        if K_1 <= key <= K_9:
            num = key - K_0
            self.place_number(num)
        elif key in (K_BACKSPACE, K_DELETE, K_0):
            self.place_number(0)

    def aide_utilisateur(self):
        if self.actualisation.score <= 0:
            self.message_erreur = "Score insuffisant pour l\'aide!"
            self.couleur_message = RED
            self.message_timer = 180
            return

        # Appelez la méthode aide_utilisateur de l'instance Aide
        result = self.aide_instance.aide_utilisateur(selected=self.selected) # <--- MODIFIEZ CETTE LIGNE

        if result:
            i, j, valeur = result
            self.grid[i][j] = valeur
            # Important : Supprimez de error_cells si une valeur correcte est placée via l'aide
            if (i, j) in self.error_cells:
                self.error_cells.remove((i, j))
            self.message_erreur = f"Aide utilisée ! -10 pts (Score actuel : {self.actualisation.score})"
            self.couleur_message = ORANGE
            self.message_timer = 180
        else:
            self.message_erreur = "Impossible d'utiliser l'aide pour le moment."
            self.couleur_message = RED
            self.message_timer = 180


    def basculer_pause(self):
        self.est_en_pause = not self.est_en_pause
        if self.est_en_pause:
            self.chrono.arreter()
            self.bouton_pause.texte = "Reprendre"
        else:
            self.chrono.demarrer()
            self.bouton_pause.texte = "Pause"

    def resoudre_grille(self):
        if not self.partie_gagnee:
            if not hasattr(self, 'solution') or not self.solution:
                self.message_erreur = "Aucune solution disponible!"
                self.couleur_message = RED
                self.message_timer = 180
                return

            for i in range(9):
                for j in range(9):
                    if not self.original[i][j]:
                        self.grid[i][j] = self.solution[i][j]

            self.partie_gagnee = True
            self.solved_automatically = True
            self.error_cells = set()
            self.error_manager.reinitialiser()
            self.chrono.arreter()
            self.actualisation.arreter_timer()
            self.message_erreur = "Grille résolue automatiquement !"
            self.couleur_message = BLUE
            self.message_timer = 180


    def verifier_grille(self):
        self.error_cells = set()
        erreurs = 0

        for i in range(9):
            for j in range(9):
                if self.grid[i][j] != 0 and not grille_valid(self.grid, i, j, self.grid[i][j]):
                    self.error_cells.add((i, j))
                    erreurs += 1

        if erreurs > 0:
            self.message_erreur = f"{erreurs} erreur(s) détectée(s) dans la grille !"
            self.couleur_message = RED
            self.message_timer = 180
            return False

        if self.est_grille_complete():
            self.partie_gagnee = True
            self.solved_automatically = False
            self.chrono.arreter()
            self.actualisation.arreter_timer()
            self.actualisation.calculer_score_final()
            self.message_erreur = "Grille correcte ! Bravo !"
            self.couleur_message = GREEN
            self.message_timer = 180
            return True
        else:
            self.message_erreur = "Grille incomplète. Continuez !"
            self.couleur_message = ORANGE
            self.message_timer = 180
            return False


    def place_number(self, num):
        if not self.selected or self.partie_gagnee or self.est_en_pause:
            return

        row, col = self.selected
        old_val = self.grid[row][col]

        if num == old_val:
            return

        self.grid[row][col] = num
        is_valid = num == 0 or grille_valid(self.grid, row, col, num)
        was_error = (row, col) in self.error_cells

        if was_error and is_valid:
            self.error_cells.remove((row, col))
        elif not is_valid and not was_error:
            self.error_cells.add((row, col))
            self.error_manager.ajouter_erreur()


    def draw(self):
        self.screen.fill(WHITE)
        self._draw_stats()
        self._draw_grid()
        self._draw_buttons()

        if self.partie_gagnee:
            self._draw_victory_screen()
        elif self.est_en_pause:
            self._draw_pause_screen()

        if self.message_timer > 0:
            self.message_timer -= 1
        msg_surface = self.stats_font.render(self.message_erreur, True, self.couleur_message)
        msg_rect = msg_surface.get_rect(center=(ACTUAL_WINDOW_WIDTH//2, BUTTON_TOP + 160))
        self.screen.blit(msg_surface, msg_rect)

        pygame.display.flip()

    def _draw_stats(self):
        temps = self.chrono.temps_format()
        erreurs = self.error_manager.nombre_erreurs()
        score = self.actualisation.score

        stats_text = f"Temps: {temps} | Erreurs: {erreurs} | Score: {score}"
        rendered_stats = self.stats_font.render(stats_text, True, BLACK)
        self.screen.blit(rendered_stats, (ACTUAL_WINDOW_WIDTH//2 - rendered_stats.get_width()//2, 20))

        pos_souris = pygame.mouse.get_pos()
        self.bouton_retour.verifier_survol(pos_souris)
        self.bouton_retour.dessiner(self.screen)
        self.bouton_pause.verifier_survol(pos_souris)
        self.bouton_pause.dessiner(self.screen)


    def _draw_grid(self):
        for i in range(GRID_N_CELLS):
            for j in range(GRID_N_CELLS):
                cell_color = LIGHT_GRAY if (i + j) % 2 == 0 else WHITE
                pygame.draw.rect(self.screen, cell_color,
                                 (GRID_LEFT_MARGIN + j * CELL_SIZE, GRID_TOP + i * CELL_SIZE,
                                  CELL_SIZE, CELL_SIZE))

                if self.grid[i][j] != 0:
                    num_color = BLUE if self.original[i][j] else BLACK
                    text = self.font.render(str(self.grid[i][j]), True, num_color)
                    self.screen.blit(text,
                                     (GRID_LEFT_MARGIN + j * CELL_SIZE + 20,
                                      GRID_TOP + i * CELL_SIZE + 10))
        for i in range(GRID_N_CELLS + 1):
            thickness = 3 if i % 3 == 0 else 1
            pygame.draw.line(self.screen, BLACK,
                             (GRID_LEFT_MARGIN, GRID_TOP + i * CELL_SIZE),
                             (GRID_LEFT_MARGIN + GRID_WIDTH_PX, GRID_TOP + i * CELL_SIZE), thickness)
            pygame.draw.line(self.screen, BLACK,
                             (GRID_LEFT_MARGIN + i * CELL_SIZE, GRID_TOP),
                             (GRID_LEFT_MARGIN + i * CELL_SIZE, GRID_TOP + GRID_WIDTH_PX), thickness)

        for r, c in self.error_cells:
            pygame.draw.rect(self.screen, RED,
                             (GRID_LEFT_MARGIN + c * CELL_SIZE, GRID_TOP + r * CELL_SIZE,
                              CELL_SIZE, CELL_SIZE), 3)

        if self.selected:
            r, c = self.selected
            pygame.draw.rect(self.screen, GREEN,
                             (GRID_LEFT_MARGIN + c * CELL_SIZE, GRID_TOP + r * CELL_SIZE,
                              CELL_SIZE, CELL_SIZE), 3)


    def _draw_buttons(self):
        pos_souris = pygame.mouse.get_pos()

        self.bouton_verifier.verifier_survol(pos_souris)
        self.bouton_verifier.dessiner(self.screen)

        self.bouton_aide.verifier_survol(pos_souris)
        self.bouton_aide.dessiner(self.screen)

        self.bouton_resoudre.verifier_survol(pos_souris)
        self.bouton_resoudre.dessiner(self.screen)

        self.bouton_nouveau.verifier_survol(pos_souris)
        self.bouton_nouveau.dessiner(self.screen)

        self.bouton_sauvegarder.verifier_survol(pos_souris)
        self.bouton_sauvegarder.dessiner(self.screen)


    def _draw_victory_screen(self):
        overlay = pygame.Surface((ACTUAL_WINDOW_WIDTH, ACTUAL_WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((200, 200, 200))
        self.screen.blit(overlay, (0, 0))

        # --- Messages en noir avec espacement uniforme ---
        if self.solved_automatically:
            texts_info = [
                ("Grille résolue automatiquement !", self.victory_font, BLACK),
            ]
        else:
            score_final = self.actualisation.score
            temps_final = self.chrono.temps_format()
            score_max = self.actualisation.scores_initiaux.get(self.difficulte, 70)
            score_pourcentage = max(0, score_final)
            pourcentage = min(100, int((score_pourcentage / score_max) * 100)) if score_max > 0 else 0

            difficulte_color = {
                "facile": DARK_GREEN,
                "moyen": ORANGE,
                "difficile": DARK_RED
            }.get(self.difficulte, BLACK)

            texts_info = [
                ("Félicitations ! Grille complétée avec succès !", self.victory_font, BLACK),
                (f"Difficulté : {self.difficulte.capitalize()}", self.button_font, difficulte_color),
                ("Résumé de votre performance :", self.button_font, BLACK),
                (f"Temps écoulé : {temps_final}", self.small_font, BLACK),
                (f"Score final : {score_final} sur {score_max} ({pourcentage}%)", self.small_font, BLACK),
                (f"Indices utilisés : {self.actualisation.aides_utilisees}", self.small_font, BLACK),
                (f"Erreurs commises : {self.error_manager.nombre_erreurs()}", self.small_font, BLACK)
            ]
        # --- Fin des messages ---

        current_y = ACTUAL_WINDOW_HEIGHT//2 - 150

        line_height = 35
        if self.solved_automatically:
            current_y = ACTUAL_WINDOW_HEIGHT//2 - 50
            line_height = 30

        for i, (text, font, color) in enumerate(texts_info):
            rendered = font.render(text, True, color)
            self.screen.blit(rendered, (ACTUAL_WINDOW_WIDTH//2 - rendered.get_width()//2, current_y + i * line_height))


        self.retour_rect = pygame.Rect(ACTUAL_WINDOW_WIDTH//2 - 100, ACTUAL_WINDOW_HEIGHT - 80, 200, 40)
        pygame.draw.rect(self.screen, GRAY, self.retour_rect, border_radius=10)
        pygame.draw.rect(
            self.screen, BLACK, self.retour_rect, 2, border_radius=10
        )
        btn_text = self.button_font.render("Retour au Menu", True, BLACK)
        self.screen.blit(btn_text, (self.retour_rect.x + (self.retour_rect.width - btn_text.get_width()) // 2, self.retour_rect.y + (self.retour_rect.height - btn_text.get_height()) // 2))


    def _draw_pause_screen(self):
        overlay = pygame.Surface((ACTUAL_WINDOW_WIDTH, ACTUAL_WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((200, 200, 200))
        self.screen.blit(overlay, (0, 0))

        pause_text = self.victory_font.render("Jeu en Pause", True, DARK_BLUE)
        self.screen.blit(pause_text, (ACTUAL_WINDOW_WIDTH//2 - pause_text.get_width()//2, ACTUAL_WINDOW_HEIGHT//2 - 50))


    def est_grille_complete(self):
        for i in range(9):
            for j in range(9):
                if self.grid[i][j] == 0:
                    return False
        return True

    def sauvegarder_grille(self):
        try:
            data = {
                "initial": [[self.solution[i][j] if self.original[i][j] else 0 for j in range(9)] for i in range(9)],
                "modifiee": self.grid,
                "solution": self.solution
            }
            with open('grille_utilisateur.json', 'w') as f:
                json.dump(data, f)
            self.message_erreur = "Grille sauvegardée avec succès!"
            self.couleur_message = GREEN
            self.message_timer = 180
        except Exception as e:
            self.message_erreur = "Erreur lors de la sauvegarde!"
            self.couleur_message = RED
            self.message_timer = 180
            print(f"Erreur: {e}")
            
    def reinitialiser_grille(self):
        """Réinitialise la grille à son état initial (cases modifiables vides)"""
        if hasattr(self, 'grille_complete') and self.grille_complete:
            # Recrée la grille initiale avec seulement les cases fixes remplies
            for i in range(9):
                for j in range(9):
                    if not self.original[i][j]:  # Si la case est modifiable
                        self.grid[i][j] = 0  # Vide la case
            
            self.error_cells = set()
            self.error_manager.reinitialiser()
            self.partie_gagnee = False
            self.chrono.reinitialiser()
            self.actualisation.reinitialiser()
            
            self.message_erreur = "Grille réinitialisée !"
            self.couleur_message = GREEN
            self.message_timer = 180