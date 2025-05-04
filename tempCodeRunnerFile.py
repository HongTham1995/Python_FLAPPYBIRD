import pygame, sys, random, json, os

# Thiết lập kích thước màn hình
SCREEN_WIDTH = 432
SCREEN_HEIGHT = 700

# Tạo hàm cho trò chơi
def draw_floor():
    screen.blit(floor, (floor_x_pos, 550))
    screen.blit(floor, (floor_x_pos + SCREEN_WIDTH, 550))

def create_pipe():
    random_pipe_pos = random.choice(pipe_height)
    bottom_pipe = pipe_surface.get_rect(midtop=(500, random_pipe_pos))
    top_pipe = pipe_surface.get_rect(midtop=(500, random_pipe_pos - 700))
    return bottom_pipe, top_pipe

def move_pipe(pipes):
    for pipe in pipes:
        pipe.centerx -= pipe_speed
    return pipes

def draw_pipe(pipes):
    for pipe in pipes:
        if pipe.bottom >= SCREEN_HEIGHT:
            screen.blit(pipe_surface, pipe)
        else:
            flip_pipe = pygame.transform.flip(pipe_surface, False, True)
            screen.blit(flip_pipe, pipe)

def check_collision(pipes):
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            hit_sound.play()
            return False
    if bird_rect.top <= -100 or bird_rect.bottom >= 550:
        return False
    return True

def rotate_bird(bird1):
    return pygame.transform.rotozoom(bird1, -bird_movement * 3, 1)

def bird_animation():
    new_bird = bird_list[bird_index]
    new_bird_rect = new_bird.get_rect(center=(100, bird_rect.centery))
    return new_bird, new_bird_rect

def score_display(game_state):
    if game_state == 'main game':
        score_surface = game_font.render(str(int(score)), True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(score_surface, score_rect)
        
        speed_surface = game_font_small.render(f'Speed: {pipe_speed}', True, (255, 255, 255))
        speed_rect = speed_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(speed_surface, speed_rect)
        
    if game_state == 'game_over':
        score_surface = game_font.render(f'Score: {int(score)}', True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(score_surface, score_rect)

        high_score_surface = game_font.render(f'High Score: {int(high_score)}', True, (255, 255, 255))
        high_score_rect = high_score_surface.get_rect(center=(SCREEN_WIDTH // 2, 630))
        screen.blit(high_score_surface, high_score_rect)
        
        if show_top_players:  # Chỉ hiển thị khi biến = True
            # Tạo nền mờ
            top5_bg = pygame.Surface((300, 200))
            top5_bg.set_alpha(180)  # Độ mờ
            top5_bg.fill((0, 0, 0))  # Màu đen
            screen.blit(top5_bg, (SCREEN_WIDTH//2 - 150, 150))
            
            # Tiêu đề
            title = game_font_small.render("TOP 5 (Press T)", True, (255, 215, 0))  # Màu vàng
            screen.blit(title, (SCREEN_WIDTH//2 - 70, 160))
            
            # Hiển thị từng người chơi
            for i, player in enumerate(top_players[:5]):
                # Nền mỗi dòng
                player_bg = pygame.Surface((280, 28))
                player_bg.set_alpha(150)
                player_bg.fill((50, 50, 50))
                screen.blit(player_bg, (SCREEN_WIDTH//2 - 140, 190 + i*32))
                
                # Text
                player_text = game_font_small.render(
                    f"{i+1}. {player['name'][:10]}: {player['score']}", 
                    True, (255, 255, 255))
                screen.blit(player_text, (SCREEN_WIDTH//2 - 130, 195 + i*32))

def update_score(score, high_score):
    return max(score, high_score)

def load_high_scores():
    try:
        with open("high_scores.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_high_score(name, score):
    high_scores = load_high_scores()
    score = int(score)
    
    # Kiểm tra nếu tên đã tồn tại
    existing_player = None
    for player in high_scores:
        if player['name'] == name:
            existing_player = player
            break
    
    if existing_player:
        # Nếu đã có thì cập nhật điểm nếu điểm mới cao hơn
        if score > existing_player['score']:
            existing_player['score'] = score
    else:
        # Nếu chưa có thì thêm mới
        high_scores.append({'name': name, 'score': score})
    
    # Sắp xếp lại danh sách
    high_scores.sort(key=lambda x: x['score'], reverse=True)
    
    # Giữ lại top 5
    with open("high_scores.json", "w") as file:
        json.dump(high_scores[:5], file, indent=4)

def adjust_difficulty(current_score):
    # Tăng tốc độ ống sau mỗi 10 điểm
    if current_score >= 10 and current_score < 20:
        return 6
    elif current_score >= 20 and current_score < 30:
        return 7
    elif current_score >= 30 and current_score < 40:
        return 8
    elif current_score >= 40:
        return 9
    return 5

def get_player_name():
    name = ""
    input_active = True
    
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 10 and event.unicode.isalnum():
                        name += event.unicode
        
        # Vẽ màn hình nhập tên
        screen.blit(bg, (0, 0))
        prompt_surface = game_font.render("Enter your name:", True, (255, 255, 255))
        prompt_rect = prompt_surface.get_rect(center=(SCREEN_WIDTH // 2, 300))
        screen.blit(prompt_surface, prompt_rect)
        
        name_surface = game_font.render(name, True, (255, 255, 255))
        name_rect = name_surface.get_rect(center=(SCREEN_WIDTH // 2, 350))
        pygame.draw.rect(screen, (100, 100, 100), (name_rect.x - 10, name_rect.y - 10, name_rect.width + 20, name_rect.height + 20))
        screen.blit(name_surface, name_rect)
        
        pygame.display.update()
        clock.tick(60)
    
    return name if name else "Player"

# Khởi tạo pygame
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
game_font = pygame.font.Font('04B_19.ttf', 35)
game_font_small = pygame.font.Font('04B_19.ttf', 20)

# Tạo các biến cho trò chơi
show_top_players = True  # Thêm dòng này cùng với các biến khác như gravity, bird_movement...
gravity = 0.25
bird_movement = 0
game_active = False
score = 0
high_score = 0
pipe_speed = 5
top_players = load_high_scores()
player_name = ""

# Chèn background
bg = pygame.image.load('assets/background-night.png').convert()
bg = pygame.transform.scale2x(bg)

# Chèn sàn
floor = pygame.image.load('assets/floor.png').convert()
floor = pygame.transform.scale2x(floor)
floor_x_pos = 0

# Tạo chim
bird_down = pygame.transform.scale2x(pygame.image.load('assets/yellowbird-downflap.png').convert_alpha())
bird_mid = pygame.transform.scale2x(pygame.image.load('assets/yellowbird-midflap.png').convert_alpha())
bird_up = pygame.transform.scale2x(pygame.image.load('assets/yellowbird-upflap.png').convert_alpha())
bird_list = [bird_down, bird_mid, bird_up]
bird_index = 0
bird = bird_list[bird_index]
bird_rect = bird.get_rect(center=(100, 350))

# Tạo timer cho bird
birdflap = pygame.USEREVENT + 1
pygame.time.set_timer(birdflap, 200)

# Tạo ống
pipe_surface = pygame.image.load('assets/pipe-green.png').convert()
pipe_surface = pygame.transform.scale2x(pipe_surface)
pipe_list = []
pipe_height = [250, 300, 350]

# Tạo timer
spawnpipe = pygame.USEREVENT
pygame.time.set_timer(spawnpipe, 1200)

# Tạo màn hình kết thúc
game_over_surface = pygame.transform.scale2x(pygame.image.load('assets/message.png').convert_alpha())
game_over_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH // 2, 350))

# Chèn âm thanh
flap_sound = pygame.mixer.Sound('sound/5_Flappy_Bird_sound_sfx_wing.wav')
hit_sound = pygame.mixer.Sound('sound/5_Flappy_Bird_sound_sfx_hit.wav')
score_sound = pygame.mixer.Sound('sound/5_Flappy_Bird_sound_sfx_point.wav')
score_sound_countdown = 100

# Lấy tên người chơi khi bắt đầu game
if not player_name:
    player_name = get_player_name()

# Vòng lặp trò chơi
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_t:  # Thêm đoạn này
                show_top_players = not show_top_players
            if event.key == pygame.K_SPACE:
                if game_active:
                    bird_movement = 0
                    bird_movement = -6
                    flap_sound.play()
                else:
                    game_active = True
                    pipe_list.clear()
                    bird_rect.center = (100, 350)
                    bird_movement = 0
                    score = 0
                    pipe_speed = 5  # Reset tốc độ khi bắt đầu game mới
        
        if event.type == spawnpipe and game_active:
            pipe_list.extend(create_pipe())
        
        if event.type == birdflap and game_active:
            bird_index = (bird_index + 1) % 3
            bird, bird_rect = bird_animation()
    
    screen.blit(bg, (0, 0))
    
    if game_active:
        # Chim
        bird_movement += gravity
        rotated_bird = rotate_bird(bird)
        bird_rect.centery += bird_movement
        screen.blit(rotated_bird, bird_rect)
        game_active = check_collision(pipe_list)
        
        # Ống
        pipe_list = move_pipe(pipe_list)
        draw_pipe(pipe_list)
        score += 0.01
        
        # Hiển thị điểm
        score_display('main game')
        
        # Phát âm thanh khi ghi điểm
        score_sound_countdown -= 1
        if score_sound_countdown <= 0:
            score_sound.play()
            score_sound_countdown = 100
        
        # Điều chỉnh độ khó
        pipe_speed = adjust_difficulty(score)
    else:
        # Màn hình kết thúc
        screen.blit(game_over_surface, game_over_rect)
        high_score = update_score(score, high_score)
        score_display('game_over')
        
        # Lưu điểm nếu đủ cao
        if score > 0 and (len(top_players) < 5 or score > top_players[-1]['score']):
            save_high_score(player_name, score)
            top_players = load_high_scores()  # Cập nhật danh sách top players
    
    # Sàn
    floor_x_pos -= 1
    draw_floor()
    if floor_x_pos <= -SCREEN_WIDTH:
        floor_x_pos = 0
    
    pygame.display.update()
    clock.tick(80)