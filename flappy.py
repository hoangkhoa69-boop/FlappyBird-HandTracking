import pygame, random, time, sys
from pygame.locals import *
from hand_tracker import HandTracker 

# --- THÔNG SỐ (Giữ nguyên từ code gốc của bạn) ---
SCREEN_WIDHT = 400
SCREEN_HEIGHT = 600
SPEED = 20
GRAVITY = 2.5
GAME_SPEED = 15
GROUND_WIDHT = 2 * SCREEN_WIDHT
GROUND_HEIGHT = 100
PIPE_WIDHT = 80
PIPE_GAP = 150

# --- KHỞI TẠO ĐỐI TƯỢNG ---
class Bird(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.images = [
            pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha(),
            pygame.image.load('assets/sprites/bluebird-midflap.png').convert_alpha(),
            pygame.image.load('assets/sprites/bluebird-downflap.png').convert_alpha()
        ]
        self.reset()

    def reset(self):
        self.speed = SPEED
        self.current_image = 0
        self.image = self.images[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect[0] = SCREEN_WIDHT / 6
        self.rect[1] = SCREEN_HEIGHT / 2

    def update(self):
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]
        self.speed += GRAVITY
        self.rect[1] += self.speed

    def bump(self):
        self.speed = -SPEED

class Pipe(pygame.sprite.Sprite):
    def __init__(self, inverted, xpos, ysize):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/sprites/pipe-green.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (PIPE_WIDHT, 500))
        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect[1] = - (self.rect[3] - ysize)
        else:
            self.rect[1] = SCREEN_HEIGHT - ysize
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect[0] -= GAME_SPEED

class Ground(pygame.sprite.Sprite):
    def __init__(self, xpos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/sprites/base.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (GROUND_WIDHT, GROUND_HEIGHT))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        self.rect[1] = SCREEN_HEIGHT - GROUND_HEIGHT
    def update(self):
        self.rect[0] -= GAME_SPEED

def get_random_pipes(xpos):
    size = random.randint(100, 300)
    return Pipe(False, xpos, size), Pipe(True, xpos, SCREEN_HEIGHT - size - PIPE_GAP)

# --- HÀM CHÍNH ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDHT, SCREEN_HEIGHT))
    pygame.display.set_caption('Flappy Bird Hand Control')
    
    BACKGROUND = pygame.image.load('assets/sprites/background-day.png')
    BACKGROUND = pygame.transform.scale(BACKGROUND, (SCREEN_WIDHT, SCREEN_HEIGHT))
    BEGIN_IMAGE = pygame.image.load('assets/sprites/message.png').convert_alpha()

    bird = Bird()
    bird_group = pygame.sprite.Group(bird)
    ground_group = pygame.sprite.Group()
    pipe_group = pygame.sprite.Group()
    
    tracker = HandTracker()
    clock = pygame.time.Clock()

    def reset_game():
        bird.reset()
        ground_group.empty()
        pipe_group.empty()
        for i in range(2): ground_group.add(Ground(GROUND_WIDHT * i))
        for i in range(2):
            p1, p2 = get_random_pipes(SCREEN_WIDHT * i + 800)
            pipe_group.add(p1, p2)

    reset_game()
    game_active = False # Ban đầu ở màn hình chờ
    
    while True:
        clock.tick(30)
        
        # 1. Xử lý sự kiện hệ thống
        for event in pygame.event.get():
            if event.type == QUIT:
                tracker.close()
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    if not game_active:
                        reset_game()
                        game_active = True
                    bird.bump()

        # 2. Xử lý nhận diện tay
        hand_jump = tracker.check_jump()
        if hand_jump:
            if not game_active:
                reset_game()
                game_active = True # Hất tay để chơi lại khi đang ở màn hình Game Over
            bird.bump()

        # 3. Logic Game
        screen.blit(BACKGROUND, (0, 0))
        
        if game_active:
            bird_group.update()
            pipe_group.update()
            ground_group.update()

            # Kiểm tra ống ra khỏi màn hình
            if pipe_group.sprites()[0].rect[0] < -80:
                pipe_group.remove(pipe_group.sprites()[0], pipe_group.sprites()[1])
                p1, p2 = get_random_pipes(SCREEN_WIDHT * 2)
                pipe_group.add(p1, p2)
            
            # Kiểm tra va chạm
            if (pygame.sprite.groupcollide(bird_group, ground_group, False, False, pygame.sprite.collide_mask) or
                pygame.sprite.groupcollide(bird_group, pipe_group, False, False, pygame.sprite.collide_mask)):
                game_active = False # Chuyển sang trạng thái thua, không tắt màn hình
        
        # 4. Vẽ lên màn hình
        pipe_group.draw(screen)
        ground_group.draw(screen)
        bird_group.draw(screen)

        if not game_active:
            # Hiện ảnh thông báo khi chưa bắt đầu hoặc đã thua
            screen.blit(BEGIN_IMAGE, (SCREEN_WIDHT//2 - BEGIN_IMAGE.get_width()//2, 100))

        pygame.display.update()

if __name__ == "__main__":
    main()