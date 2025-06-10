import pygame
import random
import socket
import threading
import pickle
import time
import sys

# Constantes du jeu
LARGEUR, HAUTEUR = 750, 750
TAILLE_GRILLE = 450
TAILLE_CELLULE = TAILLE_GRILLE // 9
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
GRIS = (200, 200, 200)
BLEU_CLAIR = (180, 200, 255)
ROUGE_CLAIR = (255, 180, 180)
VERT_CLAIR = (180, 255, 180)
JAUNE = (255, 255, 0)
BLEU = (0, 0, 255)
ROUGE = (255, 0, 0)

# Constantes réseau
PORT = 5555
TAMPON = 4096
FORMAT = 'utf-8'

class SudokuReseau:
    def __init__(self, est_hote=False, ip_hote=None):
        pygame.init()
        self.fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR))
        pygame.display.set_caption("Sudoku Multijoueur")

        self.police_petite = pygame.font.SysFont('Arial', 20)
        self.police_moyenne = pygame.font.SysFont('Arial', 30)
        self.police_grande = pygame.font.SysFont('Arial', 40)
        
        self.est_hote = est_hote
        self.id_joueur = 1 if est_hote else 2
        self.tour_joueur = 1
        self.selection = None
        self.jeu_en_cours = False
        self.gagnant = None
        self.message = "En attente de connexion..." if est_hote else "Connexion à l'hôte..."
        
        if est_hote:
            self.grille = self.generer_grille()
            self.grille_originale = [row[:] for row in self.grille]
            self.grille_joueur1 = [row[:] for row in self.grille]
            self.grille_joueur2 = [row[:] for row in self.grille]
        else:
            self.grille = [[0 for _ in range(9)] for _ in range(9)]
            self.grille_originale = [[0 for _ in range(9)] for _ in range(9)]
            self.grille_joueur1 = [[0 for _ in range(9)] for _ in range(9)]
            self.grille_joueur2 = [[0 for _ in range(9)] for _ in range(9)]
        
        self.connecte = False
        self.connexion = None
        self.client = None
        self.ip_hote = ip_hote if ip_hote else self.obtenir_ip_locale()
        
        if est_hote:
            self.thread_serveur = threading.Thread(target=self.demarrer_serveur)
            self.thread_serveur.daemon = True
            self.thread_serveur.start()
        else:
            self.thread_client = threading.Thread(target=self.connecter_client)
            self.thread_client.daemon = True
            self.thread_client.start()

    def obtenir_ip_locale(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

    def demarrer_serveur(self):
        self.serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.serveur.bind(('', PORT))
            self.serveur.listen(1)
            self.message = f"En attente d'un adversaire... IP: {self.ip_hote}, PORT: {PORT}"
            
            self.connexion, adresse = self.serveur.accept()
            self.connecte = True
            self.message = f"Joueur connecté depuis {adresse[0]}"
            
            donnees_initiales = {
                'grille': self.grille,
                'debut': True
            }
            self.connexion.send(pickle.dumps(donnees_initiales))
            
            self.jeu_en_cours = True
            
            while self.connecte:
                try:
                    donnees = self.connexion.recv(TAMPON)
                    if not donnees:
                        break
                    
                    donnees_recues = pickle.loads(donnees)
                    
                    if 'coup' in donnees_recues:
                        ligne, colonne, valeur = donnees_recues['coup']
                        self.grille_joueur2[ligne][colonne] = valeur
                        
                        if self.est_grille_complete(self.grille_joueur2):
                            self.gagnant = 2
                            self.jeu_en_cours = False
                        else:
                            self.tour_joueur = 1
                    
                    elif 'changement_tour' in donnees_recues:
                        self.tour_joueur = donnees_recues['changement_tour']
                
                except Exception as e:
                    print(f"Erreur serveur: {e}")
                    break
            
            self.connecte = False
            self.message = "Connexion perdue"
        
        except Exception as e:
            self.message = f"Erreur de serveur: {e}"
        finally:
            try:
                self.serveur.close()
            except:
                pass

    def connecter_client(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect((self.ip_hote, PORT))
            self.connecte = True
            self.message = f"Connecté à l'hôte: {self.ip_hote}"
            
            donnees = self.client.recv(TAMPON)
            donnees_recues = pickle.loads(donnees)
            
            if 'grille' in donnees_recues and 'debut' in donnees_recues:
                self.grille = donnees_recues['grille']
                self.grille_originale = [row[:] for row in self.grille]
                self.grille_joueur1 = [row[:] for row in self.grille]
                self.grille_joueur2 = [row[:] for row in self.grille]
                self.jeu_en_cours = True
            
            while self.connecte:
                try:
                    donnees = self.client.recv(TAMPON)
                    if not donnees:
                        break
                    
                    donnees_recues = pickle.loads(donnees)
                    
                    if 'coup' in donnees_recues:
                        ligne, colonne, valeur = donnees_recues['coup']
                        self.grille_joueur1[ligne][colonne] = valeur
                        
                        if self.est_grille_complete(self.grille_joueur1):
                            self.gagnant = 1
                            self.jeu_en_cours = False
                        else:
                            self.tour_joueur = 2
                    
                    elif 'changement_tour' in donnees_recues:
                        self.tour_joueur = donnees_recues['changement_tour']
                
                except Exception as e:
                    print(f"Erreur client: {e}")
                    break
            
            self.connecte = False
            self.message = "Connexion perdue"
        
        except Exception as e:
            self.message = f"Erreur de connexion: {e}"
        finally:
            try:
                self.client.close()
            except:
                pass

    def generer_grille(self):
        grille = [[0 for _ in range(9)] for _ in range(9)]
        
        solution = [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9]
        ]
        
        indices = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(indices)
        
        for i, j in indices[:30]:
            grille[i][j] = solution[i][j]
        
        return grille

    def est_placement_valide(self, grille, ligne, col, num):
        if num == 0:
            return True
            
        for j in range(9):
            if grille[ligne][j] == num and j != col:
                return False
                
        for i in range(9):
            if grille[i][col] == num and i != ligne:
                return False
                
        debut_carre_ligne = (ligne // 3) * 3
        debut_carre_col = (col // 3) * 3
        
        for i in range(debut_carre_ligne, debut_carre_ligne + 3):
            for j in range(debut_carre_col, debut_carre_col + 3):
                if grille[i][j] == num and (i != ligne or j != col):
                    return False
                    
        return True

    def est_grille_complete(self, grille):
        for i in range(9):
            for j in range(9):
                if grille[i][j] == 0:
                    return False
        return True

    def dessiner_grille(self):
        decalage = (LARGEUR - TAILLE_GRILLE) // 2
        
        for i in range(10):
            epaisseur = 3 if i % 3 == 0 else 1
            pygame.draw.line(self.fenetre, NOIR, 
                           (decalage, decalage + i * TAILLE_CELLULE), 
                           (decalage + TAILLE_GRILLE, decalage + i * TAILLE_CELLULE), 
                           epaisseur)
            pygame.draw.line(self.fenetre, NOIR, 
                           (decalage + i * TAILLE_CELLULE, decalage), 
                           (decalage + i * TAILLE_CELLULE, decalage + TAILLE_GRILLE), 
                           epaisseur)
        
        if self.selection and self.tour_joueur == self.id_joueur:
            ligne, colonne = self.selection
            rect_x = decalage + colonne * TAILLE_CELLULE
            rect_y = decalage + ligne * TAILLE_CELLULE
            pygame.draw.rect(self.fenetre, JAUNE, 
                           (rect_x, rect_y, TAILLE_CELLULE, TAILLE_CELLULE))
        
        ma_grille = self.grille_joueur1 if self.id_joueur == 1 else self.grille_joueur2
        
        if self.grille_originale is None:
            return
            
        for i in range(9):
            for j in range(9):
                if self.grille_originale[i][j] != 0:
                    texte = self.police_moyenne.render(str(self.grille_originale[i][j]), True, BLEU)
                    self.fenetre.blit(texte, (decalage + j * TAILLE_CELLULE + 15, 
                                            decalage + i * TAILLE_CELLULE + 10))
                elif ma_grille[i][j] != 0:
                    texte = self.police_moyenne.render(str(ma_grille[i][j]), True, NOIR)
                    self.fenetre.blit(texte, (decalage + j * TAILLE_CELLULE + 15, 
                                            decalage + i * TAILLE_CELLULE + 10))
        
        statut = f"Vous êtes le Joueur {self.id_joueur}"
        texte_statut = self.police_petite.render(statut, True, NOIR)
        self.fenetre.blit(texte_statut, (20, 20))
        
        statut_tour = f"Tour du Joueur {self.tour_joueur}"
        couleur_tour = VERT_CLAIR if self.tour_joueur == self.id_joueur else ROUGE_CLAIR
        texte_tour = self.police_petite.render(statut_tour, True, NOIR)
        rect_tour = texte_tour.get_rect(center=(LARGEUR // 2, 20))
        pygame.draw.rect(self.fenetre, couleur_tour, 
                       (rect_tour.x - 10, rect_tour.y - 5, 
                        rect_tour.width + 20, rect_tour.height + 10))
        self.fenetre.blit(texte_tour, rect_tour)
        
        texte_message = self.police_petite.render(self.message, True, NOIR)
        self.fenetre.blit(texte_message, (20, HAUTEUR - 30))
        
        if self.gagnant:
            message_gagnant = f"Joueur {self.gagnant} a gagné!"
            texte_gagnant = self.police_grande.render(message_gagnant, True, VERT_CLAIR if self.gagnant == self.id_joueur else ROUGE)
            rect_gagnant = texte_gagnant.get_rect(center=(LARGEUR // 2, HAUTEUR - 60))
            self.fenetre.blit(texte_gagnant, rect_gagnant)

    def envoyer_coup(self, ligne, colonne, valeur):
        try:
            donnees = {
                'coup': (ligne, colonne, valeur)
            }
            
            if self.est_hote and self.connexion:
                self.connexion.send(pickle.dumps(donnees))
                return True
            elif not self.est_hote and self.client:
                self.client.send(pickle.dumps(donnees))
                return True
            else:
                self.message = "Erreur: connexion non établie"
                return False
                
        except Exception as e:
            self.message = f"Erreur d'envoi: {e}"
            return False

    def envoyer_changement_tour(self, nouveau_tour):
        try:
            donnees = {
                'changement_tour': nouveau_tour
            }
            
            if self.est_hote and self.connexion:
                self.connexion.send(pickle.dumps(donnees))
                return True
            elif not self.est_hote and self.client:
                self.client.send(pickle.dumps(donnees))
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Erreur envoi changement tour: {e}")
            return False

    def jouer_coup(self, ligne, colonne, valeur):
        if self.tour_joueur != self.id_joueur:
            self.message = "Ce n'est pas votre tour!"
            return False
        
        if self.grille_originale[ligne][colonne] != 0:
            self.message = "Cette case est fixe et ne peut pas être modifiée!"
            nouveau_tour = 2 if self.tour_joueur == 1 else 1
            self.tour_joueur = nouveau_tour
            self.envoyer_changement_tour(nouveau_tour)
            return False
        
        ma_grille = self.grille_joueur1 if self.id_joueur == 1 else self.grille_joueur2
        
        if not self.est_placement_valide(ma_grille, ligne, colonne, valeur):
            self.message = "Ce placement n'est pas valide selon les règles du Sudoku!"
            nouveau_tour = 2 if self.tour_joueur == 1 else 1
            self.tour_joueur = nouveau_tour
            self.envoyer_changement_tour(nouveau_tour)
            return False
        
        if self.id_joueur == 1:
            self.grille_joueur1[ligne][colonne] = valeur
        else:
            self.grille_joueur2[ligne][colonne] = valeur
        
        if not self.envoyer_coup(ligne, colonne, valeur):
            return False
        
        if self.est_grille_complete(ma_grille):
            self.gagnant = self.id_joueur
            self.jeu_en_cours = False
            self.message = "Vous avez gagné!"
        else:
            nouveau_tour = 2 if self.tour_joueur == 1 else 1
            self.tour_joueur = nouveau_tour
            self.envoyer_changement_tour(nouveau_tour)
            self.message = "Coup joué avec succès!"
        
        return True

    def demarrer(self):
        horloge = pygame.time.Clock()
        en_cours = True
        
        while en_cours:
            self.fenetre.fill(BLANC)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    en_cours = False
                
                if self.jeu_en_cours and self.tour_joueur == self.id_joueur:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            pos_x, pos_y = event.pos
                            decalage = (LARGEUR - TAILLE_GRILLE) // 2
                            
                            if (decalage <= pos_x <= decalage + TAILLE_GRILLE and 
                                decalage <= pos_y <= decalage + TAILLE_GRILLE):
                                colonne = (pos_x - decalage) // TAILLE_CELLULE
                                ligne = (pos_y - decalage) // TAILLE_CELLULE
                                self.selection = (ligne, colonne)
                    
                    elif event.type == pygame.KEYDOWN:
                        if self.selection:
                            if pygame.K_1 <= event.key <= pygame.K_9:
                                valeur = event.key - pygame.K_0
                                ligne, colonne = self.selection
                                self.jouer_coup(ligne, colonne, valeur)
                            elif event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
                                ligne, colonne = self.selection
                                self.jouer_coup(ligne, colonne, 0)
            
            self.dessiner_grille()
            pygame.display.flip()
            horloge.tick(30)
        
        try:
            if self.est_hote and self.connexion:
                self.connexion.close()
            elif not self.est_hote and self.client:
                self.client.close()
            if self.est_hote:
                self.serveur.close()
        except:
            pass
            
        pygame.quit()
        sys.exit()

def afficher_menu():
    pygame.init()
    fenetre = pygame.display.set_mode((750, 750))
    pygame.display.set_caption("Sudoku Multijoueur - Menu")

    police = pygame.font.SysFont('Arial', 20)

    bouton_hote = pygame.Rect(280, 300, 200, 50)
    bouton_client = pygame.Rect(280, 370, 200, 50)

    ip_hote = ""
    saisie_active = False

    while True:
        fenetre.fill(BLANC)
        
        titre = police.render("Sudoku Multijoueur", True, NOIR)
        fenetre.blit(titre, (310, 250))
        
        pygame.draw.rect(fenetre, BLEU_CLAIR, bouton_hote)
        pygame.draw.rect(fenetre, ROUGE_CLAIR, bouton_client)
        
        texte_hote = police.render("Héberger une partie", True, NOIR)
        texte_client = police.render("Rejoindre une partie", True, NOIR)
        
        fenetre.blit(texte_hote, (bouton_hote.x + 25, bouton_hote.y + 15))
        fenetre.blit(texte_client, (bouton_client.x + 25, bouton_client.y + 15))
        
        pygame.draw.rect(fenetre, GRIS if not saisie_active else JAUNE, 
                       (280, 500, 200, 30), 2 if not saisie_active else 3)
        
        texte_ip = police.render(ip_hote, True, NOIR)
        fenetre.blit(texte_ip, (285, 505))
        
        texte_info = police.render("IP de l'hôte:", True, NOIR)
        fenetre.blit(texte_info, (340, 470))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if bouton_hote.collidepoint(event.pos):
                    pygame.quit()
                    return True, None
                    
                if bouton_client.collidepoint(event.pos):
                    if ip_hote.strip():
                        pygame.quit()
                        return False, ip_hote.strip()
                
                saisie_active = pygame.Rect(280, 505, 200, 30).collidepoint(event.pos)
                
            if event.type == pygame.KEYDOWN:
                if saisie_active:
                    if event.key == pygame.K_RETURN:
                        if ip_hote.strip():
                            pygame.quit()
                            return False, ip_hote.strip()
                    elif event.key == pygame.K_BACKSPACE:
                        ip_hote = ip_hote[:-1]
                    else:
                        ip_hote += event.unicode
        
        pygame.display.flip()

if __name__ == "__main__":
    try:
        est_hote, ip_hote = afficher_menu()
        jeu = SudokuReseau(est_hote, ip_hote)
        jeu.demarrer()
    except Exception as e:
        print(f"Erreur critique: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)

def lancer_mode_multijoueur():
    est_hote, ip_hote = afficher_menu()
    jeu = SudokuReseau(est_hote, ip_hote)
    jeu.demarrer()