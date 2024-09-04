import pygame
import sys
import random

from constants import *

pygame.init()

# Crear la ventana
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ninja Frog - La aventura de las frutas")
# Fondo de la pantalla
fondos = ["assets/Blue.png", "assets/Green.png", "assets/Purple.png", "assets/Gray.png", "assets/Pink.png", "assets/Yellow.png", "assets/Brown.png"]
# Imágenes de frutas y enemigos
frutas = ["assets/fruits/Apple.png", "assets/fruits/Bananas.png", "assets/fruits/Cherries.png", "assets/fruits/Kiwi.png", "assets/fruits/Melon.png", "assets/fruits/Pineapple.png", "assets/fruits/Strawberry.png"]
enemigos = ["assets/enemies/PinkMan.png", "assets/enemies/MaskDude.png", "assets/enemies/VirtualGuy.png"]
# Música de fondo
pygame.mixer.music.load("assets/time_for_adventure.mp3")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.5)
# Sonido de colisión
hit_sound = pygame.mixer.Sound("assets/hit.wav")
# Sonido de obtener vida
obtain_life_sound = pygame.mixer.Sound("assets/obtain_life.wav")
# Fondo de pantalla aleatorio
bg = pygame.image.load(random.choice(fondos))
# Tamaño del fondo
bg_width, bg_height = bg.get_size()

# Variable para controlar el bucle principal
running = True
clock = pygame.time.Clock()

class Player:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.x = col * SQUARE_SIZE
        self.y = row * SQUARE_SIZE
        self.sprite_sheet = pygame.image.load("assets/ninja_frog.png")
        self.hit_sprite_sheet = pygame.image.load("assets/ninja_frog_hit.png")
        self.frames = self.load_frames(self.sprite_sheet)
        self.hit_frames = self.load_frames(self.hit_sprite_sheet, hit=True)
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 100  # Milisegundos entre frames
        self.lives = 5  # Agregar atributo de vidas
        self.is_hit = False
        self.hit_start_time = 0
        self.hit_duration = 500  # Duración de la animación de "hit" en milisegundos

    # Cargar los frames de la animación del jugador
    def load_frames(self, sprite_sheet, hit=False):
        frames = []
        frame_count = 7 if hit else 11
        for i in range(frame_count):
            frame = sprite_sheet.subsurface(pygame.Rect(i * 32, 0, 32, 32))
            frame = pygame.transform.scale(frame, (64, 64))  # Escalar a 64x64
            frames.append(frame)
        return frames

    # Actualizar la animación del jugador
    def update(self):
        now = pygame.time.get_ticks()
        if self.is_hit:
            if now - self.hit_start_time > self.hit_duration:
                self.is_hit = False
                self.frames = self.load_frames(self.sprite_sheet)
            else:
                self.frames = self.hit_frames

        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)

    def drawSprite(self):
        if self.frames:
            screen.blit(self.frames[self.current_frame], (self.x, self.y))
        

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.col = self.x // SQUARE_SIZE
        self.row = self.y // SQUARE_SIZE
        if self.x < 0:
            self.x = 0
        if self.x > SCREEN_WIDTH - 64:
            self.x = SCREEN_WIDTH - 64
        if self.y < 0:
            self.y = 0
        if self.y > SCREEN_HEIGHT - 64:
            self.y = SCREEN_HEIGHT - 64

    def lose_life(self, enemies, score):
        self.lives -= 1
        hit_sound.play()
        if self.lives <= 0:
            show_game_over_menu(score)
        else:
            self.is_hit = True
            self.hit_start_time = pygame.time.get_ticks()
            self.frames = self.hit_frames  # Asegurarse de que los frames de hit se carguen
            self.current_frame = 0  # Reiniciar el frame actual
            self.respawn(enemies)

    def respawn(self, enemies):
        while True:
            new_row = random.randint(0, (SCREEN_HEIGHT // SQUARE_SIZE) - 1)
            new_col = random.randint(0, (SCREEN_WIDTH // SQUARE_SIZE) - 1)
            new_x = new_col * SQUARE_SIZE
            new_y = new_row * SQUARE_SIZE
            if not any(enemy.x == new_x and enemy.y == new_y for enemy in enemies):
                self.row = new_row
                self.col = new_col
                self.x = new_x
                self.y = new_y
                break

class Enemy:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.x = col * SQUARE_SIZE
        self.y = row * SQUARE_SIZE
        self.sprite_sheet = pygame.image.load(random.choice(enemigos))
        self.frames = self.load_frames()
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 100  # Milisegundos entre frames
        self.last_move = pygame.time.get_ticks()
        self.move_interval = 500  # Milisegundos entre movimientos

    def load_frames(self):
        frames = []
        for i in range(11):
            frame = self.sprite_sheet.subsurface(pygame.Rect(i * 32, 0, 32, 32))
            frame = pygame.transform.scale(frame, (64, 64))  # Escalar a 64x64
            frames.append(frame)
        return frames

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)
        
        # Movimiento aleatorio cada segundo
        if now - self.last_move > self.move_interval:
            self.random_move()
            self.last_move = now

    def drawSprite(self):
        screen.blit(self.frames[self.current_frame], (self.x, self.y))

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.col = self.x // SQUARE_SIZE
        self.row = self.y // SQUARE_SIZE
        if self.x < 0:
            self.x = 0
        if self.x > SCREEN_WIDTH - 64:
            self.x = SCREEN_WIDTH - 64
        if self.y < 0:
            self.y = 0
        if self.y > SCREEN_HEIGHT - 64:
            self.y = SCREEN_HEIGHT - 64

    def random_move(self):
        directions = [(64, 0), (-64, 0), (0, 64), (0, -64)]
        dx, dy = random.choice(directions)
        self.move(dx, dy)
        
class Fruits:
    def __init__(self, row=0, col=0):
        self.row = row
        self.col = col
        self.x = col * SQUARE_SIZE
        self.y = row * SQUARE_SIZE
        self.sprite_sheet = pygame.image.load(random.choice(frutas))
        self.frames = self.load_frames()
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 100  # Milisegundos entre frames
        self.last_move = pygame.time.get_ticks()
        
    def random_sprite(self):
        self.sprite_sheet = pygame.image.load(random.choice(frutas))
        self.frames = self.load_frames()
        
    def load_frames(self):
        frames = []
        for i in range(11):
            frame = self.sprite_sheet.subsurface(pygame.Rect(i * 32, 0, 32, 32))
            frame = pygame.transform.scale(frame, (64, 64))  # Escalar a 64x64
            frames.append(frame)
        return frames

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)

    def drawSprite(self):
        if self.frames:
            screen.blit(self.frames[self.current_frame], (self.x, self.y))
    
    def random_move(self, enemies):
        self.random_sprite()
        while True:
            new_row = random.randint(0, (SCREEN_HEIGHT // SQUARE_SIZE) - 1)
            new_col = random.randint(0, (SCREEN_WIDTH // SQUARE_SIZE) - 1)
            new_x = new_col * SQUARE_SIZE
            new_y = new_row * SQUARE_SIZE
            if not any(enemy.x == new_x and enemy.y == new_y for enemy in enemies):
                self.row = new_row
                self.col = new_col
                self.x = new_x
                self.y = new_y
                break

def show_menu():
    menu_running = True
    while menu_running:
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 74)
        text = font.render("Ninja Frog", True, (255, 255, 255))
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 4))

        start_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, 200, 100)
        pygame.draw.rect(screen, (255, 255, 255), start_button)
        font = pygame.font.Font(None, 48)
        text = font.render("Empezar", True, (0, 0, 0))
        screen.blit(text, (start_button.x + start_button.width // 2 - text.get_width() // 2, start_button.y + start_button.height // 2 - text.get_height() // 2))

        # Descripción del juego
        font = pygame.font.Font(None, 24)
        text = font.render("Mueve al ninja con las flechas del teclado", True, (255, 255, 255))
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 + 150))
        text = font.render("Evita a los enemigos y recolecta las frutas", True, (255, 255, 255))
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 + 180))
        
        

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    menu_running = False

        pygame.display.flip()
        clock.tick(60)

def show_game_over_menu(final_score):
    game_over_running = True
    pygame.mixer.music.load("assets/game_over.mp3")
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.5)
    
    while game_over_running:
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 74)
        text = font.render("Fin del juego", True, (255, 0, 0))
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 4))

        # Mostrar la puntuación final
        font = pygame.font.Font(None, 48)
        score_text = font.render(f"Puntuación Final: {final_score}", True, (255, 255, 255))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 200))

        # Botones de reiniciar y salir
        restart_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, 200, 100)
        pygame.draw.rect(screen, (255, 255, 255), restart_button)
        font = pygame.font.Font(None, 48)
        text = font.render("Reiniciar", True, (0, 0, 0))
        screen.blit(text, (restart_button.x + restart_button.width // 2 - text.get_width() // 2, restart_button.y + restart_button.height // 2 - text.get_height() // 2))

        quit_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100, 200, 100)
        pygame.draw.rect(screen, (255, 255, 255), quit_button)
        font = pygame.font.Font(None, 48)
        text = font.render("Salir", True, (0, 0, 0))
        screen.blit(text, (quit_button.x + quit_button.width // 2 - text.get_width() // 2, quit_button.y + quit_button.height // 2 - text.get_height() // 2))

        # Eventos de ratón para los botones de reiniciar y salir
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.collidepoint(event.pos):
                    game_over_running = False
                    Game()  # Reiniciar el juego
                if quit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(60)

def Game():
    global running
    player = Player(0, 0)
    fruit = Fruits()
    enemies = [Enemy(5, 5), Enemy(5, 5), Enemy(5, 5), Enemy(5, 5), Enemy(5, 5), Enemy(5, 5)]  # Inicializar los enemigos
    start_time = pygame.time.get_ticks()
    score = 0
    life_for_fruit = 0
    bg = pygame.image.load(random.choice(fondos)) # Cambiar el fondo al azar
    # Canción de combate
    pygame.mixer.music.load("assets/battle.mp3")
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.5)

    while running:
        # Si se presiona el botón de cerrar la ventana, se cierra el juego
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit() # Cerrar la ventana
                sys.exit() # Salir del programa 

            # Eventos de teclado para mover al jugador
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_LEFT:
                    player.move(-64, 0)
                if event.key == pygame.K_RIGHT:
                    player.move(64, 0)
                if event.key == pygame.K_UP:
                    player.move(0, -64)
                if event.key == pygame.K_DOWN:
                    player.move(0, 64)

        # Dibujar el fondo con un patrón de cuadros
        for x in range(0, SCREEN_WIDTH, bg_width):
            for y in range(0, SCREEN_HEIGHT, bg_height):
                screen.blit(bg, (x, y))

        # Actualizar y dibujar al jugador y a los enemigos
        player.update()
        player.drawSprite()
        
        fruit.update()
        fruit.drawSprite()

        for enemy in enemies:
            enemy.update()
            enemy.drawSprite()

        # Comprobar colisiones con enemigos
        for enemy in enemies:
            if player.x == enemy.x and player.y == enemy.y:
                score -= random.randint(1, 10)
                if score < 0:
                    score = 0
                player.lose_life(enemies, score)

        # Comprobar colisiones con frutas
        if player.x == fruit.x and player.y == fruit.y:
            score += random.randint(1, 10) # Asignar un valor aleatorio a la puntuación al recoger una fruta en el rango de 1 a 10
            fruit.random_move(enemies)
            life_for_fruit += 1
            if life_for_fruit == 5: # Cada 5 frutas recogidas, se añade una vida
                player.lives += 1
                obtain_life_sound.play()
                life_for_fruit = 0

        # Dibuja la puntuación y las vidas restantes
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Puntuación: {score}", True, (210, 31, 102))
        lives_text = font.render(f"Vidas: {player.lives}", True, (210, 31, 102))
        screen.blit(score_text, (10, SCREEN_HEIGHT - 30))
        screen.blit(lives_text, (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 30))

        # Actualizar la pantalla
        pygame.display.flip()
        clock.tick(60)  # Limitar la velocidad del juego a 60 FPS

show_menu()
Game()