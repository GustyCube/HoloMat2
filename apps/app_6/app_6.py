import pygame
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

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
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Settings
GRID_SPACING = 70  # cm spacing in pixels
BUTTON_FONT = pygame.font.Font(None, 40)
TRACE_THICKNESS = 20
RING_RADIUS = 26
RING_THICKNESS = 18
BUTTON_HEIGHT = 80  # Increased button height

def map_coords(x, y):
    return x, y 

class Button:
    def __init__(self, rect, label):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.selected = False

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

class ColorButton:
    def __init__(self, rect, color):
        self.rect = pygame.Rect(rect)
        self.color = color
        self.selected = False

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=15)
        if self.selected:
            pygame.draw.rect(screen, WHITE, self.rect, 3, border_radius=15)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def draw_grid(screen):
    for x in range(0, SCREEN_WIDTH, GRID_SPACING):
        pygame.draw.line(screen, LIGHT_GRAY, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, GRID_SPACING):
        pygame.draw.line(screen, LIGHT_GRAY, (0, y), (SCREEN_WIDTH, y))

def get_nearest_grid_point(pos):
    return (round(pos[0] / GRID_SPACING) * GRID_SPACING, round(pos[1] / GRID_SPACING) * GRID_SPACING)

def export_design(traces, holes):
    # Create a new surface with the same size for export
    export_surface = pygame.Surface(SCREEN_SIZE)
    export_surface.fill(BLACK)

    # Draw traces
    for trace_start, trace_end, trace_color in traces:
        pygame.draw.line(export_surface, trace_color, trace_start, trace_end, TRACE_THICKNESS)

    # Draw holes with a dynamic inner black circle
    for hole_pos, hole_color in holes:
        pygame.draw.circle(export_surface, hole_color, hole_pos, RING_RADIUS, RING_THICKNESS)
        inner_circle_radius = RING_RADIUS - RING_THICKNESS  # Dynamic calculation for the inner circle
        pygame.draw.circle(export_surface, BLACK, hole_pos, inner_circle_radius)

    # Save each color layer separately as .png for quality
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pygame.image.save(export_surface, f"pcb_design_{timestamp}.png")

def run(screen):
    button_spacing = 10
    button_width, button_height = 160, BUTTON_HEIGHT  # Increased button size

    buttons = [
        Button((SCREEN_WIDTH // 5 - button_width // 2, SCREEN_HEIGHT - button_height - button_spacing, button_width, button_height), "Hole"),
        Button((2 * SCREEN_WIDTH // 5 - button_width // 2, SCREEN_HEIGHT - button_height - button_spacing, button_width, button_height), "Trace"),
        Button((3 * SCREEN_WIDTH // 5 - button_width // 2, SCREEN_HEIGHT - button_height - button_spacing, button_width, button_height), "Clear"),
        Button((4 * SCREEN_WIDTH // 5 - button_width // 2, SCREEN_HEIGHT - button_height - button_spacing, button_width, button_height), "Undo"),
        Button((4 * SCREEN_WIDTH // 5 - button_width // 2, 20, button_width, button_height), "Home"),
        Button((SCREEN_WIDTH - button_width - 10, SCREEN_HEIGHT - button_height - button_spacing, button_width, button_height), "Export")
    ]

    colors = [WHITE, RED, BLUE]
    color_buttons = [ColorButton((SCREEN_WIDTH - 100, 200 + i * 100, 80, 80), color) for i, color in enumerate(colors)]
    selected_trace_color = WHITE
    selected_hole_color = WHITE

    placing_hole = False
    drawing_trace = False
    traces = []
    holes = []
    actions = []  # Stores both traces and holes to support undoing
    start_point = None
    dragging_trace = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = map_coords(*event.pos)
                pos = get_nearest_grid_point((x, y))

                button_clicked = False
                for button in buttons:
                    if button.is_clicked((x, y)):
                        button_clicked = True
                        for b in buttons:
                            b.selected = False
                        button.selected = True

                        if button.label == "Hole":
                            placing_hole = True
                            drawing_trace = False
                        elif button.label == "Trace":
                            placing_hole = False
                            drawing_trace = True
                        elif button.label == "Clear":
                            traces.clear()
                            holes.clear()
                            actions.clear()
                        elif button.label == "Undo":
                            if actions:
                                last_action = actions.pop()
                                if last_action[0] == "hole":
                                    holes.pop()
                                elif last_action[0] == "trace":
                                    traces.pop()
                        elif button.label == "Home":
                            return  # Return to the home screen
                        elif button.label == "Export":
                            export_design(traces, holes)
                        break

                if button_clicked:
                    continue

                color_button_clicked = False
                if placing_hole or drawing_trace:
                    for color_button in color_buttons:
                        if color_button.is_clicked((x, y)):
                            color_button_clicked = True
                            for cb in color_buttons:
                                cb.selected = False
                            color_button.selected = True
                            if placing_hole:
                                selected_hole_color = color_button.color
                            elif drawing_trace:
                                selected_trace_color = color_button.color
                            break

                if color_button_clicked:
                    continue

                if placing_hole:
                    holes.append((pos, selected_hole_color))
                    actions.append(("hole", pos, selected_hole_color))
                
                elif drawing_trace:
                    start_point = pos
                    dragging_trace = True

            elif event.type == pygame.MOUSEBUTTONUP:
                if dragging_trace and start_point:
                    end_point = get_nearest_grid_point(map_coords(*event.pos))
                    traces.append((start_point, end_point, selected_trace_color))
                    actions.append(("trace", (start_point, end_point, selected_trace_color)))
                    dragging_trace = False
                    start_point = None

            elif event.type == pygame.MOUSEMOTION:
                if dragging_trace and start_point:
                    end_point = get_nearest_grid_point(map_coords(*event.pos))
                    temp_trace = (start_point, end_point, selected_trace_color)
                else:
                    temp_trace = None

        screen.fill(BLACK)

        draw_grid(screen)

        for trace_start, trace_end, color in traces:
            pygame.draw.line(screen, color, trace_start, trace_end, TRACE_THICKNESS)

        if dragging_trace and temp_trace:
            pygame.draw.line(screen, temp_trace[2], temp_trace[0], temp_trace[1], TRACE_THICKNESS)

        for hole_pos, color in holes:
            pygame.draw.circle(screen, color, hole_pos, RING_RADIUS, RING_THICKNESS)
            # Dynamic inner black circle for the hole
            inner_circle_radius = RING_RADIUS - (RING_THICKNESS)
            pygame.draw.circle(screen, BLACK, hole_pos, inner_circle_radius)

        for button in buttons:
            button.draw(screen)

        for color_button in color_buttons:
            color_button.draw(screen)

        pygame.display.flip()
        pygame.time.delay(50)

if __name__ == '__main__':
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption('PCB Designer')
    run(screen)
