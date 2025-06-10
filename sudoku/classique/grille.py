
from copy import deepcopy
import random
from typing import List, Optional, Tuple


class Grille:

    """Représente la matrice 9×9 et contient génération, validation, résolution."""

    def __init__(self, matrice: Optional[List[List[int]]] = None) -> None:
        
        self.matrice: List[List[int]] = deepcopy(matrice) if matrice else [
            [0] * 9 for _ in range(9)
        ]


    def est_valide(self, r: int, c: int, val: int) -> bool:
        """True si `val` peut être placée en (r, c)."""
        for i in range(9):
            if self.matrice[r][i] == val and i != c:
                return False
            if self.matrice[i][c] == val and i != r:
                return False

        br, bc = 3 * (r // 3), 3 * (c // 3)
        for i in range(br, br + 3):
            for j in range(bc, bc + 3):
                if self.matrice[i][j] == val and (i != r or j != c):
                    return False
        return True

   
    def remplir_backtracking(self) -> bool:
        """Backtracking : remplit la grille courante (renvoie True si succès)."""
        for r in range(9):
            for c in range(9):
                if self.matrice[r][c] == 0:
                    chiffres = list(range(1, 10))
                    random.shuffle(chiffres)
                    for val in chiffres:
                        if self.est_valide(r, c, val):
                            self.matrice[r][c] = val
                            if self.remplir_backtracking():
                                return True
                            self.matrice[r][c] = 0
                    return False
        return True  

    @classmethod
    def grille_aleatoire_complete(cls) -> "Grille":
        """Fabrique et renvoie une grille totalement remplie et valide."""
        g = cls()
        g.remplir_backtracking()
        return g
    
    def creuser(self, nb_cases_vides: int) -> "Grille":
        """Retourne une nouvelle Grille avec `nb_cases_vides` trous et solution unique."""
        copie = deepcopy(self.matrice)
        positions = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(positions)
        trous = 0

        for r, c in positions:
            if copie[r][c] == 0:
                continue
            sauvegarde = copie[r][c]
            copie[r][c] = 0

            
            solutions = []
            self._solve_multiple(deepcopy(copie), solutions, limite=2)
            if len(solutions) != 1:           
                copie[r][c] = sauvegarde      
            else:
                trous += 1
                if trous >= nb_cases_vides:
                    break

        return Grille(copie)

 
    def resoudre(self) -> bool:
        """Résout la grille en place ; renvoie True si solvable."""
        vide = self._case_vide()
        if not vide:
            return True  # fini
        r, c = vide
        for val in range(1, 10):
            if self.est_valide(r, c, val):
                self.matrice[r][c] = val
                if self.resoudre():
                    return True
                self.matrice[r][c] = 0
        return False

  
    def _case_vide(self) -> Optional[Tuple[int, int]]:
        for i in range(9):
            for j in range(9):
                if self.matrice[i][j] == 0:
                    return i, j
        return None

    def _solve_multiple(self, grid: List[List[int]],
                        solutions: List[List[List[int]]], limite: int = 2) -> None:
        """Cherche plusieurs solutions (stoppe dès qu’il y en a `limite`)."""
        vide = None
        for r in range(9):
            for c in range(9):
                if grid[r][c] == 0:
                    vide = (r, c)
                    break
            if vide:
                break

        if not vide:
            solutions.append(deepcopy(grid))
            return
        r, c = vide
        for val in range(1, 10):
            if self.est_valide_case(grid, r, c, val):
                grid[r][c] = val
                self._solve_multiple(grid, solutions, limite)
                grid[r][c] = 0
                if len(solutions) >= limite:
                    return


    @staticmethod
    def est_valide_case(grid, r, c, val):
        for i in range(9):
            if grid[r][i] == val and i != c:
                return False
            if grid[i][c] == val and i != r:
                return False
        br, bc = 3 * (r // 3), 3 * (c // 3)
        for i in range(br, br + 3):
            for j in range(bc, bc + 3):
                if grid[i][j] == val and (i != r or j != c):
                    return False
        return True

    
    def __getitem__(self, item):
        return self.matrice[item]

    def __str__(self):
        lignes = [
            " ".join(str(c) if c else "." for c in row) for row in self.matrice
        ]
        return "\n".join(lignes)
