import pygame, sys, random, json, os

# Thiết lập kích thước màn hình
SCREEN_WIDTH = 432
SCREEN_HEIGHT = 700
# tọa độ 0,0 là góc trên bên trái màn hình
# Tạo hàm cho trò chơi
def draw_floor():
    screen.blit(floor, (floor_x_pos, 550)) #sàn nằm ở tọa độ cách viền trên 550px,sàn dài 150px
    screen.blit(floor, (floor_x_pos + SCREEN_WIDTH, 550))

def create_pipe():
    random_pipe_pos = random.choice(pipe_height)
    pipe_gap = 200  # khoảng cách giữa ống trên và ống dưới

    bottom_pipe = {
        'rect': pipe_surface.get_rect(midtop=(SCREEN_WIDTH + 100, random_pipe_pos)),
        'scored': False, # xác định ống chưa được tính điểm, sau khi tính điểm thành true
        'type': 'bottom' # xác định ống trên ống dưới
    }
    top_pipe = {
        'rect': pipe_surface.get_rect(midbottom=(SCREEN_WIDTH + 100, random_pipe_pos - pipe_gap)),
        'scored': False,  # THÊM dòng này để tránh KeyError
        'type': 'top'
    }

    #pipe là 1 dictionary lưu các thông tin
    return [bottom_pipe, top_pipe]



def move_pipe(pipes):
    for pipe in pipes:
        pipe['rect'].centerx -= pipe_speed
    return pipes


def draw_pipe(pipes):
    for pipe in pipes:
        if pipe['rect'].top > 0:
            screen.blit(pipe_surface, pipe['rect'])  # Ống dưới
        else:
            flip_pipe = pygame.transform.flip(pipe_surface, False, True)  # Ống trên
            screen.blit(flip_pipe, pipe['rect'])

#bird-rect: đại diện cho vị trí kích thước của chim
#pipe là đối tượng rect đại diện cho vị trí kích thước của ống
def check_collision(pipes):
    for pipe in pipes:
        if bird_rect.colliderect(pipe['rect']):
            hit_sound.play()
            return False
    if bird_rect.top <= -100 or bird_rect.bottom >= 550:
        return False
    return True


def rotate_bird(bird1):
    return pygame.transform.rotozoom(bird1, -bird_movement * 3, 1) # hình ảnh, góc xoay, tỷ lệ hỉnh ảnh ( giữ nguyên)
   # nếu bird_movenment có giá trị dương thì tạo ra gốc âm xoay ngược hướng kim dđồng hồ tạo cảm giác đi lên và ngược lại

def bird_animation():
    new_bird = bird_list[bird_index] #danh sách hình ảnh khác nhau của chim
    new_bird_rect = new_bird.get_rect(center=(100, bird_rect.centery)) #chim giữ nguyên vị trí khi đổi hình ảnh, tránh bị "nhấp nháy" lên xuống do sự khác nhau giữa các hình ảnh.
    return new_bird, new_bird_rect
#giữ nguyên vị trí của chim x:100, y là vị trí hiện tại 

def score_display(game_state): # truyền vào trạng thái game
    if game_state == 'main game':
        score_surface = game_font.render(str(int(score)), True, (255, 255, 255))# dùng font để vẽ điểm thành 1 hình ảnh văn bản surface , true: mịn chữ, màu trắng
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, 100)) #tạo rect cho ảnh điểm đặt giữa màn hình theo chiều ngang
        screen.blit(score_surface, score_rect) # vẽ ảnh điểm số lên màmanfinhf theo vị trí vừa tạo
        
        #hiển thị tốc độ ống
        speed_surface = game_font_small.render(f'Speed: {pipe_speed}', True, (255, 255, 255)) # hiển thị tốc độ hiện tại
        speed_rect = speed_surface.get_rect(center=(SCREEN_WIDTH // 2, 50)) # tạo rect định vị trí cho ảnh tốc độ
        screen.blit(speed_surface, speed_rect)
        
    if game_state == 'game_over':
        # Hiển thị điểm vừa mới chơi được
        score_surface = game_font.render(f'Score: {int(score)}', True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(score_surface, score_rect)

        #hiển thị điểm cao nhất
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
    base_speed = 5
    increase = int(current_score) // 5  # Mỗi 10 điểm tăng thêm 1 đơn vị tốc độ
    return base_speed + increase


def get_player_name():
    name = ""
    input_active = True
    
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # kiểm tra bấm dấu x thoát game
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name: # nhân phím enter kết thúc nhập tên
                    input_active = False
                elif event.key == pygame.K_BACKSPACE: # xóa tên nhập lại
                    name = name[:-1]
                else:
                    if len(name) < 10 and event.unicode.isalnum(): # tên không quá 10 kí tự, không có kí tự đặc biệt
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
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512) # khởi tạo âm thành 
pygame.init() # khởi tạo các mô đun của pygame trước khi dùng bất kì tính năng nào
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock() # giúp các vòng lặp chạy ổn định theo thời gian
game_font = pygame.font.Font('04B_19.ttf', 35)
game_font_small = pygame.font.Font('04B_19.ttf', 20)

# Tạo các biến cho trò chơi
show_top_players = True  # Thêm dòng này cùng với các biến khác như gravity, bird_movement...
gravity = 0.25 # trọng lực làm chim rơi ( tốc độ rơi của chim) càng lớn chim rơi càng nhanh
bird_movement = 0 # tốc độ rơi ban đầu của chim
game_active = False # trạng thái chơi game
score = 0
high_score = 0
pipe_speed = 5 # tốc độ di chuyển của ống
top_players = load_high_scores()
player_name = ""

# Chèn background
bg = pygame.image.load('assets/background-night.png').convert()
bg = pygame.transform.scale2x(bg)

# Chèn sàn
floor = pygame.image.load('assets/floor.png').convert()
floor = pygame.transform.scale2x(floor)
floor_x_pos = 0

# Tạo chim, tạo hiệu ứng cánh chim bay
bird_down = pygame.transform.scale2x(pygame.image.load('assets/yellowbird-downflap.png').convert_alpha())
bird_mid = pygame.transform.scale2x(pygame.image.load('assets/yellowbird-midflap.png').convert_alpha())
bird_up = pygame.transform.scale2x(pygame.image.load('assets/yellowbird-upflap.png').convert_alpha())
bird_list = [bird_down, bird_mid, bird_up]
bird_index = 0
bird = bird_list[bird_index]
bird_rect = bird.get_rect(center=(100, 350)) # vị trí xuất phát cho chim

# Tạo timer cho bird
birdflap = pygame.USEREVENT + 1
pygame.time.set_timer(birdflap, 200) # cứ 0.2 giây đổi ảnh chim tạo trạng thái bay

# Tạo ống
pipe_surface = pygame.image.load('assets/pipe-green.png').convert()
pipe_surface = pygame.transform.scale2x(pipe_surface)
pipe_list = [] #chứa các ống mới tạo ra
pipe_height = [250, 300, 350]

# Tạo timer
spawnpipe = pygame.USEREVENT
pygame.time.set_timer(spawnpipe, 1200) # cứ 1,2 giây tạo ống

# Tạo màn hình kết thúc
game_over_surface = pygame.transform.scale2x(pygame.image.load('assets/message.png').convert_alpha())
game_over_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH // 2, 350))

# Chèn âm thanh
flap_sound = pygame.mixer.Sound('sound/5_Flappy_Bird_sound_sfx_wing.wav') # khi chim bay lên
hit_sound = pygame.mixer.Sound('sound/5_Flappy_Bird_sound_sfx_hit.wav') # khi chim va vào vật cản
score_sound = pygame.mixer.Sound('sound/5_Flappy_Bird_sound_sfx_point.wav') # khi chim ghi điểm
score_sound_countdown = 100

# Lấy tên người chơi khi bắt đầu game
if not player_name:
    player_name = get_player_name()

# Vòng lặp trò chơi
while True:
    for event in pygame.event.get(): #lấy tất cả sự kiện game
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_t:  # Nhấn phim T để tắt bật top 5 người chơi cao điểm nhất
                show_top_players = not show_top_players
            if event.key == pygame.K_SPACE: # Nhân phím space
                if game_active: # Nếu đang chơi thì cho chim bay lên , phát tiến vỗ cánh
                    bird_movement = 0 # vận tốc chim đưa về 0 rồi thêm -6, không bị dồn vận tốc cũ không bay yếu hơn
                    bird_movement = -6
                    flap_sound.play()
                else:
                    game_active = True # Nếu chưa chơi thì bật trạng thái chới
                    pipe_list.clear()
                    bird_rect.center = (100, 350) # Đặt lại vị trí chim
                    bird_movement = 0
                    score = 0
                    pipe_speed = 5  # Reset tốc độ khi bắt đầu game mới
        
        if event.type == spawnpipe and game_active: # khi sự kiện spawpipe dc gọi thì 1,2 giây tạo ống mới
            pipe_list.extend(create_pipe())
        
        if event.type == birdflap and game_active:
            bird_index = (bird_index + 1) % 3 # vì có 3 ảnh nên chia ra kết quả là 0,1,2 tương ứng vị trí ảnh trong list
            bird, bird_rect = bird_animation()
    
    screen.blit(bg, (0, 0)) # vẽ ảnh background lên toàn bộ màn hình
    
    if game_active:
        # Chim
        bird_movement += gravity # trọng lực kéo chim xuống
        rotated_bird = rotate_bird(bird) # quay ảnh chim theo hướng rơi xuống
        bird_rect.centery += bird_movement # cập nhật lại vị trí
        screen.blit(rotated_bird, bird_rect) # vẽ chim lên màn hình 
        game_active = check_collision(pipe_list) # kết thúc game nếu có va chạm
        
        # Ống
        pipe_list = move_pipe(pipe_list)
        draw_pipe(pipe_list)
        for pipe in pipe_list:
            # Chỉ xử lý ống dưới (có 'type' là 'bottom')
            if pipe['rect'].centerx < bird_rect.centerx and not pipe['scored'] and pipe.get('type') == 'bottom':
                score += 1
                pipe['scored'] = True
                score_sound.play()



        
        # Hiển thị điểm
        score_display('main game')
        
        # Điều chỉnh độ khó
        pipe_speed = adjust_difficulty(score) # cứ sau 10 điểm tốc độ tăng 
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