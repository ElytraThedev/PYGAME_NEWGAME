import pygame
import sys
import random

pygame.init()
screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
width, height = screen.get_size()
pygame.display.set_caption("Isobilateral")
clock = pygame.time.Clock()

icon = pygame.image.load("douglas1.ico")
pygame.display.set_icon(icon)

bg = pygame.image.load("wp4469123.png").convert()
bg_width = bg.get_width()

player_img = pygame.image.load("8VNo8G.png").convert_alpha()

velocity_y = 0
gravity = 0.5
speed = 5
jump_strength = -18
jumps_left = 2
angle = 0
spinning = False
spin_speed = 10
camera_x = 0
obstacles = []
game_over = False

font_big = pygame.font.SysFont(None, 100)
font_small = pygame.font.SysFont(None, 40)
font_tiny = pygame.font.SysFont(None, 24)

score = 0
max_player_x = 100
obstacles_passed = 0
orb_active = False
orb_rect = None
orb_hue = 0

def make_obstacle(x):
    size = random.randint(20, 40)
    height_mult = random.randint(1, 4)
    rect = pygame.Rect(x, 0, size, size * 2 * height_mult)
    obstacles.append(rect)

def draw_triangle(surf, color, rect, ground_y, cam_x):
    rect.bottom = ground_y
    moved = rect.move(-cam_x, 0)
    points = [moved.bottomleft, moved.bottomright, moved.midtop]
    pygame.draw.polygon(surf, color, points)

def reset_game():
    global player_rect, velocity_y, jumps_left, angle, spinning, camera_x, obstacles, game_over, score, max_player_x, obstacles_passed, orb_active, orb_rect
    player_rect = player_img.get_rect()
    player_rect.midbottom = (100, height - 10)
    velocity_y = 0
    jumps_left = 2
    angle = 0
    spinning = False
    camera_x = 0
    obstacles = []
    for i in range(10):
        make_obstacle(600 + i * 600)
    game_over = False
    score = 0
    max_player_x = player_rect.centerx
    obstacles_passed = 0
    orb_active = False
    orb_rect = None

reset_game()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.VIDEORESIZE:
            width, height = event.w, event.h
            screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if game_over:
                if event.key == pygame.K_r:
                    reset_game()
            else:
                if (event.key == pygame.K_UP or event.key == pygame.K_w) and jumps_left > 0:
                    velocity_y = jump_strength
                    jumps_left -= 1
                    spinning = True

    if not game_over:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_rect.x -= speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_rect.x += speed

        if player_rect.centerx > max_player_x:
            score += (player_rect.centerx - max_player_x) * 0.01
            max_player_x = player_rect.centerx

        velocity_y += gravity
        player_rect.y += velocity_y

        ground_y = height - 10
        if player_rect.bottom >= ground_y:
            player_rect.bottom = ground_y
            velocity_y = 0
            jumps_left = 2
            spinning = False
            angle = 0

        camera_x = player_rect.centerx - 100

        if obstacles[-1].x - camera_x < width:
            make_obstacle(obstacles[-1].x + random.randint(500, 700))

        passed = [ob for ob in obstacles if ob.right < player_rect.left]
        if len(passed) > obstacles_passed:
            obstacles_passed = len(passed)
            if obstacles_passed % 2 == 0 and not orb_active:
                orb_x = player_rect.centerx + 500
                orb_rect = pygame.Rect(orb_x, ground_y - 30, 20, 20)
                orb_active = True

        if orb_active:
            orb_hue = (orb_hue + 2) % 360
            color = pygame.Color(0)
            color.hsva = (orb_hue, 100, 100, 100)
            pygame.draw.circle(screen, color, (orb_rect.centerx - camera_x, orb_rect.centery), orb_rect.width // 2)
            if player_rect.colliderect(orb_rect):
                score += 50
                orb_active = False

        for ob in obstacles:
            temp = ob.copy()
            temp.bottom = ground_y
            if player_rect.colliderect(temp):
                game_over = True

        if spinning:
            angle = (angle + spin_speed) % 360

    rel_x = -camera_x % bg_width
    screen.blit(bg, (rel_x - bg_width, 0))
    screen.blit(bg, (rel_x, 0))

    for ob in obstacles:
        draw_triangle(screen, (255, 0, 0), ob, ground_y, camera_x)

    rotated_img = pygame.transform.rotate(player_img, angle)
    rotated_rect = rotated_img.get_rect(center=(player_rect.centerx - camera_x, player_rect.centery))
    screen.blit(rotated_img, rotated_rect)

    if not game_over:
        score_text = font_small.render(f"Score: {int(score)}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        controls = [
            "W / UP - Jump",
            "D / RIGHT - Move forward",
            "A / LEFT - Move backward",
            "Double Jump - Double tap W or UP",
            " ",
            "A game made By Vivek"
        ]
        for i, line in enumerate(controls):
            text_surf = font_tiny.render(line, True, (200, 200, 200))
            screen.blit(text_surf, (width - text_surf.get_width() - 10, 10 + i * 20))
    else:
        screen.fill((0, 0, 0))
        text1 = font_big.render("You Died", True, (255, 0, 0))
        text2 = font_small.render("Press R to restart", True, (255, 0, 0))
        score_text = font_small.render(f"Score: {int(score)}", True, (255, 0, 0))
        rect1 = text1.get_rect(center=(width // 2, height // 2 - 50))
        rect2 = text2.get_rect(midtop=(width // 2, rect1.bottom + 10))
        rect3 = score_text.get_rect(midtop=(width // 2, rect2.bottom + 10))
        screen.blit(text1, rect1)
        screen.blit(text2, rect2)
        screen.blit(score_text, rect3)

    pygame.display.flip()
    clock.tick(60)
