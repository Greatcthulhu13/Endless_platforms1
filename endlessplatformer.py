import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Initialize Pygame Mixer for sound
pygame.mixer.init()

# Screen dimensions
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Endless Platforms")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)  # Blue color for the player

# Clock
clock = pygame.time.Clock()

# Load sound effects
jump_sound = pygame.mixer.Sound("jump_sound.mp3")
death_sound = pygame.mixer.Sound("death_sound.mp3")

# Load background music and start playing it
pygame.mixer.music.load("endless_platforms.mp3")
pygame.mixer.music.play(-1)  # Play the music indefinitely

# Player Class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(BLUE)  # Set player color to blue
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.vel_y = 0
        self.jumping = False

        # World position
        self.world_x = WIDTH // 2

    def update(self, keys):
        # Horizontal movement
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
            self.world_x -= 5
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5
            self.world_x += 5

        # Jumping
        if keys[pygame.K_SPACE] and not self.jumping:
            self.vel_y = -15
            self.jumping = True
            jump_sound.play()  # Play jump sound

        # Gravity
        self.vel_y += 1
        self.rect.y += self.vel_y

        # Prevent player from falling off screen
        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.jumping = False
            self.vel_y = 0

# Platform Class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.world_x = x

    def update(self, camera):
        # Adjust platform position based on camera offset
        self.rect.x = self.world_x + camera.offset_x

# Camera Class
class Camera:
    def __init__(self):
        self.offset_x = 0

    def apply(self, entity):
        # Apply the camera offset to an entity's position
        return entity.rect.x + self.offset_x, entity.rect.y

    def update(self, player):
        # Update the camera position based on the player's position
        if player.rect.centerx > WIDTH * 0.6:
            self.offset_x = -(player.world_x - WIDTH * 0.6)
        elif player.rect.centerx < WIDTH * 0.4:
            self.offset_x = -(player.world_x - WIDTH * 0.4)
        else:
            self.offset_x = 0

# Create a player instance
player = Player()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

# Create initial platform directly beneath the player
platforms = pygame.sprite.Group()
starting_platform = Platform(player.rect.centerx - 100, player.rect.bottom + 10, 200, 20)
platforms.add(starting_platform)
all_sprites.add(starting_platform)

# Handle Collisions
def handle_collisions(player, platforms):
    hits = pygame.sprite.spritecollide(player, platforms, False)
    if hits:
        if player.vel_y > 0:
            player.rect.bottom = hits[0].rect.top
            player.jumping = False
            player.vel_y = 0

# Generate a new platform
def generate_platform():
    # Randomize the position and size
    width = random.randint(100, 200)
    height = 20
    x = platforms.sprites()[-1].world_x + random.randint(200, 300)  # Horizontal spacing
    y = random.randint(HEIGHT - 400, HEIGHT - 100)

    platform = Platform(x, y, width, height)
    platforms.add(platform)
    all_sprites.add(platform)

# Camera instance
camera = Camera()

# Generate initial platforms
for _ in range(4):  # 4 additional platforms, since 1 is already added
    generate_platform()

# Main game loop
running = True
game_over = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over:
        keys = pygame.key.get_pressed()

        # Update player and camera
        player.update(keys)
        handle_collisions(player, platforms)
        camera.update(player)

        # Check if player has landed on the ground (game over condition)
        if player.rect.bottom >= HEIGHT:
            game_over = True
            death_sound.play()  # Play death sound
            pygame.mixer.music.stop()  # Stop background music

        # Update platforms with camera
        for platform in platforms:
            platform.update(camera)

        # Generate new platforms as the player moves forward
        if platforms.sprites()[-1].world_x < player.world_x + WIDTH:
            generate_platform()

        # Remove platforms that are out of the screen
        for platform in platforms.copy():
            if platform.rect.right < 0:
                platforms.remove(platform)
                all_sprites.remove(platform)

    # Draw everything
    screen.fill(BLACK)
    for sprite in all_sprites:
        screen.blit(sprite.image, sprite.rect.topleft)

    if game_over:
        # Display Game Over message
        font = pygame.font.SysFont(None, 74)
        text = font.render("GAME OVER", True, RED)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
