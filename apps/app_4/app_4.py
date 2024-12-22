import pygame
import sys
import os
from dotenv import load_dotenv
from RealtimeSTT import AudioToTextRecorder

load_dotenv()

# Initialize Pygame
pygame.init()
mixer = pygame.mixer
mixer.init()

# Screen settings
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_BLUE = (173, 216, 230)
NAVY_BLUE = (20, 20, 40)
BLUE = (0, 0, 255)

# Define fonts
LARGE_FONT = pygame.font.Font(None, 100)
BUTTON_FONT = pygame.font.Font(None, 40)

# STT Recorder
recorder = AudioToTextRecorder(spinner=False, model="tiny.en", language="en", post_speech_silence_duration=0.1, silero_sensitivity=0.4)

class KeyButton:
    def __init__(self, rect, label, color=NAVY_BLUE, border_color=LIGHT_BLUE):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.color = color
        self.border_color = border_color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 5)
        if self.label:
            text_surface = BUTTON_FONT.render(self.label, True, WHITE)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def play_click_sound():
    mixer.music.load('./audio/quick_click.wav')
    mixer.music.play()

def create_keyboard():
    buttons = []
    # Keyboard layout with Backspace as ←
    rows = [
        ["Tab", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "←"],  # Replaced Backspace with ←
        ["Caps", "A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'"],
        ["Shift", "Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "Shift"],
        ["Space"]
    ]

    x_offset = (SCREEN_WIDTH - 1200) // 2
    y_offset = SCREEN_HEIGHT - 400
    button_width = 80
    button_height = 80
    spacing = 8

    row_offsets = [0, button_width // 2, button_width, button_width * 1.5]

    for row_index, row in enumerate(rows):
        x = x_offset + row_offsets[row_index]
        y = y_offset + row_index * (button_height + spacing)

        for char in row:
            width = button_width
            if char in {"Tab", "Caps", "Shift", "←"}:
                width = int(button_width * 1.5)
            elif char == "Space":
                width = button_width * 6
                x = (SCREEN_WIDTH - width) // 2

            buttons.append(KeyButton((x, y, width, button_height), char))
            x += width + spacing

    # Add Home button at top right
    home_button_rect = pygame.Rect(SCREEN_WIDTH - 150, 20, 130, 60)
    buttons.append(KeyButton(home_button_rect, "Home"))

    # Add Speech button at bottom right
    speech_button_rect = pygame.Rect(SCREEN_WIDTH - 180, SCREEN_HEIGHT - 100, 150, 60)
    buttons.append(KeyButton(speech_button_rect, "Speech"))

    return buttons

def run(screen):
    running = True
    buttons = create_keyboard()
    typed_text = ""
    listening = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos

                for button in buttons:
                    if button.is_clicked((x, y)):
                        play_click_sound()

                        if button.label == "Space":
                            typed_text += " "
                        elif button.label == "Tab":
                            typed_text += "    "
                        elif button.label == "←":
                            typed_text = typed_text[:-1]
                        elif button.label == "Home":
                            running = False
                        elif button.label == "Speech":
                            print("button click")
                            listening = not listening
                            if listening:
                                recorder.start()
                            else:
                                recorder.stop()
                        else:
                            typed_text += button.label
                        break

        if listening:
            current_text = recorder.text()
            if current_text:
                typed_text += f" {current_text}."

        screen.fill(BLACK)

        # Display typed text
        text_surface = LARGE_FONT.render(typed_text, True, WHITE)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        screen.blit(text_surface, text_rect)

        # Draw keyboard buttons
        for button in buttons:
            if button.label == "Speech":
                button.color = BLUE if listening else NAVY_BLUE
            button.draw(screen)

        pygame.display.flip()
        pygame.time.delay(1)

if __name__ == '__main__':
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption('Keyboard App with Speech Input')
    run(screen)
