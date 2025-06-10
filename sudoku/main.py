import pygame
from pygame.locals import *
from interface import SudokuGrid
import sys
import menu
from classique.aide import Aide

WIDTH, HEIGHT = 750, 750

def main(grille_complete=None, grille_trous=None, difficulte="moyen", solution=None):
    if not pygame.get_init():
        pygame.init()

    try:
        screen = pygame.display.get_surface()
        if screen is None:
            screen = pygame.display.set_mode((WIDTH, HEIGHT))
    except:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))

    pygame.display.set_caption("Sudoku")

    grid = SudokuGrid(screen, grille_complete, grille_trous, difficulte)
    if solution:
        grid.solution = solution

    running = True

    while running:
        grid.draw()

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if grid.partie_gagnee:
                    x, y = event.pos
                    if hasattr(grid, 'retour_rect') and grid.retour_rect.collidepoint(x, y):
                        grid.retour_menu = True
                        running = False
                        return True
                else:
                    grid.handle_click(event.pos)

                if grid.retour_menu:
                    running = False
                    return True
            elif event.type == KEYDOWN:
                if grid.selected and not grid.partie_gagnee:
                    if event.key in (K_1, K_KP1): grid.place_number(1)
                    elif event.key in (K_2, K_KP2): grid.place_number(2)
                    elif event.key in (K_3, K_KP3): grid.place_number(3)
                    elif event.key in (K_4, K_KP4): grid.place_number(4)
                    elif event.key in (K_5, K_KP5): grid.place_number(5)
                    elif event.key in (K_6, K_KP6): grid.place_number(6)
                    elif event.key in (K_7, K_KP7): grid.place_number(7)
                    elif event.key in (K_8, K_KP8): grid.place_number(8)
                    elif event.key in (K_9, K_KP9): grid.place_number(9)
                    elif event.key in (K_DELETE, K_BACKSPACE): grid.place_number(0)

    if hasattr(grid, 'retour_menu') and grid.retour_menu:
        return True
    else:
        pygame.quit()
        return False

if __name__ == "__main__":
    import accueil
    if accueil.lancer_accueil():
        menu.main()
        