import pygame
import sys
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize Pygame
pygame.init()

# Screen settings
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)

# Define fonts
BUTTON_FONT = pygame.font.Font(None, 40)

def map_coords(x, y):
    return x, y 

class ClickRing:
    def __init__(self, pos):
        self.pos = pos
        self.radius = 10
        self.alpha = 150  # Initial transparency
        self.growth_rate = 3
        self.fade_rate = 5

    def update(self):
        self.radius += self.growth_rate
        self.alpha = max(0, self.alpha - self.fade_rate)  # Fade out

    def draw(self, screen):
        if self.alpha > 0:
            surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, (255, 255, 255, self.alpha), (self.radius, self.radius), self.radius, 2)
            screen.blit(surface, (self.pos[0] - self.radius, self.pos[1] - self.radius))

    def is_visible(self):
        return self.alpha > 0

class Button:
    def __init__(self, rect, label, unit, selected=False):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.unit = unit
        self.selected = selected

    def draw(self, screen):
        if self.selected:
            pygame.draw.rect(screen, WHITE, self.rect, border_radius=15)
            text_surface = BUTTON_FONT.render(self.label, True, BLACK)
        else:
            pygame.draw.rect(screen, BLACK, self.rect, border_radius=15)
            pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=15)
            text_surface = BUTTON_FONT.render(self.label, True, WHITE)
        
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def draw_grid(screen, spacing):
    for x in range(0, SCREEN_WIDTH, spacing):
        pygame.draw.line(screen, LIGHT_GRAY, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, spacing):
        pygame.draw.line(screen, LIGHT_GRAY, (0, y), (SCREEN_WIDTH, y))

class Slider:
    def __init__(self, center_x, center_y, height, min_value, max_value, initial_value):
        self.rect = pygame.Rect(center_x - 10, center_y - height // 2, 20, height)
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.knob_y = self._calculate_knob_position()
    
    def _calculate_knob_position(self):
        # Convert the value to a y position on the slider
        ratio = (self.value - self.min_value) / (self.max_value - self.min_value)
        return int(self.rect.top + ratio * self.rect.height)

    def draw(self, screen):
        # Draw slider bar
        pygame.draw.rect(screen, WHITE, self.rect)
        # Draw slider knob
        pygame.draw.circle(screen, LIGHT_BLUE, (self.rect.centerx, self.knob_y), 10)

    def update_knob_position(self, y):
        # Adjust the knob position and value based on y coordinate
        if self.rect.top <= y <= self.rect.bottom:
            self.knob_y = y
            ratio = (y - self.rect.top) / self.rect.height
            self.value = int(self.min_value + ratio * (self.max_value - self.min_value))

    def is_knob_clicked(self, pos):
        knob_rect = pygame.Rect(self.rect.centerx - 10, self.knob_y - 10, 20, 20)
        return knob_rect.collidepoint(pos)

def run(screen):
    # Button setup
    button_spacing = 10
    button_width, button_height = 150, 50
    buttons = [
        Button((SCREEN_WIDTH // 4 - button_width // 2, SCREEN_HEIGHT - button_height - button_spacing, button_width, button_height), "cm", 50),
        Button((SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT - button_height - button_spacing, button_width, button_height), "in", 70),
        Button((3 * SCREEN_WIDTH // 4 - button_width // 2, SCREEN_HEIGHT - button_height - button_spacing, button_width, button_height), "large", 150)
    ]

    selected_spacing = buttons[0].unit  # Default grid spacing (cm)

    # Slider setup
    slider = Slider(SCREEN_WIDTH - 40, SCREEN_HEIGHT // 2, 200, 20, 200, selected_spacing)
    dragging_knob = False  # Track if slider knob is being dragged

    # Click rings list
    click_rings = []

    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = map_coords(*event.pos)
                
                # Add a click ring at the clicked position
                click_rings.append(ClickRing((x, y)))
                
                # Check for button clicks
                for button in buttons:
                    if button.is_clicked((x, y)):
                        selected_spacing = button.unit
                        slider.value = selected_spacing  # Update slider to match selected button
                        slider.knob_y = slider._calculate_knob_position()
                        for b in buttons:
                            b.selected = False
                        button.selected = True

                # Check if slider knob is clicked
                if slider.is_knob_clicked((x, y)):
                    dragging_knob = True

            elif event.type == pygame.MOUSEBUTTONUP:
                dragging_knob = False

            elif event.type == pygame.MOUSEMOTION:
                if dragging_knob:
                    x, y = map_coords(*event.pos)
                    slider.update_knob_position(y)
                    selected_spacing = slider.value
                    # Deselect all buttons when using slider
                    for b in buttons:
                        b.selected = False

        screen.fill(BLACK)

        # Draw grid based on selected spacing
        draw_grid(screen, selected_spacing)

        # Draw buttons
        for button in buttons:
            button.draw(screen)

        # Draw slider
        slider.draw(screen)

        # Update and draw click rings
        for ring in click_rings[:]:
            ring.update()
            ring.draw(screen)
            if not ring.is_visible():
                click_rings.remove(ring)

        pygame.display.flip()
        pygame.time.delay(50)

if __name__ == '__main__':
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption('Grid with Adjustable Spacing')
    run(screen)
