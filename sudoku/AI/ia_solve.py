import pygame
import sys
import time


class SudokuSolverAI:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 750, 750
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Résolution par IA")
        
        # Couleurs
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GREEN = (0, 200, 0)
        self.RED = (255, 0, 0)
        self.YELLOW = (255, 255, 0)
        self.LIGHT_BLUE = (173, 216, 230)
        
        # Polices
        self.font = pygame.font.SysFont("comicsans", 40)
        self.small_font = pygame.font.SysFont("comicsans", 30)
        
        # Paramètres de la grille
        self.CELL_SIZE_GRID = 60
        self.N_CELLS = 9
        self.GRID_TOTAL_WIDTH = self.N_CELLS * self.CELL_SIZE_GRID
        self.GRID_TOTAL_HEIGHT = self.N_CELLS * self.CELL_SIZE_GRID
        
        self.GRID_START_X = (self.WIDTH - self.GRID_TOTAL_WIDTH) // 2
        self.GRID_START_Y = (self.HEIGHT - self.GRID_TOTAL_HEIGHT) // 2
        
        # Données de la grille
        self.grid = []
        self.original_grid = []
        self.menu_button_rect = None

    def load_grid(self):
        """Charge la grille depuis le fichier ou crée une grille vide"""
        grid = []
        try:
            with open("grille_personnalisee.txt", "r") as f:
                for line in f:
                    grid.append([int(num) for num in line.strip().split()])
            if len(grid) != self.N_CELLS or not all(len(row) == self.N_CELLS for row in grid):
                print(f"Avertissement: La grille dans grille_personnalisee.txt n'est pas {self.N_CELLS}x{self.N_CELLS}. Utilisation d'une grille vide.")
                grid = [[0 for _ in range(self.N_CELLS)] for _ in range(self.N_CELLS)]
        except FileNotFoundError:
            print("Fichier grille_personnalisee.txt non trouvé. Utilisation d'une grille vide.")
            grid = [[0 for _ in range(self.N_CELLS)] for _ in range(self.N_CELLS)]
        except Exception as e:
            print(f"Erreur lors du chargement de la grille: {e}. Utilisation d'une grille vide.")
            grid = [[0 for _ in range(self.N_CELLS)] for _ in range(self.N_CELLS)]
        return grid

    def draw_grid(self):
        """Dessine la grille Sudoku sur l'écran"""
        self.screen.fill(self.WHITE)

        # Dessiner les lignes de la grille
        for i in range(self.N_CELLS + 1):
            line_width = 4 if i % 3 == 0 else 1
            pygame.draw.line(self.screen, self.BLACK,
                             (self.GRID_START_X, self.GRID_START_Y + i * self.CELL_SIZE_GRID),
                             (self.GRID_START_X + self.GRID_TOTAL_WIDTH, self.GRID_START_Y + i * self.CELL_SIZE_GRID),
                             line_width)
            pygame.draw.line(self.screen, self.BLACK,
                             (self.GRID_START_X + i * self.CELL_SIZE_GRID, self.GRID_START_Y),
                             (self.GRID_START_X + i * self.CELL_SIZE_GRID, self.GRID_START_Y + self.GRID_TOTAL_HEIGHT),
                             line_width)

        # Dessiner les numéros
        for r in range(self.N_CELLS):
            for c in range(self.N_CELLS):
                if self.grid[r][c] != 0:
                    color = self.GREEN if self.original_grid[r][c] != 0 else self.BLACK
                    text_surface = self.font.render(str(self.grid[r][c]), True, color)
                    self.screen.blit(text_surface, (self.GRID_START_X + c * self.CELL_SIZE_GRID + 20,
                                               self.GRID_START_Y + r * self.CELL_SIZE_GRID + 10))

        # Dessiner le bouton menu
        menu_button_rect = pygame.Rect(self.WIDTH // 2 - 150, self.HEIGHT - 60, 300, 50)
        pygame.draw.rect(self.screen, self.LIGHT_BLUE, menu_button_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.BLACK, menu_button_rect, 2, border_radius=10)
        menu_text_surface = self.small_font.render("Retour au menu", True, self.BLACK)
        menu_text_rect = menu_text_surface.get_rect(center=menu_button_rect.center)
        self.screen.blit(menu_text_surface, menu_text_rect)

        pygame.display.update()
        return menu_button_rect

    def is_valid(self, row, col, num):
        """Vérifie si un numéro peut être placé à une position donnée"""
        # Vérifier la ligne
        for x in range(self.N_CELLS):
            if self.grid[row][x] == num and x != col:
                return False
        
        # Vérifier la colonne
        for x in range(self.N_CELLS):
            if self.grid[x][col] == num and x != row:
                return False
        
        # Vérifier le carré 3x3
        start_row, start_col = row - row % 3, col - col % 3
        for i in range(3):
            for j in range(3):
                if self.grid[i + start_row][j + start_col] == num and \
                   (i + start_row != row or j + start_col != col):
                    return False
        return True

    def solve_with_animation(self):
        """Résout le Sudoku avec animation"""
        for r in range(self.N_CELLS):
            for c in range(self.N_CELLS):
                if self.grid[r][c] == 0:
                    for num_to_try in range(1, self.N_CELLS + 1):
                        # Gérer les événements
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            elif event.type == pygame.MOUSEBUTTONDOWN:
                                if self.menu_button_rect and self.menu_button_rect.collidepoint(event.pos):
                                    return "MENU" # Indique qu'on veut retourner au menu
                            elif event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_ESCAPE:
                                    return "MENU" # Indique qu'on veut retourner au menu

                        if self.is_valid(r, c, num_to_try):
                            self.grid[r][c] = num_to_try
                            self.menu_button_rect = self.draw_grid()
                            
                            # Effet visuel pour la cellule actuelle
                            pygame.draw.rect(self.screen, self.GREEN,
                                             (self.GRID_START_X + c * self.CELL_SIZE_GRID, 
                                              self.GRID_START_Y + r * self.CELL_SIZE_GRID,
                                              self.CELL_SIZE_GRID, self.CELL_SIZE_GRID), 3)
                            pygame.display.update()
                            time.sleep(0.05)

                            # Récursion
                            result = self.solve_with_animation()
                            if result is True:
                                return True
                            if result == "MENU": # Propager le signal de retour au menu
                                return "MENU"

                            # Backtrack
                            self.grid[r][c] = 0
                            self.menu_button_rect = self.draw_grid()
                            
                            # Effet visuel pour le backtrack
                            pygame.draw.rect(self.screen, self.RED,
                                             (self.GRID_START_X + c * self.CELL_SIZE_GRID, 
                                              self.GRID_START_Y + r * self.CELL_SIZE_GRID,
                                              self.CELL_SIZE_GRID, self.CELL_SIZE_GRID), 3)
                            pygame.display.update()
                            time.sleep(0.05)
                    return False
        return True

    def show_message(self, message_text):
        """Affiche un message à l'écran"""
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        message_surface = self.small_font.render(message_text, True, self.YELLOW)
        message_bg_rect = message_surface.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
        message_bg_rect.inflate_ip(20, 20)

        pygame.draw.rect(self.screen, self.BLACK, message_bg_rect, border_radius=10)
        self.screen.blit(message_surface, message_surface.get_rect(center=message_bg_rect.center))

        if self.menu_button_rect:
            pygame.draw.rect(self.screen, self.LIGHT_BLUE, self.menu_button_rect, border_radius=10)
            pygame.draw.rect(self.screen, self.BLACK, self.menu_button_rect, 2, border_radius=10)
            menu_text_surface_btn = self.small_font.render("Retour au menu", True, self.BLACK)
            menu_text_rect_btn = menu_text_surface_btn.get_rect(center=self.menu_button_rect.center)
            self.screen.blit(menu_text_surface_btn, menu_text_rect_btn)

        pygame.display.update()

        message_loop = True
        start_time = time.time()
        while message_loop:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.menu_button_rect and self.menu_button_rect.collidepoint(event.pos):
                        message_loop = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        message_loop = False
            
            if time.time() - start_time > 5: # Afficher le message pendant au moins 5 secondes
                message_loop = False
            pygame.time.wait(10)

    def run(self):
        """Lance le solveur IA"""
        # Initialiser les données
        self.grid = self.load_grid()
        self.original_grid = [row[:] for row in self.grid]
        
        # Dessiner la grille initiale
        self.menu_button_rect = self.draw_grid()
        
        # Résoudre avec animation
        solution_status = self.solve_with_animation()
        
        # Afficher le résultat
        if solution_status == "MENU":
            pygame.quit() # Quitter Pygame ici pour que le parent puisse reprendre
            return # Sortir de la fonction pour revenir à l'appelant (remplir_grille.main())
        elif not solution_status:
            self.show_message("La grille est insoluble.")
        else:
            self.show_message("Résolution terminée!")
        
      
        running = True
        while running:
            self.menu_button_rect = self.draw_grid() # Redessiner la grille pour que le bouton soit interactif
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit() # Quitter Pygame en quittant
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.menu_button_rect and self.menu_button_rect.collidepoint(event.pos):
                        running = False
                        pygame.quit() # Quitter Pygame avant de sortir
                        return # Retourne au point d'appel (remplir_grille.main())
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        pygame.quit() # Quitter Pygame avant de sortir
                        return # Retourne au point d'appel (remplir_grille.main())
            pygame.time.Clock().tick(30)
        
        
        pygame.quit()


def main():
    """Fonction principale"""
    solver = SudokuSolverAI()
    solver.run() 


if __name__ == "__main__":
    main()