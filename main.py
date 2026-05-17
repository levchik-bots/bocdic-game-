import pygame
import sys
import random
import math

pygame.init()
pygame.font.init()

# Авто-определение разрешения экрана смартфона
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
if HEIGHT > WIDTH:
    WIDTH, HEIGHT = HEIGHT, WIDTH

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Bogdik's Basics: Prestige Complete")

# --- ПАЛИТРА ЦВЕТОВ ---
DARK_BG = (12, 12, 14)
PANEL_BG = (22, 22, 26)
WALL_COLOR = (45, 45, 55)  
TEXT_WHITE = (240, 240, 245)
TEXT_GRAY = (110, 110, 120)
MB_GREEN = (0, 255, 128)
ACCENT_RED = (255, 70, 70)
ACCENT_BLUE = (60, 140, 255)
YELLOW_NOTE = (255, 210, 60)
ORANGE_KVASS = (230, 120, 35)

# Стили локаций (Цвет фона пола, цвет стен, Название)
LOCATIONS = {
    1: ((15, 15, 18), (55, 55, 65), "Заброшенный Класс"),
    2: ((18, 14, 14), (70, 50, 50), "Технический Коридор"),
    3: ((12, 18, 15), (45, 65, 55), "Серверная MB TEAM"),
    4: ((16, 12, 20), (65, 50, 80), "Архив Реголита"),
    5: ((10, 15, 20), (45, 60, 80), "Лаборатория Альбедо"),
    6: ((20, 18, 12), (75, 65, 50), "Склад Пятерочки"),
    7: ((15, 20, 15), (50, 75, 50), "Бункер Душнилы"),
    8: ((22, 16, 12), (80, 60, 45), "Секретный Отсек 8"),
    9: ((12, 12, 12), (40, 40, 40), "Ядро Системы"),
    10:((25, 10, 10), (90, 40, 40), "Финальный Экзамен")
}

# Адаптивные шрифты
font = pygame.font.SysFont("Arial", int(HEIGHT * 0.04))
mid_font = pygame.font.SysFont("Arial", int(HEIGHT * 0.05))
big_font = pygame.font.SysFont("Arial", int(HEIGHT * 0.07), bold=True)
logo_font = pygame.font.SysFont("Arial", int(HEIGHT * 0.1), bold=True)

def load_image(name, color, size):
    try:
        img = pygame.image.load(name).convert_alpha()
        return pygame.transform.scale(img, size)
    except:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill(color)
        return surf

# Размеры объектов
p_size = int(HEIGHT * 0.07)
player_img = load_image("bogdik.jpg", ACCENT_BLUE, (p_size, p_size))
enemy_img = load_image("dunnila.jpg", ACCENT_RED, (int(p_size*1.2), int(p_size*1.2)))

# Сохранения и прогресс
prestige_count = 0
unlocked_level = 1  
current_level = 1
notebooks_collected = 0
total_notebooks = 7

# Игровые состояния
game_state = "SPLASH"
splash_timer = 0

# Виртуальный Джойстик
joy_center = (int(WIDTH * 0.14), int(HEIGHT * 0.74))
joy_radius = int(HEIGHT * 0.11)
stick_pos = list(joy_center)
stick_radius = int(HEIGHT * 0.045)
is_dragging_joy = False
player_pos = [WIDTH // 4, HEIGHT // 2]
player_speed = HEIGHT * 0.016  

# Механика Кваса
kvass_rect = None          
has_kvass_item = False     
kvass_button = pygame.Rect(WIDTH - int(WIDTH * 0.16), HEIGHT - int(HEIGHT * 0.22), int(WIDTH * 0.12), int(HEIGHT * 0.14))
stun_timer = 0             

# --- ГЕНЕРАЦИЯ СТЕН С КОМНАТАМИ ---
def generate_level(level):
    global walls, notebooks, enemy_pos, enemy_base_speed, player_pos, exit_door, kvass_rect, has_kvass_item, stun_timer
    
    player_pos = [WIDTH // 4, HEIGHT // 2]
    enemy_pos = [WIDTH - int(WIDTH*0.12), HEIGHT - int(HEIGHT*0.15)]
    
    enemy_base_speed = (HEIGHT * 0.0035) + (level * 0.0005) + (prestige_count * 0.0006)
    stun_timer = 0
    has_kvass_item = False
    
    thick = int(HEIGHT * 0.035)
    walls = [
        pygame.Rect(0, 0, WIDTH, thick),
        pygame.Rect(0, 0, thick, HEIGHT),
        pygame.Rect(WIDTH - thick, 0, thick, HEIGHT),
        pygame.Rect(0, HEIGHT - thick, WIDTH, thick),
    ]
    
    w_mid_h = int(HEIGHT * 0.18)
    if level in [1, 2, 3]:
        walls.extend([
            pygame.Rect(int(WIDTH*0.33), 0, thick, int(HEIGHT*0.4)),
            pygame.Rect(int(WIDTH*0.33), int(HEIGHT*0.65), thick, int(HEIGHT*0.35)),
            pygame.Rect(int(WIDTH*0.66), 0, thick, int(HEIGHT*0.35)),
            pygame.Rect(int(WIDTH*0.66), int(HEIGHT*0.6), thick, int(HEIGHT*0.4))
        ])
    elif level in [4, 5, 6, 7]:
        walls.extend([
            pygame.Rect(int(WIDTH*0.2), int(HEIGHT*0.5) - thick//2, int(WIDTH*0.25), thick),
            pygame.Rect(int(WIDTH*0.55), int(HEIGHT*0.5) - thick//2, int(WIDTH*0.25), thick),
            pygame.Rect(WIDTH // 2 - thick//2, int(HEIGHT*0.1), thick, int(HEIGHT*0.3)),
            pygame.Rect(WIDTH // 2 - thick//2, int(HEIGHT*0.6), thick, int(HEIGHT*0.3))
        ])
    else:
        walls.extend([
            pygame.Rect(int(WIDTH*0.25), int(HEIGHT*0.2), int(WIDTH*0.5), thick),
            pygame.Rect(int(WIDTH*0.25), int(HEIGHT*0.7), int(WIDTH*0.5), thick),
            pygame.Rect(int(WIDTH*0.25), int(HEIGHT*0.2), thick, w_mid_h),
            pygame.Rect(int(WIDTH*0.75), int(HEIGHT*0.5), thick, w_mid_h),
            pygame.Rect(int(WIDTH*0.48), int(HEIGHT*0.35), thick, int(HEIGHT*0.3))
        ])

    exit_door = pygame.Rect(WIDTH - thick - 10, HEIGHT // 2 - int(HEIGHT*0.1), thick + 10, int(HEIGHT*0.2))

    # Сбор тетрадей
    notebooks = []
    n_size = int(HEIGHT * 0.05)
    while len(notebooks) < total_notebooks:
        rx = random.randint(thick * 2, WIDTH - thick * 3)
        ry = random.randint(thick * 2, HEIGHT - thick * 3)
        candidate = pygame.Rect(rx, ry, n_size, n_size)
        
        in_wall = any(candidate.colliderect(w) for w in walls)
        near_player = math.hypot(rx - player_pos[0], ry - player_pos[1]) < int(WIDTH * 0.15)
        near_joy = math.hypot(rx - joy_center[0], ry - joy_center[1]) < joy_radius * 1.6
        
        if not in_wall and not near_player and not near_joy:
            notebooks.append(candidate)
            
    # Спавн Кваса
    while True:
        kx = random.randint(thick * 2, WIDTH - thick * 3)
        ky = random.randint(thick * 2, HEIGHT - thick * 3)
        kvass_candidate = pygame.Rect(kx, ky, int(HEIGHT*0.05), int(HEIGHT*0.07))
        if not any(kvass_candidate.colliderect(w) for w in walls) and math.hypot(kx - player_pos[0], ky - player_pos[1]) > 200:
            kvass_rect = kvass_candidate
            break

# Математика
current_num1, current_num2, current_operator, current_ans, user_input = 0, 0, "+", 0, ""
def generate_math(level):
    global current_num1, current_num2, current_operator, current_ans, user_input
    user_input = ""
    if level <= 3:
        current_num1, current_num2 = random.randint(5, 20), random.randint(5, 20)
        current_operator, current_ans = "+", current_num1 + current_num2
    elif level <= 7:
        current_num1, current_num2 = random.randint(20, 70), random.randint(10, 40)
        current_operator, current_ans = "-", current_num1 - current_num2
    else:
        current_num1, current_num2 = random.randint(3, 11), random.randint(3, 11)
        current_operator, current_ans = "*", current_num1 * current_num2

# Виртуальный Нампад
num_buttons = {}
def setup_numpad():
    global num_buttons
    bx, by = int(WIDTH * 0.42), int(HEIGHT * 0.46)
    b_w, b_h = int(WIDTH * 0.055), int(HEIGHT * 0.085)
    gap = int(HEIGHT * 0.018)
    for i in range(9):
        row, col = i // 3, i % 3
        num_buttons[str(i + 1)] = pygame.Rect(bx + col * (b_w + gap), by + row * (b_h + gap), b_w, b_h)
    num_buttons["-"] = pygame.Rect(bx - (b_w + gap), by + 2 * (b_h + gap), b_w, b_h)
    num_buttons["0"] = pygame.Rect(bx + 1 * (b_w + gap), by + 3 * (b_h + gap), b_w, b_h)
    num_buttons["C"] = pygame.Rect(bx, by + 3 * (b_h + gap), b_w, b_h)
    num_buttons["OK"] = pygame.Rect(bx + 2 * (b_w + gap), by + 3 * (b_h + gap), b_w, b_h)

setup_numpad()

# Сетка кнопок уровней
level_buttons = []
def setup_level_select():
    global level_buttons
    level_buttons = []
    start_x = int(WIDTH * 0.18)
    start_y = int(HEIGHT * 0.38)
    b_size = int(HEIGHT * 0.13)
    gap = int(WIDTH * 0.03)
    for i in range(10):
        row, col = i // 5, i % 5
        bx = start_x + col * (b_size + gap)
        by = start_y + row * (b_size + gap)
        level_buttons.append((i + 1, pygame.Rect(bx, by, b_size, b_size)))

setup_level_select()
clock = pygame.time.Clock()

# --- ЦИКЛ ИГРЫ ---
while True:
    clock.tick(60)
    bg_color, wall_color, loc_name = LOCATIONS.get(current_level, (DARK_BG, WALL_COLOR, "Школа"))
    touch_pos = None
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            touch_pos = event.pos
            if game_state == "SPLASH":
                game_state = "MENU"
            elif game_state == "MENU":
                game_state = "LEVEL_SELECT"
            elif game_state in ["LEVEL_CLEAR", "GAME_OVER", "WIN"]:
                game_state = "MENU"
                
            elif game_state == "LEVEL_SELECT":
                for lvl_num, rect in level_buttons:
                    if rect.collidepoint(touch_pos) and lvl_num <= unlocked_level:
                        current_level = lvl_num
                        notebooks_collected = 0
                        generate_level(current_level)
                        game_state = "PLAYING"
                        break
                        
            elif game_state == "PLAYING":
                if math.hypot(touch_pos[0] - joy_center[0], touch_pos[1] - joy_center[1]) <= joy_radius:
                    is_dragging_joy = True
                if has_kvass_item and kvass_button.collidepoint(touch_pos):
                    has_kvass_item = False
                    stun_timer = 600 
                    
            elif game_state == "MATH_SCREEN":
                for btn_txt, rect in num_buttons.items():
                    if rect.collidepoint(touch_pos):
                        if btn_txt == "C": user_input = user_input[:-1]
                        elif btn_txt == "-":
                            if len(user_input) == 0: user_input += "-"
                        elif btn_txt == "OK":
                            try:
                                if int(user_input) == current_ans:
                                    notebooks_collected += 1
                                    game_state = "PLAYING"
                                else:
                                    enemy_pos[0] += (player_pos[0] - enemy_pos[0]) * 0.35
                                    enemy_pos[1] += (player_pos[1] - enemy_pos[1]) * 0.35
                                    game_state = "PLAYING"
                            except: pass
                        else:
                            if len(user_input) < 5: user_input += btn_txt

        if event.type == pygame.MOUSEBUTTONUP:
            is_dragging_joy = False
            stick_pos = list(joy_center)

        if event.type == pygame.MOUSEMOTION and is_dragging_joy:
            touch_pos = event.pos

    # --- УМНЫЙ ИИ И ФИЗИКА ДВИЖЕНИЯ ---
    if game_state == "SPLASH":
        splash_timer += 1
        if splash_timer >= 100: game_state = "MENU"

    elif game_state == "PLAYING":
        if is_dragging_joy and touch_pos:
            dx, dy = touch_pos[0] - joy_center[0], touch_pos[1] - joy_center[1]
            dist = math.hypot(dx, dy)
            if dist > 0:
                limited = min(dist, joy_radius)
                stick_pos = [joy_center[0] + (dx/dist)*limited, joy_center[1] + (dy/dist)*limited]
                
                mx = player_pos[0] + (dx / dist) * player_speed
                my = player_pos[1] + (dy / dist) * player_speed
                
                px_rect = pygame.Rect(mx, player_pos[1], p_size, p_size)
                if not any(px_rect.colliderect(w) for w in walls): player_pos[0] = mx
                py_rect = pygame.Rect(player_pos[0], my, p_size, p_size)
                if not any(py_rect.colliderect(w) for w in walls): player_pos[1] = my

        # ИИ ДАНИЛЫ: Обход углов стен
        if stun_timer > 0:
            stun_timer -= 1
        else:
            edx, edy = player_pos[0] - enemy_pos[0], player_pos[1] - enemy_pos[1]
            edist = math.hypot(edx, edy)
            if edist > 0:
                curr_e_speed = enemy_base_speed + (notebooks_collected * (HEIGHT * 0.00045))
                e_w = int(p_size * 1.2)
                
                step_x = (edx / edist) * curr_e_speed
                step_y = (edy / edist) * curr_e_speed
                
                next_x = enemy_pos[0] + step_x
                next_y = enemy_pos[1] + step_y
                
                rect_x = pygame.Rect(next_x, enemy_pos[1], e_w, e_w)
                rect_y = pygame.Rect(enemy_pos[0], next_y, e_w, e_w)
                
                collide_x = any(rect_x.colliderect(w) for w in walls)
                collide_y = any(rect_y.colliderect(w) for w in walls)
                
                if not collide_x:
                    enemy_pos[0] = next_x
                elif not collide_y:
                    enemy_pos[1] += curr_e_speed if edy > 0 else -curr_e_speed
                    
                if not collide_y:
                    enemy_pos[1] = next_y
                elif not collide_x:
                    enemy_pos[0] += curr_e_speed if edx > 0 else -curr_e_speed

        # Сбор Кваса
        p_rect = pygame.Rect(player_pos[0], player_pos[1], p_size, p_size)
        if kvass_rect and p_rect.colliderect(kvass_rect):
            kvass_rect = None
            has_kvass_item = True

        # Коллизия с Данилой
        e_rect = pygame.Rect(enemy_pos[0], enemy_pos[1], int(p_size*1.2), int(p_size*1.2))
        if p_rect.colliderect(e_rect) and stun_timer <= 0:
            game_state = "GAME_OVER"
            
        # Сбор тетрадей
        for nb in notebooks[:]:
            if p_rect.colliderect(nb):
                notebooks.remove(nb)
                generate_math(current_level)
                game_state = "MATH_SCREEN"
                
        # Триггер финала уровня
        if notebooks_collected >= total_notebooks and p_rect.colliderect(exit_door):
            if current_level == 10:
                prestige_count += 1
                unlocked_level = 1 
                game_state = "WIN"
            else:
                if current_level == unlocked_level:
                    unlocked_level += 1
                game_state = "LEVEL_CLEAR"

    # --- ОТРИСОВКА ИНТЕРФЕЙСА ---
    screen.fill(bg_color)
    
    if game_state == "SPLASH":
        t1 = logo_font.render("MB TEAM", True, MB_GREEN)
        t2 = font.render("P r e s e n t s", True, TEXT_GRAY)
        screen.blit(t1, (WIDTH // 2 - t1.get_width() // 2, HEIGHT // 2 - int(HEIGHT*0.08)))
        screen.blit(t2, (WIDTH // 2 - t2.get_width() // 2, HEIGHT // 2 + int(HEIGHT*0.06)))
        
    elif game_state == "MENU":
        t1 = big_font.render("BOGDIK'S BASICS", True, TEXT_WHITE)
        t2 = font.render(f"Твой Престиж: [ {prestige_count} ]  |  Глобальный ранг: #{max(1, 10 - prestige_count)}", True, MB_GREEN)
        t3 = mid_font.render("Тапни по экрану, чтобы открыть выбор уровня", True, TEXT_GRAY)
        screen.blit(t1, (WIDTH // 2 - t1.get_width() // 2, HEIGHT // 3))
        screen.blit(t2, (WIDTH // 2 - t2.get_width() // 2, HEIGHT // 3 + int(HEIGHT*0.1)))
        screen.blit(t3, (WIDTH // 2 - t3.get_width() // 2, HEIGHT // 2 + int(HEIGHT*0.12)))
        
    elif game_state == "LEVEL_SELECT":
        screen.fill(DARK_BG)
        title = big_font.render("ВЫБОР ЛОКАЦИИ ШКОЛЫ", True, TEXT_WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT * 0.15))
        
        for lvl_num, rect in level_buttons:
            is_unlocked = lvl_num <= unlocked_level
            box_color = PANEL_BG if is_unlocked else (35, 35, 40)
            border_color = MB_GREEN if is_unlocked else TEXT_GRAY
            
            pygame.draw.rect(screen, box_color, rect, border_radius=12)
            pygame.draw.rect(screen, border_color, rect, 3, border_radius=12)
            
            if is_unlocked:
                num_t = mid_font.render(str(lvl_num), True, TEXT_WHITE)
                screen.blit(num_t, (rect.centerx - num_t.get_width()//2, rect.centery - num_t.get_height()//2))
            else:
                lock_t = font.render("🔒", True, ACCENT_RED)
                screen.blit(lock_t, (rect.centerx - lock_t.get_width()//2, rect.centery - lock_t.get_height()//2))
                
        info_p = font.render(f"Текущий ранг Престижа: РАЗРЯД {prestige_count}", True, MB_GREEN)
        screen.blit(info_p, (WIDTH // 2 - info_p.get_width() // 2, HEIGHT * 0.85))

    elif game_state in ["PLAYING", "MATH_SCREEN"]:
        for w in walls: pygame.draw.rect(screen, wall_color, w)
        for nb in notebooks: pygame.draw.rect(screen, YELLOW_NOTE, nb, border_radius=6)
        if notebooks_collected >= total_notebooks: pygame.draw.rect(screen, MB_GREEN, exit_door)
        
        if kvass_rect:
            pygame.draw.rect(screen, ORANGE_KVASS, kvass_rect, border_radius=4)
            kv_lbl = pygame.font.SysFont("Arial", int(HEIGHT*0.03)).render("КВАС", True, TEXT_WHITE)
            screen.blit(kv_lbl, (kvass_rect.x, kvass_rect.y - 20))
            
        screen.blit(player_img, (player_pos[0], player_pos[1]))
        
        # ФИКС: Заменил .inflated() на рабочий метод .inflate()
        if stun_timer > 0:
            pygame.draw.rect(screen, ACCENT_BLUE, e_rect.inflate(6,6), 3, border_radius=4)
            screen.blit(enemy_img, (enemy_pos[0], enemy_pos[1]))
            s_txt = font.render(f"СТАН: {stun_timer//60 + 1}с", True, ACCENT_BLUE)
            screen.blit(s_txt, (enemy_pos[0], enemy_pos[1] - 30))
        else:
            screen.blit(enemy_img, (enemy_pos[0], enemy_pos[1]))
        
        screen.blit(font.render(f"ЛОКАЦИЯ {current_level}: {loc_name}", True, MB_GREEN), (40, 40))
        screen.blit(font.render(f"ТЕТРАДИ: {notebooks_collected}/{total_notebooks}", True, TEXT_WHITE), (40, 40 + int(HEIGHT*0.05)))
        
        if game_state == "PLAYING":
            pygame.draw.circle(screen, PANEL_BG, joy_center, joy_radius)
            pygame.draw.circle(screen, wall_color, joy_center, joy_radius, 3)
            pygame.draw.circle(screen, ACCENT_BLUE, (int(stick_pos[0]), int(stick_pos[1])), stick_radius)
            
            if has_kvass_item:
                pygame.draw.rect(screen, ORANGE_KVASS, kvass_button, border_radius=15)
                pygame.draw.rect(screen, TEXT_WHITE, kvass_button, 3, border_radius=15)
                k_lbl = font.render("КВАС", True, TEXT_WHITE)
                screen.blit(k_lbl, (kvass_button.centerx - k_lbl.get_width()//2, kvass_button.centery - k_lbl.get_height()//2))

        if game_state == "MATH_SCREEN":
            pygame.draw.rect(screen, PANEL_BG, (WIDTH // 5, HEIGHT // 12, int(WIDTH * 0.6), int(HEIGHT * 0.84)), border_radius=15)
            pygame.draw.rect(screen, wall_color, (WIDTH // 5, HEIGHT // 12, int(WIDTH * 0.6), int(HEIGHT * 0.84)), 3, border_radius=15)
            
            t_head = font.render(f"НЕБЕСНАЯ МЕХАНИКА. УРОВЕНЬ {current_level}", True, ACCENT_RED)
            t_math = big_font.render(f"{current_num1} {current_operator} {current_num2} = {user_input}_", True, TEXT_WHITE)
            screen.blit(t_head, (WIDTH // 2 - t_head.get_width() // 2, HEIGHT // 12 + int(HEIGHT*0.03)))
            screen.blit(t_math, (WIDTH // 2 - t_math.get_width() // 2, HEIGHT // 4))
            
            for btn_txt, rect in num_buttons.items():
                b_color = MB_GREEN if btn_txt == "OK" else (ACCENT_RED if btn_txt == "C" else wall_color)
                t_color = DARK_BG if btn_txt in ["OK", "C"] else TEXT_WHITE
                pygame.draw.rect(screen, b_color, rect, border_radius=8)
                b_lbl = font.render(btn_txt, True, t_color)
                screen.blit(b_lbl, (rect.centerx - b_lbl.get_width() // 2, rect.centery - b_lbl.get_height() // 2))

    elif game_state == "LEVEL_CLEAR":
        t1 = big_font.render(f"СЕКТОР {current_level} ЗАЧИЩЕН!", True, MB_GREEN)
        t2 = font.render("Тапни, чтобы разблокировать следующую комнату", True, TEXT_WHITE)
        screen.blit(t1, (WIDTH // 2 - t1.get_width() // 2, HEIGHT // 3))
        screen.blit(t2, (WIDTH // 2 - t2.get_width() // 2, HEIGHT // 2))

    elif game_state == "GAME_OVER":
        t1 = big_font.render("ДУШНИЛА ОДОЛЕЛ ВАС!", True, ACCENT_RED)
        t2 = font.render(f"Вы проиграли на уровне {current_level}. Тапни для меню", True, TEXT_WHITE)
        screen.blit(t1, (WIDTH // 2 - t1.get_width() // 2, HEIGHT // 3))
        screen.blit(t2, (WIDTH // 2 - t2.get_width() // 2, HEIGHT // 2))
        
    elif game_state == "WIN":
        t1 = big_font.render(f"ПРЕСТИЖ ПОВЫШЕН! ТЕПЕРЬ У ВАС: {prestige_count}", True, MB_GREEN)
        t2 = font.render("Вы прошли всю игру! Скорость Данилы выросла. Тапни для нового круга!", True, TEXT_WHITE)
        screen.blit(t1, (WIDTH // 2 - t1.get_width() // 2, HEIGHT // 3))
        screen.blit(t2, (WIDTH // 2 - t2.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()
