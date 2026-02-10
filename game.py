import pygame
import random
import os
import math
import sys

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 480, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Гонки")
clock = pygame.time.Clock()

# Загрузка изображений
player_img = pygame.image.load(resource_path("assets/player.png")).convert_alpha()
enemy_img = pygame.image.load(resource_path("assets/enemy.png")).convert_alpha()

# Загрузка звуков
crash_sound = pygame.mixer.Sound(resource_path("sounds/crash.wav"))
engine_sound = pygame.mixer.Sound(resource_path("sounds/engine.wav"))
game_over_sound = pygame.mixer.Sound(resource_path("sounds/game_over.wav"))
menu_music = pygame.mixer.Sound(resource_path("sounds/menu_music.wav"))
coin_sound = pygame.mixer.Sound(resource_path("sounds/coin.wav"))
explosion_sound = pygame.mixer.Sound(resource_path("sounds/explosion.wav"))

# Громкость
crash_sound.set_volume(1.0)
engine_sound.set_volume(0.8)
game_over_sound.set_volume(0.7)
menu_music.set_volume(0.5)
coin_sound.set_volume(0.8)
explosion_sound.set_volume(1.0)

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (240, 30, 30)
BLUE = (30, 144, 255)
GRAY = (70, 70, 70)
YELLOW = (255, 255, 0)
GREEN = (0, 180, 0)

# Шрифт
font = pygame.font.Font(None, 48)
font_big = pygame.font.Font(None, 72)

# Глобальные переменные для передачи очков
last_score = 0
best_score = 0

def load_high_score():
    if os.path.exists("highscore.txt"):
        with open("highscore.txt", "r") as f:
            return int(f.read())
    return 0

def save_high_score(score):
    with open("highscore.txt", "w") as f:
        f.write(str(score))

def load_records():
    if os.path.exists("records.txt"):
        with open("records.txt", "r") as f:
            records = []
            for line in f.readlines():
                line = line.strip()
                if line:
                    records.append(int(line))
            return sorted(records, reverse=True)[:5]
    return []

def save_record(score):
    records = load_records()
    records.append(score)
    records = sorted(records, reverse=True)[:5]
    with open("records.txt", "w") as f:
        for r in records:
            f.write(str(r) + "\n")
    return records

def get_place(score):
    records = load_records()
    for i, r in enumerate(records):
        if score >= r:
            return i + 1
    if len(records) < 5:
        return len(records) + 1
    return 0

def draw_road(offset):
    screen.fill((34, 139, 34))
    pygame.draw.rect(screen, (50, 50, 50), (40, 0, WIDTH - 80, HEIGHT))
    pygame.draw.rect(screen, (80, 80, 80), (55, 0, WIDTH - 110, HEIGHT))
    pygame.draw.rect(screen, WHITE, (58, 0, 4, HEIGHT))
    pygame.draw.rect(screen, WHITE, (WIDTH - 62, 0, 4, HEIGHT))

    for i in range(0, HEIGHT, 60):
        y = (i + offset) % HEIGHT
        pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 3, y, 6, 30))

    pygame.draw.rect(screen, (0, 160, 0), (0, 0, 40, HEIGHT))
    pygame.draw.rect(screen, (0, 160, 0), (WIDTH - 40, 0, 40, HEIGHT))

    for i in range(0, HEIGHT, 30):
        y = (i + offset) % HEIGHT
        color = RED if (i // 30) % 2 == 0 else WHITE
        pygame.draw.rect(screen, color, (40, y, 15, 15))

    for i in range(0, HEIGHT, 30):
        y = (i + offset) % HEIGHT
        color = RED if (i // 30) % 2 == 0 else WHITE
        pygame.draw.rect(screen, color, (WIDTH - 55, y, 15, 15))

def draw_text_center(text, y, size=48, color=WHITE):
    font_ = pygame.font.Font(None, size)
    surface = font_.render(text, True, color)
    rect = surface.get_rect(center=(WIDTH // 2, y))
    screen.blit(surface, rect)

class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frame = 0
        self.max_frames = 30
        self.alive = True

    def update(self):
        self.frame += 1
        if self.frame >= self.max_frames:
            self.alive = False

    def draw(self):
        progress = self.frame / self.max_frames

        radius1 = int(40 * progress)
        color1 = (255, int(100 * progress), 0)
        pygame.draw.circle(screen, color1, (self.x, self.y), radius1)

        radius2 = int(25 * progress)
        color2 = (255, int(200 * progress), 0)
        pygame.draw.circle(screen, color2, (self.x, self.y), radius2)

        radius3 = max(1, int(15 * (1 - progress)))
        pygame.draw.circle(screen, WHITE, (self.x, self.y), radius3)

        if self.frame < 15:
            for i in range(8):
                angle = i * (math.pi / 4) + progress * 2
                dist = int(30 * progress)
                sx = self.x + int(math.cos(angle) * dist)
                sy = self.y + int(math.sin(angle) * dist)
                spark_size = max(1, int(4 * (1 - progress)))
                pygame.draw.circle(screen, YELLOW, (sx, sy), spark_size)
                
def draw_road_night(offset):
    # Тёмная трава
    screen.fill((10, 40, 10))

    # Тёмная обочина
    pygame.draw.rect(screen, (30, 30, 30), (40, 0, WIDTH - 80, HEIGHT))

    # Тёмный асфальт
    pygame.draw.rect(screen, (40, 40, 40), (55, 0, WIDTH - 110, HEIGHT))

    # Белые линии (тусклые)
    pygame.draw.rect(screen, (150, 150, 150), (58, 0, 4, HEIGHT))
    pygame.draw.rect(screen, (150, 150, 150), (WIDTH - 62, 0, 4, HEIGHT))

    # Центральная разметка (тусклая)
    for i in range(0, HEIGHT, 60):
        y = (i + offset) % HEIGHT
        pygame.draw.rect(screen, (150, 150, 150), (WIDTH // 2 - 3, y, 6, 30))

    # Тёмная трава по бокам
    pygame.draw.rect(screen, (5, 30, 5), (0, 0, 40, HEIGHT))
    pygame.draw.rect(screen, (5, 30, 5), (WIDTH - 40, 0, 40, HEIGHT))

    # Бордюр (тусклый)
    for i in range(0, HEIGHT, 30):
        y = (i + offset) % HEIGHT
        color = (150, 20, 20) if (i // 30) % 2 == 0 else (150, 150, 150)
        pygame.draw.rect(screen, color, (40, y, 15, 15))

    for i in range(0, HEIGHT, 30):
        y = (i + offset) % HEIGHT
        color = (150, 20, 20) if (i // 30) % 2 == 0 else (150, 150, 150)
        pygame.draw.rect(screen, color, (WIDTH - 55, y, 15, 15))

    # Фонари на обочине
    for i in range(0, HEIGHT, 150):
        y = (i + offset) % HEIGHT
        pygame.draw.circle(screen, (255, 255, 150), (45, y), 5)
        pygame.draw.circle(screen, (255, 255, 150), (WIDTH - 45, y), 5)
        # Свечение фонаря
        glow = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 255, 100, 50), (15, 15), 15)
        screen.blit(glow, (30, y - 15))
        screen.blit(glow, (WIDTH - 60, y - 15))

    # Звёзды на траве
    random.seed(42)
    for _ in range(20):
        sx = random.choice([random.randint(5, 35), random.randint(WIDTH - 35, WIDTH - 5)])
        sy = random.randint(0, HEIGHT)
        brightness = random.randint(150, 255)
        pygame.draw.circle(screen, (brightness, brightness, brightness), (sx, sy), 1)
    random.seed()

def draw_headlights(player_rect):
    # Конус света фар
    light = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    cx = player_rect.x + player_rect.width // 2
    cy = player_rect.y

    # Левая фара
    points_left = [
        (cx - 10, cy),
        (cx - 60, cy - 200),
        (cx - 5, cy - 200)
    ]
    pygame.draw.polygon(light, (255, 255, 200, 40), points_left)

    # Правая фара
    points_right = [
        (cx + 10, cy),
        (cx + 5, cy - 200),
        (cx + 60, cy - 200)
    ]
    pygame.draw.polygon(light, (255, 255, 200, 40), points_right)

    # Общее свечение
    pygame.draw.ellipse(light, (255, 255, 200, 25), (cx - 70, cy - 250, 140, 280))

    screen.blit(light, (0, 0))                

def game_loop():
    global last_score, best_score

    player_visual = pygame.Rect(WIDTH // 2 - 30, HEIGHT - 110, 60, 60)
    player_img_scaled = pygame.transform.scale(player_img, (60, 60))
    enemies = []
    coins = []
    explosions = []
    coin_timer = 0
    score = 0
    lives = 3
    speed = 5
    max_speed = 15
    speed_increase = 0.005
    frame = 0
    offset = 0
    high_score = load_high_score()
    running = True
    paused = False
    night_mode = False

    engine_sound.play(-1)

    while running:
        dt = clock.tick(60)
        frame += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                engine_sound.stop()
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                    if paused:
                        engine_sound.stop()
                    else:
                        engine_sound.play(-1)
                if event.key == pygame.K_n:
                    night_mode = not night_mode        

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            engine_sound.stop()
            return "menu"

        if paused:
            draw_text_center("ПАУЗА", HEIGHT // 2 - 40, 72, YELLOW)
            draw_text_center("P - продолжить", HEIGHT // 2 + 20, 36, WHITE)
            draw_text_center("ESC - в меню", HEIGHT // 2 + 60, 36, WHITE)
            pygame.display.flip()
            continue

        if keys[pygame.K_LEFT] and player_visual.left > 65:
            player_visual.x -= 6
        if keys[pygame.K_RIGHT] and player_visual.right < WIDTH - 65:
            player_visual.x += 6

        spawn_delay = max(20, int(40 - speed))
        if frame % spawn_delay == 0:
            x = random.choice([80, 150, 220, 290, 360])
            enemy_rect = pygame.Rect(x, -60, 60, 60)
            enemies.append(enemy_rect)

        coin_timer += 1
        if coin_timer > 80:
            coin_x = random.choice([100, 170, 240, 310, 380])
            coin_rect = pygame.Rect(coin_x, -30, 25, 25)
            coins.append(coin_rect)
            coin_timer = 0

        for enemy in enemies[:]:
            enemy.y += int(speed)
            player_hitbox = player_visual.inflate(-35, -35)
            enemy_hitbox = enemy.inflate(-35, -35)

            if enemy_hitbox.colliderect(player_hitbox):
                lives -= 1
                ex = enemy.x + enemy.width // 2
                ey = enemy.y + enemy.height // 2
                explosions.append(Explosion(ex, ey))
                explosion_sound.play()
                enemies.remove(enemy)
            elif enemy.top > HEIGHT:
                enemies.remove(enemy)
                score += 10

        for coin in coins[:]:
            coin.y += int(speed)
            player_hitbox = player_visual.inflate(-10, -10)

            if coin.colliderect(player_hitbox):
                coins.remove(coin)
                score += 50
                coin_sound.play()
            elif coin.top > HEIGHT:
                coins.remove(coin)

        if speed < max_speed:
            speed += speed_increase

        offset = int(frame * speed) % HEIGHT
        if night_mode:
            draw_road_night(offset)
        else:
            draw_road(offset)

        screen.blit(player_img_scaled, player_visual)
        if night_mode:
            draw_headlights(player_visual)

        for enemy in enemies:
            scaled_enemy = pygame.transform.scale(enemy_img, (enemy.width, enemy.height))
            screen.blit(scaled_enemy, enemy)

        for coin in coins:
            pygame.draw.circle(screen, YELLOW, (coin.x + 12, coin.y + 12), 12)
            pygame.draw.circle(screen, (200, 200, 0), (coin.x + 12, coin.y + 12), 12, 2)
            coin_font = pygame.font.Font(None, 20)
            coin_text = coin_font.render("$", True, BLACK)
            screen.blit(coin_text, (coin.x + 7, coin.y + 4))

        for explosion in explosions[:]:
            explosion.update()
            explosion.draw()
            if not explosion.alive:
                explosions.remove(explosion)

        # Ночное затемнение
        if night_mode:
            darkness = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(darkness, (0, 0, 0, 100), (0, 0, WIDTH, HEIGHT))
            screen.blit(darkness, (0, 0))

        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 80))
        score_text = font.render(f"Очки: {score}", True, YELLOW)
        lives_text = font.render(f"♥ {lives}", True, RED)
        speed_text = font.render(f"x{speed:.1f}", True, WHITE)

        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 40))
        screen.blit(speed_text, (WIDTH - 100, 10))
        if night_mode:
            mode_text = font.render("N", True, YELLOW)
            screen.blit(mode_text, (WIDTH - 100, 40))

        pygame.display.flip()

        if lives <= 0:
            engine_sound.stop()
            game_over_sound.play()
            if score > high_score:
                high_score = score
                save_high_score(score)
            last_score = score
            best_score = high_score
            return "game_over"

def show_menu():
    menu_music.play(-1)
    while True:
        screen.fill(BLACK)
        draw_text_center("2D ГОНКИ", 150, 80, YELLOW)
        draw_text_center("1 - Играть", 300, 48, WHITE)
        draw_text_center("2 - Рекорды", 360, 48, WHITE)
        draw_text_center("3 - Выход", 420, 48, WHITE)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu_music.stop()
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    menu_music.stop()
                    return "play"
                elif event.key == pygame.K_2:
                    menu_music.stop()
                    return "records"
                elif event.key == pygame.K_3:
                    menu_music.stop()
                    return "quit"

def show_records():
    while True:
        screen.fill(BLACK)
        draw_text_center("ТАБЛИЦА РЕКОРДОВ", 60, 56, YELLOW)

        records = load_records()

        if len(records) == 0:
            draw_text_center("Пока пусто!", 300, 48, WHITE)
        else:
            for i, record in enumerate(records):
                if i == 0:
                    color = YELLOW
                elif i == 1:
                    color = WHITE
                elif i == 2:
                    color = (205, 127, 50)
                else:
                    color = WHITE

                y = 150 + i * 70
                draw_text_center(f"{i + 1}.  {record} очков", y, 48, color)

        draw_text_center("ESC - назад", HEIGHT - 60, 36, WHITE)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"

def show_game_over():
    records = save_record(last_score)
    place = get_place(last_score)

    while True:
        screen.fill(BLACK)
        draw_text_center("ИГРА ОКОНЧЕНА", 80, 72, RED)
        draw_text_center(f"Ваш счёт: {last_score}", 170, 56, YELLOW)
        draw_text_center(f"Рекорд: {best_score}", 230, 48, GREEN)

        if place > 0 and place <= 5:
            draw_text_center(f"Вы на {place} месте!", 300, 48, YELLOW)

        if last_score >= best_score and last_score > 0:
            draw_text_center("НОВЫЙ РЕКОРД!", 360, 48, YELLOW)

        draw_text_center("1 - Играть снова", 450, 40, WHITE)
        draw_text_center("2 - Рекорды", 500, 40, WHITE)
        draw_text_center("3 - В меню", 550, 40, WHITE)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "play"
                elif event.key == pygame.K_2:
                    return "records"
                elif event.key == pygame.K_3:
                    return "menu"

def main():
    state = "menu"
    while True:
        if state == "menu":
            state = show_menu()
        elif state == "play":
            state = game_loop()
        elif state == "game_over":
            state = show_game_over()
        elif state == "records":
            state = show_records()
        elif state == "quit":
            break

    pygame.quit()

if __name__ == "__main__":
    main()