import json
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
    top_pipe = pipe_surface.get_rect(midbottom=(SCREEN_WIDTH, random_pipe_pos - 150))
    return bottom_pipe, top_pipe

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

def load_high_scores():
    try:
        with open("high_scores.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []  # Nếu file không tồn tại, trả về danh sách trống

# Hàm lưu điểm cao
def save_high_score(name, score):
    high_scores = load_high_scores()  # Lấy danh sách điểm hiện có
    found = False

    # Cập nhật điểm nếu tên đã có trong danh sách
    for entry in high_scores:
        if entry["name"] == name:
            entry["score"] = max(entry["score"], int(score))  # Giữ điểm cao nhất
            found = True
            break

    # Nếu tên chưa có, thêm mới vào danh sách
    if not found:
        high_scores.append({"name": name, "score": int(score)})

    # Sắp xếp danh sách theo điểm số giảm dần
    high_scores = sorted(high_scores, key=lambda x: x["score"], reverse=True)

    # Giữ lại tối đa 5 người chơi có điểm cao nhất
    with open("high_scores.json", "w") as file:
        json.dump(high_scores[:5], file, indent=4)


def draw_high_scores():
    high_scores = load_high_scores()  # Cập nhật danh sách điểm ngay lập tức
    y_offset = 20  # Hiển thị ở góc trái trên cùng màn hình
    for i, entry in enumerate(high_scores):
        text_surface = font.render(f"{i+1}. {entry['name']}: {entry['score']}", True, (255, 255, 255))
        screen.blit(text_surface, (20, y_offset))  # Căn trái trên cùng
        y_offset += 40


def reset_game():
    global bird_movement, pipe_list, score, game_active, waiting_to_start
    pipe_list.clear()
    bird_rect.center = (100, 350)
    bird_movement = 0
    score = 0
    game_active = True
    waiting_to_start = False

def draw_combobox():
    """Vẽ combobox chọn mức độ"""
    font = pygame.font.Font(None, 36)

    # Hiển thị chữ "Mức độ:"
    text_surface = font.render("Level:", True, (255, 255, 255))
    screen.blit(text_surface, (dropdown_rect.x - 100, dropdown_rect.y + 10))  

    # Vẽ ô combobox
    pygame.draw.rect(screen, (100, 100, 100), dropdown_rect)  
    selected_text = font.render(selected_difficulty, True, (255, 255, 255))
    screen.blit(selected_text, (dropdown_rect.x + 10, dropdown_rect.y + 10))

    # Nếu combobox mở, hiển thị danh sách lựa chọn
    if dropdown_open:
        for i, level in enumerate(difficulty_levels):
            pygame.draw.rect(screen, (50, 50, 50), dropdown_items[i])  
            option_text = font.render(level, True, (255, 255, 255))
            screen.blit(option_text, (dropdown_items[i].x + 10, dropdown_items[i].y + 10))

def handle_combobox_click(pos):
    """Xử lý bấm vào combobox"""
    global dropdown_open, selected_difficulty

    if dropdown_rect.collidepoint(pos):
        dropdown_open = not dropdown_open  
    elif dropdown_open:
        for i, rect in enumerate(dropdown_items):
            if rect.collidepoint(pos):
                selected_difficulty = difficulty_levels[i]
                dropdown_open = False
                update_game_difficulty(selected_difficulty)  
def update_game_difficulty(level):
    """Cập nhật tốc độ game theo mức độ"""
    global pipe_speed, gravity
    if level == "Easy":
        pipe_speed = 3
        gravity = 0.25
    elif level == "Medium":
        pipe_speed = 5
        gravity = 0.25
    elif level == "Hard":
        pipe_speed = 7
        gravity = 0.25

def move_pipe(pipes):
    for pipe in pipes:
        pipe.centerx -= pipe_speed  # Sử dụng biến pipe_speed
    return pipes






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

# Lấy 5 người có điểm cao nhất từ file JSON
high_scores = []
try:
    with open("high_scores.json", "r") as file:
        scores = json.load(file)
        high_scores = sorted(scores, key=lambda x: x["score"], reverse=True)[:5]
except (FileNotFoundError, json.JSONDecodeError):
    print("Không tìm thấy hoặc không thể đọc file điểm cao!")

# Font hiển thị điểm
font = pygame.font.Font(None, 36)

# Mức độ mặc định là Medium
difficulty_levels = ["Easy", "Medium", "Hard"]
selected_difficulty = "Medium"  
dropdown_open = False

# Vị trí combobox
dropdown_rect = pygame.Rect(SCREEN_WIDTH - 180, 20, 150, 40)  
dropdown_items = [pygame.Rect(SCREEN_WIDTH - 180, 60 + i * 40, 150, 40) for i in range(len(difficulty_levels))]
# Đặt mức độ mặc định
update_game_difficulty(selected_difficulty)

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


        elif event.type == pygame.MOUSEBUTTONDOWN:
            handle_combobox_click(event.pos)  

        # Chờ bấm SPACE để bắt đầu
        elif waiting_to_start:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
               reset_game()

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
         draw_combobox()
         draw_high_scores()
         

    # Game đang chạy
    elif game_active:
        bird_movement += gravity
        bird_rect.centery += bird_movement
        screen.blit(bird, bird_rect)

        # Kiểm tra va chạm
        game_active = check_collision(pipe_list)
        if bird_rect.top <= -50 or bird_rect.bottom >= 550:
            game_active = False
            save_high_score(player_name, score)
            waiting_to_start = True  # Sau khi thua, quay lại màn hình chờ SPACE

        # Xử lý ống nước
        pipe_list = move_pipe(pipe_list)
        draw_pipe(pipe_list)

        for pipe in pipe_list:
            if pipe.centerx == bird_rect.centerx:  # Khi chim đi qua tâm của ống nước
                score += 1
                score_sound.play()  # Phát âm thanh điểm

        score_display('main game')



    # Khi thua
    else:
        high_score = update_score(score, high_score)
        save_high_score(player_name, score)
        screen.blit(game_over_surface, game_over_rect)
        score_display('game_over')
        waiting_to_start = True  # Sau khi thua, quay lại màn hình chờ SPACE
        draw_high_scores()
    #sàn
    floor_x_pos -= 1
    draw_floor()
    if floor_x_pos <= -432:
        floor_x_pos =0
    pygame.display.update()
    clock.tick(80)