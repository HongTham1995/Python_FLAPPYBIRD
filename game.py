import pygame, sys, random

# Thiết lập kích thước màn hình mới
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 700

# Tạo hàm cho trò chơi
def draw_floor():
    screen.blit(floor, (floor_x_pos, 550))
    screen.blit(floor, (floor_x_pos + SCREEN_WIDTH, 550))

def create_pipe():
    random_pipe_pos = random.choice(pipe_height)
    bottom_pipe = pipe_surface.get_rect(midtop=(SCREEN_WIDTH, random_pipe_pos))
    top_pipe = pipe_surface.get_rect(midbottom=(SCREEN_WIDTH, random_pipe_pos - 200))
    return bottom_pipe, top_pipe

def move_pipe(pipes):
    for pipe in pipes:
        pipe.centerx -= 5
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
    if game_state == 'game_over':
        score_surface = game_font.render(f'Score: {int(score)}', True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(score_surface, score_rect)

        high_score_surface = game_font.render(f'High Score: {int(high_score)}', True, (255, 255, 255))
        high_score_rect = high_score_surface.get_rect(center=(SCREEN_WIDTH // 2, 630))
        screen.blit(high_score_surface, high_score_rect)

def update_score(score, high_score):
    return max(score, high_score)

# Tạo hàm nhập tên người chơi
def draw_text_input():
    text_surface = game_font.render(player_name, True, (255, 255, 255))
    screen.blit(input_box, input_box_rect)
    screen.blit(text_surface, (input_box_rect.x + 10, input_box_rect.y + 5))

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
game_font = pygame.font.Font('04B_19.ttf', 35)

# Tạo các biến cho trò chơi
gravity = 0.25
bird_movement = 0
score = 0
high_score = 0


# Biến trạng thái trò chơi
game_active = False
waiting_to_start = False  # Biến mới: Đợi bấm SPACE để bắt đầu game
player_name = ""
input_active = True

# Tạo ô nhập tên
input_box = pygame.Surface((300, 50))
input_box.fill((50, 50, 50))
input_box_rect = input_box.get_rect(center=(SCREEN_WIDTH // 2, 350))

# Chèn background
bg = pygame.image.load('assets/background-night.png').convert()
bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Chèn sàn
floor = pygame.image.load('assets/floor.png').convert()
floor = pygame.transform.scale(floor, (SCREEN_WIDTH, 150))
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
pipe_surface = pygame.transform.scale(pipe_surface, (70, 400))
pipe_list = []
pipe_height = [300, 350, 400, 450]

# Tạo timer
spawnpipe = pygame.USEREVENT
pygame.time.set_timer(spawnpipe, 1200)

# Tạo màn hình kết thúc
game_over_surface = pygame.image.load('assets/message.png').convert_alpha()
game_over_surface = pygame.transform.scale(game_over_surface, (300, 400))
game_over_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH // 2, 350))

# Chèn âm thanh
flap_sound = pygame.mixer.Sound('sound/5_Flappy_Bird_sound_sfx_wing.wav')
hit_sound = pygame.mixer.Sound('sound/5_Flappy_Bird_sound_sfx_hit.wav')
score_sound = pygame.mixer.Sound('sound/5_Flappy_Bird_sound_sfx_point.wav')
score_sound_countdown = 100

# Vòng lặp trò chơi
while True:
    screen.blit(bg, (0, 0))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # Nhập tên người chơi
        if input_active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and player_name:
                    input_active = False
                    waiting_to_start = True  # Chuyển sang trạng thái chờ bấm SPACE
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    if len(player_name) < 10:
                        player_name += event.unicode

        # Chờ bấm SPACE để bắt đầu
        elif waiting_to_start:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting_to_start = False
                game_active = True
                pipe_list.clear()
                bird_rect.center = (100, 350)
                bird_movement = 0
                score = 0

        # Game đang chạy
        elif game_active:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bird_movement = -6  
                flap_sound.play()

            if event.type == spawnpipe:
                pipe_list.extend(create_pipe())

            if event.type == birdflap:
                bird_index = (bird_index + 1) % 3
                bird = bird_list[bird_index]
                bird_rect = bird.get_rect(center=(bird_rect.centerx, bird_rect.centery))  

    # Giao diện nhập tên
    if input_active:
        text_surface = game_font.render(player_name, True, (255, 255, 255))
        screen.blit(input_box, input_box_rect)
        screen.blit(text_surface, (input_box_rect.x + 10, input_box_rect.y + 5))

    # Hiển thị "Nhấn SPACE để bắt đầu"
    elif waiting_to_start:
         screen.blit(game_over_surface,game_over_rect) 

    # Game đang chạy
    elif game_active:
        bird_movement += gravity
        bird_rect.centery += bird_movement
        screen.blit(bird, bird_rect)

        # Kiểm tra va chạm
        game_active = check_collision(pipe_list)
        if bird_rect.top <= -50 or bird_rect.bottom >= 550:
            game_active = False
            waiting_to_start = True  # Sau khi thua, quay lại màn hình chờ SPACE

        # Xử lý ống nước
        pipe_list = move_pipe(pipe_list)
        draw_pipe(pipe_list)

        # Hiển thị điểm
        score += 0.01
        score_display('main game')

    # Khi thua
    else:
        screen.blit(game_over_surface, game_over_rect)
        high_score = update_score(score, high_score)
        score_display('game_over')
        waiting_to_start = True  # Sau khi thua, quay lại màn hình chờ SPACE

    pygame.display.update()
    clock.tick(80)