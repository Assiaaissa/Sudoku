import pygame

class Chronometre:
    def reinitialiser(self):
        """Réinitialise complètement le chronomètre"""
        self.start_time = 0
        self.elapsed_time = 0
        self.running = False
    def __init__(self):
        self.start_time = 0
        self.elapsed_time = 0
        self.running = False
    
    def demarrer(self):
        self.start_time = pygame.time.get_ticks()
        self.running = True
    
    def arreter(self):
        if self.running:
            self.elapsed_time += pygame.time.get_ticks() - self.start_time
            self.running = False
    
    def temps_format(self):
        total_ms = self.elapsed_time
        if self.running:
            total_ms += pygame.time.get_ticks() - self.start_time
        total_secs = total_ms // 1000
        return f"{total_secs // 60:02d}:{total_secs % 60:02d}"