import pygame
import sys



class RemplirGrille:
    """Classe pour gérer l'interface de remplissage de grille Sudoku"""
    
    # Constantes de classe
    WIDTH, HEIGHT = 750, 750
    
    # Couleurs
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    LIGHT_BLUE = (173, 216, 230)
    RED = (255, 0, 0)
    
    # Paramètres de la grille
    CELL_SIZE_GRID = 60
    N_CELLS = 9
    GRID_TOTAL_WIDTH = N_CELLS * CELL_SIZE_GRID
    GRID_TOTAL_HEIGHT = N_CELLS * CELL_SIZE_GRID
    
    def __init__(self):
        """Initialise l'interface de remplissage de grille"""
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Remplir votre Sudoku")
        
        # État de la grille
        self.grid = [[0 for _ in range(9)] for _ in range(9)]
        self.selected_cell = None
        
        # Polices
        self.font = pygame.font.SysFont("comicsans", 40)
        self.small_font = pygame.font.SysFont("comicsans", 30)
        
        # Calcul des positions
        self._calculate_positions()
        
        # État de l'application
        self.running = True
    
    def _calculate_positions(self):
        """Calcule les positions des éléments de l'interface"""
        # Position de la grille
        self.grid_start_x = (self.WIDTH - self.GRID_TOTAL_WIDTH) // 2
        self.grid_start_y = 50
        
        # Position des boutons
        self.button_y_pos = self.grid_start_y + self.GRID_TOTAL_HEIGHT + 30
        self.button_width = 270
        self.button_height = 50
        self.button_spacing = 20
        
        total_buttons_width = (self.button_width * 2) + self.button_spacing
        button_menu_x_start = (self.WIDTH - total_buttons_width) // 2
        
        # Rectangles des boutons
        self.button_menu_rect = pygame.Rect(
            button_menu_x_start, 
            self.button_y_pos, 
            self.button_width, 
            self.button_height
        )
        
        self.button_rect = pygame.Rect(
            button_menu_x_start + self.button_width + self.button_spacing, 
            self.button_y_pos, 
            self.button_width, 
            self.button_height
        )
    
    def is_valid_move(self, row, col, num):
        """Vérifie si un mouvement est valide selon les règles du Sudoku"""
        # Vérification de la ligne
        for j in range(self.N_CELLS):
            if j != col and self.grid[row][j] == num:
                return False
        
        # Vérification de la colonne
        for i in range(self.N_CELLS):
            if i != row and self.grid[i][col] == num:
                return False
        
        # Vérification du carré 3x3
        box_row_start = (row // 3) * 3
        box_col_start = (col // 3) * 3
        for i in range(3):
            for j in range(3):
                r_box = box_row_start + i
                c_box = box_col_start + j
                if (r_box != row or c_box != col) and self.grid[r_box][c_box] == num:
                    return False
        
        return True
    
    def is_grid_valid(self):
        """Vérifie si la grille entière est valide"""
        for i in range(self.N_CELLS):
            for j in range(self.N_CELLS):
                num = self.grid[i][j]
                if num != 0 and not self.is_valid_move(i, j, num):
                    return False
        return True
    
    def save_grid(self):
        """Sauvegarde la grille dans un fichier"""
        with open("grille_personnalisee.txt", "w") as f:
            for row in self.grid:
                f.write(" ".join(str(num) for num in row) + "\n")
    
    def draw_grid_lines(self):
        """Dessine les lignes de la grille"""
        for i in range(self.N_CELLS + 1):
            line_width = 4 if i % 3 == 0 else 1
            
            # Lignes horizontales
            pygame.draw.line(
                self.screen, 
                self.BLACK,
                (self.grid_start_x, self.grid_start_y + i * self.CELL_SIZE_GRID),
                (self.grid_start_x + self.GRID_TOTAL_WIDTH, self.grid_start_y + i * self.CELL_SIZE_GRID),
                line_width
            )
            
            # Lignes verticales
            pygame.draw.line(
                self.screen, 
                self.BLACK,
                (self.grid_start_x + i * self.CELL_SIZE_GRID, self.grid_start_y),
                (self.grid_start_x + i * self.CELL_SIZE_GRID, self.grid_start_y + self.GRID_TOTAL_HEIGHT),
                line_width
            )
    
    def draw_numbers(self):
        """Dessine les nombres dans la grille"""
        for r in range(self.N_CELLS):
            for c in range(self.N_CELLS):
                if self.grid[r][c] != 0:
                    # Couleur rouge si le nombre est invalide
                    color = self.BLACK if self.is_valid_move(r, c, self.grid[r][c]) else self.RED
                    text = self.font.render(str(self.grid[r][c]), True, color)
                    self.screen.blit(
                        text, 
                        (self.grid_start_x + c * self.CELL_SIZE_GRID + 20,
                         self.grid_start_y + r * self.CELL_SIZE_GRID + 10)
                    )
    
    def draw_selection(self):
        """Dessine la sélection de cellule"""
        if self.selected_cell:
            r_sel, c_sel = self.selected_cell
            pygame.draw.rect(
                self.screen, 
                self.LIGHT_BLUE,
                (self.grid_start_x + c_sel * self.CELL_SIZE_GRID, 
                 self.grid_start_y + r_sel * self.CELL_SIZE_GRID,
                 self.CELL_SIZE_GRID, 
                 self.CELL_SIZE_GRID), 
                3
            )
    
    def draw_buttons(self):
        """Dessine les boutons"""
        # Bouton "Lancer IA"
        pygame.draw.rect(self.screen, self.LIGHT_BLUE, self.button_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.BLACK, self.button_rect, 2, border_radius=10)
        button_text = self.small_font.render("Lancer IA", True, self.BLACK)
        text_rect = button_text.get_rect(center=self.button_rect.center)
        self.screen.blit(button_text, text_rect)
        
        # Bouton "Retour au menu"
        pygame.draw.rect(self.screen, self.LIGHT_BLUE, self.button_menu_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.BLACK, self.button_menu_rect, 2, border_radius=10)
        menu_text = self.small_font.render("Retour au menu", True, self.BLACK)
        menu_text_rect = menu_text.get_rect(center=self.button_menu_rect.center)
        self.screen.blit(menu_text, menu_text_rect)
    
    def draw_grid(self):
        """Dessine la grille complète"""
        self.screen.fill(self.WHITE)
        self.draw_grid_lines()
        self.draw_numbers()
        self.draw_selection()
        self.draw_buttons()
        pygame.display.update()
    
    def handle_lancer_ia_click(self):
        """Gère le clic sur le bouton 'Lancer IA'"""
        if self.is_grid_valid():
            self.save_grid()
            self.running = False 
            import AI.ia_solve as ia_solve 
            pygame.quit() # Quitter pygame pour que ia_solve puisse l'initialiser proprement
            ia_solve.main() # Lance la résolution IA
            
        else:
            print("Grille invalide : conflits détectés !")
            
    
    def handle_menu_click(self):
        """Gère le clic sur le bouton 'Retour au menu'"""
        self.running = False
        
    def handle_grid_click(self, pos):
        """Gère le clic sur la grille"""
        x, y = pos
        if (self.grid_start_x <= x < self.grid_start_x + self.GRID_TOTAL_WIDTH and 
            self.grid_start_y <= y < self.grid_start_y + self.GRID_TOTAL_HEIGHT):
            
            c = (x - self.grid_start_x) // self.CELL_SIZE_GRID
            r = (y - self.grid_start_y) // self.CELL_SIZE_GRID
            
            if 0 <= r < self.N_CELLS and 0 <= c < self.N_CELLS:
                self.selected_cell = (r, c)
            else:
                self.selected_cell = None
        else:
            self.selected_cell = None
    
    def handle_mouse_click(self, pos):
        """Gère tous les clics de souris"""
        if self.button_rect.collidepoint(pos):
            self.handle_lancer_ia_click()
        elif self.button_menu_rect.collidepoint(pos):
            self.handle_menu_click()
        else:
            self.handle_grid_click(pos)
    
    def handle_key_input(self, key):
        """Gère la saisie au clavier"""
        if self.selected_cell:
            i_sel, j_sel = self.selected_cell
            
            # Effacer la cellule
            if key in [pygame.K_0, pygame.K_DELETE, pygame.K_BACKSPACE]:
                self.grid[i_sel][j_sel] = 0
            
            # Saisir un chiffre
            elif pygame.K_1 <= key <= pygame.K_9:
                value = key - pygame.K_0
                self.grid[i_sel][j_sel] = value
    
    def handle_events(self):
        """Gère tous les événements pygame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_click(event.pos)
            
            elif event.type == pygame.KEYDOWN:
                self.handle_key_input(event.key)
    
    def run(self):
        """Lance la boucle principale de l'application"""
        while self.running:
            self.draw_grid()
            self.handle_events()
        
        
        pygame.quit() # Quitter pygame ici pour que le menu puisse le réinitialiser
        return True # Retourne True pour indiquer que le menu doit reprendre


def main():
    """Fonction principale pour lancer l'interface de remplissage"""
    remplir_grille_app = RemplirGrille()
    # Le retour de cette fonction sera utilisé par MenuSudoku.execute_action
    return remplir_grille_app.run()


if __name__ == "__main__":
    
    main()