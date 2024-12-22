import pygame
from pygame import mixer
import sys
import time
import math
from dotenv import load_dotenv
import os

load_dotenv()
# Initialize Pygame
pygame.init()
# Initialize the mixer
mixer.init()
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
BLACK = (0, 0, 0)
LIGHT_BLUE = (173, 216, 230)
WHITE = (255, 255, 255)
NAVY_BLUE = (20, 20, 40)
PIXEL_TO_MM = 0.4478  # Adjust this variable as needed

def map_coords(x, y):
    return x, y 

def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def play_sound(file_path):
    mixer.music.stop()
    mixer.music.load(file_path)
    mixer.music.play()

def draw_line_with_measurement(screen, start_point, end_point):
    if start_point and end_point:
        pygame.draw.line(screen, LIGHT_BLUE, start_point, end_point, 2)
        pygame.draw.circle(screen, LIGHT_BLUE, start_point, 5)
        pygame.draw.circle(screen, LIGHT_BLUE, end_point, 5)
        mid_line_point = ((start_point[0] + end_point[0]) // 2, (start_point[1] + end_point[1]) // 2)
        line_length = distance(start_point, end_point) * PIXEL_TO_MM
        font = pygame.font.Font(None, 36)
        text_surface = font.render(f'{line_length:.2f} mm', True, WHITE)
        screen.blit(text_surface, mid_line_point)

def run(screen):
    running = True
    drawing = False
    start_point = None
    end_point = None
    permanent_lines = []

    home_button_center = (150, 100)
    home_button_radius = 50

    clear_button_rect = pygame.Rect((SCREEN_SIZE[0] // 2 - 150, SCREEN_SIZE[1] - 150, 300, 70))

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                mapped_x, mapped_y = map_coords(x, y)

                if distance((mapped_x, mapped_y), home_button_center) <= home_button_radius:
                    running = False
                    play_sound('audio/back.wav')
                elif clear_button_rect.collidepoint(mapped_x, mapped_y):
                    permanent_lines = []
                    play_sound('audio/back.wav')
                else:
                    start_point = (mapped_x, mapped_y)
                    drawing = True
                    play_sound('audio/quick_click.wav')
            elif event.type == pygame.MOUSEBUTTONUP:
                if drawing and start_point and end_point:
                    permanent_lines.append((start_point, end_point))
                    play_sound('audio/quick_click.wav')
                drawing = False
                start_point = None
                end_point = None
            elif event.type == pygame.MOUSEMOTION:
                if drawing:
                    end_point = map_coords(*event.pos)

        screen.fill(BLACK)

        # Draw all permanent lines
        for line in permanent_lines:
            draw_line_with_measurement(screen, line[0], line[1])

        # Draw the current line being drawn
        if drawing and start_point and end_point:
            draw_line_with_measurement(screen, start_point, end_point)

        # Draw the Home button
        pygame.draw.circle(screen, NAVY_BLUE, home_button_center, home_button_radius)
        pygame.draw.circle(screen, LIGHT_BLUE, home_button_center, home_button_radius, 5)
        font = pygame.font.Font(None, 36)
        text_surface = font.render('Home', True, WHITE)
        text_rect = text_surface.get_rect(center=home_button_center)
        screen.blit(text_surface, text_rect)

        # Draw the Clear button
        pygame.draw.rect(screen, NAVY_BLUE, clear_button_rect, border_radius=15)
        pygame.draw.rect(screen, LIGHT_BLUE, clear_button_rect, 5, border_radius=15)
        text_surface = font.render('Clear', True, WHITE)
        text_rect = text_surface.get_rect(center=clear_button_rect.center)
        screen.blit(text_surface, text_rect)

        pygame.display.flip()
        pygame.time.delay(1)

if __name__ == '__main__':
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption('Measurement App')
    run(screen)
