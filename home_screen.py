import pygame
from pygame import mixer
import time
import os
import sys
import math
from dotenv import load_dotenv

load_dotenv()

# Initialize Pygame
pygame.init()

# Initialize the mixer
mixer.init()

# Screen settings
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
NAVY_BLUE = (20, 20, 40)
LIGHT_BLUE = (173, 216, 230)
HOME_TOGGLE_DELAY = 1.0  # Delay in seconds for home button toggle
APP_SELECT_DELAY = 1.0  # Delay to prevent immediate app launch
LOGO_DELAY = 1  # Delay in seconds before showing the logo


def play_sound(file_path):
    try:
        mixer.music.load(file_path)
        mixer.music.play()
    except Exception as e:
        print(f"Error playing sound {file_path}: {e}")


class AppCircle:
    def __init__(self, center, radius, app_index, final_pos, is_main=False):
        self.center = center
        self.radius = radius
        self.app_index = app_index
        self.is_main = is_main
        self.visible = is_main
        self.final_pos = final_pos
        self.hover_time = 0
        self.is_hovered_flag = False
        self.animation_start_time = None
        self.is_animating = False
        self.image = self.load_image()

    def load_image(self):
        try:
            if self.is_main:
                image_path = './logo.jpg'
                if os.path.exists(image_path):
                    image = pygame.image.load(image_path)
                    return pygame.transform.scale(image, (2 * self.radius, 2 * self.radius))
            else:
                image_path = f'./apps/app_{self.app_index}/app_{self.app_index}.jpg'
                if os.path.exists(image_path):
                    image = pygame.image.load(image_path)
                    return pygame.transform.scale(image, (2 * self.radius, 2 * self.radius))
            print(f"Image not found for AppCircle: {self.app_index}")
        except Exception as e:
            print(f"Error loading image for AppCircle {self.app_index}: {e}")
        return None

    def draw(self, screen):
        # Adjust radius when hovered
        if self.is_hovered_flag:
            current_radius = self.radius + min((time.time() - self.hover_time) * 10, self.radius * 0.5)
        else:
            current_radius = self.radius

        # Animate position
        if self.animation_start_time is not None:
            elapsed_time = time.time() - self.animation_start_time
            if elapsed_time < 0.5:  # Animation duration is 0.5 seconds
                t = elapsed_time / 0.5
                # Interpolate between center and final_pos
                if self.visible:
                    self.center = (
                        int((1 - t) * SCREEN_SIZE[0] // 2 + t * self.final_pos[0]),
                        int((1 - t) * SCREEN_SIZE[1] // 2 + t * self.final_pos[1])
                    )
                else:
                    self.center = (
                        int(t * SCREEN_SIZE[0] // 2 + (1 - t) * self.final_pos[0]),
                        int(t * SCREEN_SIZE[1] // 2 + (1 - t) * self.final_pos[1])
                    )
            else:
                self.center = self.final_pos if self.visible else (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2)
                self.animation_start_time = None
                self.is_animating = False

        # Draw the circle
        if self.visible or self.is_animating:
            if self.image:
                top_left = (self.center[0] - self.radius, self.center[1] - self.radius)
                screen.blit(self.image, top_left)
            else:
                pygame.draw.circle(screen, NAVY_BLUE, self.center, int(current_radius))
            pygame.draw.circle(screen, LIGHT_BLUE, self.center, int(current_radius), 5)

    def is_hovered(self, pos):
        hovered = math.hypot(pos[0] - self.center[0], pos[1] - self.center[1]) <= self.radius
        return hovered


def map_coords(x, y):
    return x, y 


def create_circles():
    circles = []
    num_circles = 8
    center_x, center_y = SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2
    main_circle_radius = 100
    app_circle_radius = 50
    distance = 250  # Distance from main circle to app circles

    # Create the main circle
    main_circle = AppCircle((center_x, center_y), main_circle_radius, 0, (center_x, center_y), is_main=True)
    circles.append(main_circle)

    # Create app circles around the main circle
    angle_step = 360 / num_circles
    for i in range(num_circles):
        angle = math.radians(angle_step * i)
        x = center_x + int(distance * math.cos(angle))
        y = center_y + int(distance * math.sin(angle))
        circles.append(AppCircle((center_x, center_y), app_circle_radius, i + 1, (x, y)))
    return circles


def run_home_screen(screen):
    circles = create_circles()
    main_circle = circles[0]
    running = True
    apps_visible = False
    last_toggle_time = 0
    last_app_select_time = 0

    start_time = time.time()
    while time.time() - start_time < LOGO_DELAY:
        screen.fill((0, 0, 0))
        pygame.display.flip()
        pygame.time.delay(100)

    play_sound("./audio/startup.wav")
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                mapped_x, mapped_y = map_coords(x, y)

                main_clicked = False
                for circle in circles:
                    if circle.is_hovered((mapped_x, mapped_y)):
                        if circle.is_main:
                            main_clicked = True  # Track if the main circle was clicked
                            play_sound("./audio/home.wav")
                            if time.time() - last_toggle_time > HOME_TOGGLE_DELAY:
                                apps_visible = not apps_visible
                                last_toggle_time = time.time()
                                for app_circle in circles[1:]:
                                    app_circle.visible = apps_visible
                                    app_circle.animation_start_time = time.time()
                                    app_circle.is_animating = True
                        elif circle.visible and apps_visible and not main_clicked:  # Only process app circle clicks if main was not clicked
                            if time.time() > last_app_select_time:
                                try:
                                    app = f'app_{circle.app_index}.app_{circle.app_index}'
                                    mod = __import__(f'apps.{app}', fromlist=[''])
                                    play_sound("./audio/confirmation.wav")
                                    mod.run(screen)  # Run the app
                                    last_app_select_time = time.time()
                                except ModuleNotFoundError as e:
                                    play_sound("./audio/reject.wav")
                    else:
                        circle.hover_time = time.time() if circle.visible else 0


        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, (255, 255, 255), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 10)

        for circle in circles:
            circle.draw(screen)

        pygame.display.flip()
        pygame.time.delay(50)


if __name__ == '__main__':
    os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'
    screen = pygame.display.set_mode(SCREEN_SIZE, pygame.FULLSCREEN)    
    pygame.display.set_caption('Home Screen')
    run_home_screen(screen)
