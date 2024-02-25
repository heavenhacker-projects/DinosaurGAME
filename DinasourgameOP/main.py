import pygame
import sys
import random


# Initialize Pygame
pygame.init()

# Initialize the mixer
pygame.mixer.init()
# Load your music file
pygame.mixer.music.load('Patreon Challenge - 08.ogg')
# Play the music, the -1 means it will loop indefinitely
pygame.mixer.music.play(-1)



# Screen setup
infoObject = pygame.display.Info()
SCREEN_WIDTH = infoObject.current_w
SCREEN_HEIGHT = infoObject.current_h
GROUND_HEIGHT = 150
FPS = 60


# Colors
WHITE = (255, 255, 255)


# Screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dinosaur Game")


# Load font
font = pygame.font.Font('QuinqueFive.otf', 24)


# Load and process images
move_img = pygame.image.load('move.png').convert_alpha()
dino_run_frames = [move_img.subsurface((i * (move_img.get_width() // 6), 0, move_img.get_width() // 6, move_img.get_height())) for i in range(6)]
dino_run_frames = [pygame.transform.scale(frame, (150, 150)) for frame in dino_run_frames]


jump_img = pygame.image.load('jump.png').convert_alpha()
dino_jump_frames = [jump_img.subsurface((i * (jump_img.get_width() // 4), 0, jump_img.get_width() // 4, jump_img.get_height())) for i in range(4)]
dino_jump_frames = [pygame.transform.scale(frame, (150, 150)) for frame in dino_jump_frames]


idle_img = pygame.image.load('idle.png').convert_alpha()
idle_frames = [idle_img.subsurface((i * (idle_img.get_width() // 3), 0, idle_img.get_width() // 3, idle_img.get_height())) for i in range(3)]
idle_frames = [pygame.transform.scale(frame, (150, 150)) for frame in idle_frames]


background_img = pygame.image.load('backpurpepic.jpg').convert()
background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))


ground_image = pygame.image.load('terrain.png').convert_alpha()
ground_image = pygame.transform.scale(ground_image, (SCREEN_WIDTH, GROUND_HEIGHT))


cactus_img = pygame.image.load('cactus.png').convert_alpha()
cactus_img = pygame.transform.scale(cactus_img, (50, 100))


cherries_img = pygame.image.load('Cherries.png').convert_alpha()
cherries_frames = [cherries_img.subsurface((i * (cherries_img.get_width() // 17), 0, cherries_img.get_width() // 17, cherries_img.get_height())) for i in range(17)]
cherries_frames = [pygame.transform.scale(frame, (100, 100)) for frame in cherries_frames]


collected_img = pygame.image.load('collected.png').convert_alpha()
collected_frames = [collected_img.subsurface((i * (collected_img.get_width() // 6), 0, collected_img.get_width() // 6, collected_img.get_height())) for i in range(6)]
collected_frames = [pygame.transform.scale(frame, (100, 100)) for frame in collected_frames]


# Load and process helper images
helper_images = [pygame.image.load(f'helper{i}.png').convert_alpha() for i in range(1, 5)]
helper_frames = [pygame.transform.scale(frame, (150, 150)) for frame in helper_images]


# Load the logo image
logo_img = pygame.image.load('dinodash.png').convert_alpha()
logo_img = pygame.transform.scale(logo_img, (800, 200))  # Adjust size as needed


# Game variables
dino_size = 150
dino_x = 50
dino_y = SCREEN_HEIGHT - GROUND_HEIGHT - dino_size + 17
gravity = 1.3
is_jumping = False
is_game_active = False
score = 0
double_jump_available = True
is_riding_helper = False  # Variable to track if the dinosaur is riding the helper


ground_x = 0
background_x = 0


clock = pygame.time.Clock()


cacti = []
cherries = []
collected_animations = []


last_cherry_spawn_time = 0  # Tracks the last time a cherry was spawned
cherry_spawn_interval = 5000  # 5 seconds in milliseconds


# Helper variables
helper_x = 200
helper_y = SCREEN_HEIGHT - GROUND_HEIGHT - 300
helper_frame_count = 0
helper_flipped = False  # New variable to track if the helper is flipped
helper_ride_timer = 0  # Timer to track how long the dinosaur has ridden the helper
helper_ride_duration = 8000  # 8 seconds in milliseconds


def jump():
   global is_jumping, dino_y_speed, double_jump_available
   if not is_jumping and is_game_active:
       is_jumping = True
       dino_y_speed = -23
       double_jump_available = False
   elif double_jump_available and is_jumping:
       dino_y_speed = -23  # Apply the same upward speed for the second jump
       double_jump_available = False  # Disable further jumps until landing


def spawn_cactus():
   global cacti
   min_distance = 300  # Minimum distance between each cactus
   if cacti:  # Check if there are already cacti on the screen
       last_cactus_x = cacti[-1][0]  # Get the x position of the last cactus
       # Ensure the new cactus is spawned only if there's enough distance from the last cactus
       if SCREEN_WIDTH - last_cactus_x > min_distance and random.randint(0, 200) < 2:
           cacti.append([SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT - 100])
   else:  # If there are no cacti, spawn one
       if random.randint(0, 200) < 2:
           cacti.append([SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT - 100])


def spawn_cherry(current_time):
   global cherries, last_cherry_spawn_time
   if current_time - last_cherry_spawn_time > cherry_spawn_interval:
       cherries.append([SCREEN_WIDTH, random.randint(200, SCREEN_HEIGHT - GROUND_HEIGHT - 150), 0])  # Random height within jump reach
       last_cherry_spawn_time = current_time


def update_cherries():
   global cherries, collected_animations, score
   cherries = [cherry for cherry in cherries if cherry[0] > -50]
   for cherry in list(cherries):
       cherry[0] -= 5  # Move cherries to the left
       cherry[2] = (cherry[2] + 1) % (len(cherries_frames) * 3)  # Update cherry frame for animation, slowed down
       if pygame.Rect(dino_x, dino_y, dino_size, dino_size).colliderect(pygame.Rect(cherry[0], cherry[1], 1, 1)):
           score += 100  # Increase score for collecting cherry
           collected_animations.append([cherry[0], cherry[1], 0])  # Add collected animation
           cherries.remove(cherry)  # Remove cherry from list


dhelper_ride_duration = 5000  # Duration in milliseconds (5 seconds)
helper_flying = False
helper_flying_start_time = 0


helper_velocity = 0
helper_ride_duration = 300000
def move_helper():
   global helper_x, helper_y, helper_frame_count, helper_flipped, dino_x, dino_y, is_jumping, is_riding_helper, helper_flying, helper_flying_start_time, dino_y_speed, helper_velocity, helper_ride_timer


   # Increment the helper frame count
   helper_frame_count += 1
   if helper_frame_count >= len(helper_frames) * 12:
       helper_frame_count = 0


   # Create rectangles for the dinosaur and helper for collision detection
   dino_rect = pygame.Rect(dino_x, dino_y, dino_size, dino_size)
   helper_rect = pygame.Rect(helper_x, helper_y, 150, 150)


   # If the dinosaur collides with the helper and is not already riding it
   if dino_rect.colliderect(helper_rect) and not is_riding_helper:
       # Start riding the helper
       is_riding_helper = True
       helper_flipped = True
       helper_flying = True
       helper_flying_start_time = pygame.time.get_ticks()  # Record the start time of the ride
       helper_ride_timer = 0  # Reset the ride timer


       # Adjust the helper's position to stay on the ground if needed
       if helper_rect.colliderect(pygame.Rect(ground_x, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT)):
           helper_velocity = 0
           helper_y = SCREEN_HEIGHT - GROUND_HEIGHT - 150


       # Reset jumping and vertical speed for the dinosaur
       is_jumping = False
       dino_y_speed = 0
       helper_velocity = 0


   # If the dinosaur is currently riding the helper
   if is_riding_helper:
       # If the helper is flying
       if helper_flying:
           # Check for space key to apply upward force
           keys = pygame.key.get_pressed()
           if keys[pygame.K_SPACE]:
               helper_velocity = -10  # Upward force when space is pressed


           # Apply gravity to the helper's vertical movement
           helper_velocity += gravity
           helper_y += helper_velocity


           # Prevent the helper from going off-screen vertically
           if helper_y < 0:
               helper_y = 0
               helper_velocity = 0
           elif helper_y > SCREEN_HEIGHT - GROUND_HEIGHT - dino_size:
               helper_y = SCREEN_HEIGHT - GROUND_HEIGHT - dino_size
               helper_velocity = 0


           # Update the dinosaur's position to match the helper's position
           dino_x = helper_x + 20
           dino_y = helper_y - dino_size + 101


           # Check if the ride duration has exceeded 5 seconds or if the helper reaches the ground
           current_time = pygame.time.get_ticks()
           helper_ride_timer = current_time - helper_flying_start_time
           if helper_ride_timer > helper_ride_duration or helper_y >= SCREEN_HEIGHT - GROUND_HEIGHT - dino_size:
               # End the ride and make the dinosaur fall due to gravity
               helper_flying = False
               is_riding_helper = False
               dino_y_speed = gravity


   # If the helper is not flying, move it horizontally
   if not helper_flying:
       if not helper_flipped:
           helper_x -= 2
       else:
           helper_x += 2


       # If the helper reaches the edge of the screen, reset its position and flags
       if helper_x <= -150 or helper_x >= SCREEN_WIDTH:
           helper_x = SCREEN_WIDTH if helper_x <= -150 else -150
           helper_flipped = False
           is_riding_helper = False




# Function to draw the helper on the screen
def draw_helper():
   current_frame = helper_frames[helper_frame_count // 12]
   if helper_flipped:
       current_frame = pygame.transform.flip(current_frame, True, False)
   screen.blit(current_frame, (helper_x, helper_y))


# Helper variables
last_helper_spawn_time = 0  # Tracks the last time a helper was spawned
helper_spawn_interval = 10000  # 10 seconds in milliseconds


def main():
   global dino_y, dino_y_speed, is_jumping, ground_x, background_x, is_game_active, score, cacti, cherries, collected_animations, double_jump_available, logo_img


   dino_y_speed = 0
   run_count = 0
   jump_count = 0
   idle_count = 0
   collected_count = 0


   while True:
       screen.blit(background_img, (background_x, 0))
       screen.blit(background_img, (background_x + SCREEN_WIDTH, 0))
       screen.blit(ground_image, (ground_x, SCREEN_HEIGHT - GROUND_HEIGHT))
       screen.blit(ground_image, (ground_x + SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT))


       background_x -= 1
       if background_x <= -SCREEN_WIDTH:
           background_x = 0


       if is_game_active:
           ground_x -= 5
           if ground_x <= -SCREEN_WIDTH:
               ground_x = 0


       current_time = pygame.time.get_ticks()


       spawn_cherry(current_time)
       spawn_cactus()
       for event in pygame.event.get():
           if event.type == pygame.QUIT:
               pygame.quit()
               sys.exit()
           if event.type == pygame.KEYDOWN:
               if event.key == pygame.K_SPACE:
                   if not is_game_active:
                       is_game_active = True
                       cacti.clear()
                       cherries.clear()
                       collected_animations.clear()
                       score = 0
                       # Remove the logo image from memory
                       del logo_img
                   elif not is_jumping and double_jump_available:
                       jump()


       if is_game_active:
           if is_jumping:
               dino_y += dino_y_speed
               dino_y_speed += gravity
               if dino_y > SCREEN_HEIGHT - GROUND_HEIGHT - dino_size + 17:
                   dino_y = SCREEN_HEIGHT - GROUND_HEIGHT - dino_size + 17
                   is_jumping = False
                   double_jump_available = True
               screen.blit(dino_jump_frames[jump_count // 6], (dino_x, dino_y))
               jump_count += 1
               if jump_count >= 24:
                   jump_count = 0
           else:
               screen.blit(dino_run_frames[run_count // 6], (dino_x, dino_y))
               run_count += 1
               if run_count >= 36:
                   run_count = 0


           cacti = [cactus for cactus in cacti if cactus[0] > -cactus_img.get_width()]
           for cactus in cacti:
               cactus[0] -= 5
               screen.blit(cactus_img, (cactus[0], SCREEN_HEIGHT - GROUND_HEIGHT - 100))


           update_cherries()
           for cherry in cherries:
               screen.blit(cherries_frames[cherry[2] // 3], (cherry[0], cherry[1]))  # Slowed down cherry animation


           collected_animations = [anim for anim in collected_animations if anim[2] < 6 * 4]  # Slow down collected animation
           for anim in list(collected_animations):
               screen.blit(collected_frames[anim[2] // 10], (anim[0], anim[1]))  # Slow down animation frame update
               anim[2] += 1


           move_helper()
           draw_helper()


           score_text = font.render(f"Score: {score}", True, WHITE)
           screen.blit(score_text, (10, 10))


       else:  # Game is not active
           # Display the logo
           logo_rect = logo_img.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4))
           screen.blit(logo_img, logo_rect)


           # Instructions to start the game
           title_text = font.render("Press SPACE to start", True, WHITE)
           title_rect = title_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
           screen.blit(title_text, title_rect)


           # Dinosaur idle animation or any placeholder before the game starts
           screen.blit(idle_frames[idle_count // 10], (dino_x, dino_y))
           idle_count += 1
           if idle_count >= 30:
               idle_count = 0


       pygame.display.update()
       clock.tick(FPS)


if __name__ == "__main__":
   main()

