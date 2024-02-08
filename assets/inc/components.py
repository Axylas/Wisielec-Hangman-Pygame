import pygame
from pygame.locals import *
import json
import os
import sys

def resource_path(nazwa_pliku):
    # Jeśli aplikacja jest "zamrożona" (skompilowana przez PyInstaller)
    if getattr(sys, 'frozen', False):
        # Pobierz ścieżkę do katalogu, w którym znajduje się skompilowany plik .exe
        biezacy_katalog = os.path.dirname(sys.executable)
    else:
        # Pobierz ścieżkę do katalogu, w którym znajduje się aktualnie uruchamiany skrypt
        biezacy_katalog = os.path.dirname(os.path.abspath(__file__))
    
    # Połącz ścieżkę katalogu z nazwą pliku
    return os.path.join(biezacy_katalog, nazwa_pliku)


background_image = resource_path('assets/images/b.jpg')
settings_path = 'assets/settings/settings.json'
music_path = resource_path('assets/music/background_music.mp3')
savegame_path = resource_path('assets/player/savegame.json')
words_path = resource_path('assets/settings/words.json')
icon_path = resource_path('assets/images/ikonka.png')
savepoints_path = 'assets/player/points.json'

# Wszystkie stałe kolorów i inne zmienne globalne
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (52, 73, 94)
DARK_GRAY = (44, 62, 80)
LIGHT_GRAY = (200, 200, 200)
HOVER_COLOR = (100, 141, 181)

# Ładowanie ustawień z pliku
with open(settings_path, 'r') as f:
    settings = json.load(f)

class Text:
    def __init__(self, text, x, y, font_size=36, max_width=None):
        self.text = text
        self.x = x
        self.y = y
        self.font = pygame.font.Font(None, font_size)
        self.max_width = max_width

    def _wrap_text(self):
        words = self.text.split(' ')
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            width, _ = self.font.size(test_line)

            if self.max_width and width <= self.max_width or not current_line:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        
        lines.append(' '.join(current_line))
        return lines

    def display(self, screen):
        lines = [self.text] if not self.max_width else self._wrap_text()

        for i, line in enumerate(lines):
            text_surface_white = self.font.render(line, True, WHITE)
            text_surface_black = self.font.render(line, True, BLACK)
            
            offsets = [(-1, -1), (1, -1), (-1, 1), (1, 1), (0, -1), (0, 1), (-1, 0), (1, 0)]  # Przesunięcia dla poświaty
            
            y_position = self.y + i * self.font.get_height()

            # Rysowanie poświaty (czarny tekst)
            for offset_x, offset_y in offsets:
                screen.blit(text_surface_black, (self.x + offset_x, y_position + offset_y))

            # Rysowanie głównego tekstu (biały tekst)
            screen.blit(text_surface_white, (self.x, y_position))

    def get_text_width(self):
        """Zwraca szerokość tekstu bez zawijania."""
        width, _ = self.font.size(self.text)
        return width



class InputBox:
    def __init__(self, x, y, w, h, font_size=36):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = LIGHT_GRAY
        self.color_active = GRAY
        self.color = self.color_inactive
        self.text = ''
        self.font = pygame.font.Font(None, font_size)
        self.txt_surface_white = self.font.render(self.text, True, WHITE)
        self.txt_surface_black = self.font.render(self.text, True, BLACK)
        self.active = False

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            # Sprawdź czy myszka jest w obrębie prostokąta
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == KEYDOWN:
            if self.active:
                if event.key == K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Aktualizacja białego i czarnego tekstu
                self.txt_surface_white = self.font.render(self.text, True, WHITE)
                self.txt_surface_black = self.font.render(self.text, True, BLACK)

    def display(self, screen):
        # Rysuj tło
        pygame.draw.rect(screen, self.color, self.rect)
        # Rysuj poświatę (czarny tekst)
        offsets = [(-1, -1), (1, -1), (-1, 1), (1, 1), (0, -1), (0, 1), (-1, 0), (1, 0)]
        for offset_x, offset_y in offsets:
            screen.blit(self.txt_surface_black, (self.rect.x + 5 + offset_x, self.rect.y + 5 + offset_y))
        # Rysuj główny tekst (biały tekst)
        screen.blit(self.txt_surface_white, (self.rect.x + 5, self.rect.y + 5))
        # Rysuj obramowanie prostokąta
        pygame.draw.rect(screen, BLACK, self.rect, 2)

class Button:
    def __init__(self, text, x, y, width, height, action=None):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.action = action
        self.color = GRAY
        self.hover_color = HOVER_COLOR  # Dodaj ciemniejszy kolor dla efektu hover
        self.font = pygame.font.Font(None, 36)
        self.hover = False
        self.radius = 10  # Zaokrąglenie rogu
        self.pressed = False  # Nowy atrybut do przechowywania stanu przycisku

    def display(self, screen):
        if self.hover:
            color = self.hover_color
        else:
            color = self.color
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height), border_radius=self.radius)
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        # Sprawdzanie, czy mysz jest nad przyciskiem
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if self.x <= mouse_x <= self.x + self.width and self.y <= mouse_y <= self.y + self.height:
            self.hover = True
            if event.type == MOUSEBUTTONDOWN:
                self.pressed = True  # Aktualizacja stanu przycisku
                if self.action:
                    self.action()
            elif event.type == MOUSEBUTTONUP:
                self.pressed = False
        else:
            self.hover = False
            self.pressed = False  

def save_settings():
    """Zapisuje ustawienia do pliku settings.json."""
    with open(settings_path, 'w') as f:
        json.dump(settings, f, indent=4)

class Slider:
    def __init__(self, x, y, width, min_val, max_val, value):
        self.x = x
        self.y = y
        self.width = width
        self.min = min_val
        self.max = max_val
        self.value = value
        self.dragging = False
        self.thumb_radius = 15
        self.font = pygame.font.Font(None, 32)
        self.update_thumb_pos_from_value()

    def draw_text_with_shadow(self, screen, text, position):
        text_surface = self.font.render(text, True, BLACK)  # Poświata (cienie)
        x, y = position
        shadow_positions = [(x-1, y-1), (x+1, y-1), (x-1, y+1), (x+1, y+1)]
        for shadow_pos in shadow_positions:
            screen.blit(text_surface, shadow_pos)

        text_surface = self.font.render(text, True, WHITE)  # Główny tekst
        screen.blit(text_surface, position)

    def display(self, screen):
        # Rysowanie linii
        pygame.draw.line(screen, WHITE, (self.x, self.y), (self.x + self.width, self.y), 3)
        pygame.draw.circle(screen, HOVER_COLOR if self.dragging else GRAY, (int(self.thumb_pos), self.y), self.thumb_radius)

        # Wyświetlanie wartości pod suwakiem
        value_text = str(self.value)
        text_width, text_height = self.font.size(value_text)
        value_position = (self.x + self.width // 2 - text_width // 2, self.y + self.thumb_radius + 5)
        self.draw_text_with_shadow(screen, value_text, value_position)

    def update_thumb_pos_from_value(self):
        """Aktualizuje pozycję kciuka na podstawie wartości suwaka."""
        self.thumb_pos = self.x + (self.value - self.min) * self.width / (self.max - self.min)

    def handle_event(self, event):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        distance_to_thumb = abs(mouse_x - self.thumb_pos)
        if event.type == MOUSEBUTTONDOWN:
            if distance_to_thumb <= self.thumb_radius and self.y - self.thumb_radius <= mouse_y <= self.y + self.thumb_radius:
                self.dragging = True
        elif event.type == MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == MOUSEMOTION and self.dragging:
            self.thumb_pos = min(max(mouse_x, self.x), self.x + self.width)
            self.value = self.min + (self.thumb_pos - self.x) * (self.max - self.min) / self.width

            # Zaokrąglamy wartość do najbliższej wartości o kroku 0.1
            self.value = round(self.value, 1)
            self.update_thumb_pos_from_value()

            settings['music_volume'] = self.value
            pygame.mixer.music.set_volume(self.value)

            save_settings()




class CheckBox:
    def __init__(self, x, y, checked):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.checked = checked
        self.font = pygame.font.Font(None, 32)

    def draw_text_with_shadow(self, screen, text, position):
        text_surface = self.font.render(text, True, BLACK)  # Poświata (cienie)
        x, y = position
        shadow_positions = [(x-1, y-1), (x+1, y-1), (x-1, y+1), (x+1, y+1)]
        for shadow_pos in shadow_positions:
            screen.blit(text_surface, shadow_pos)

        text_surface = self.font.render(text, True, WHITE)  # Główny tekst
        screen.blit(text_surface, position)

    def display(self, screen):
        pygame.draw.rect(screen, DARK_GRAY, (self.x, self.y, self.width, self.height), border_radius=5)
        
        if self.checked:
            checkmark_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.line(checkmark_surface, WHITE, (10, 20), (15, 30), 4)
            pygame.draw.line(checkmark_surface, WHITE, (15, 30), (30, 10), 4)
            screen.blit(checkmark_surface, (self.x, self.y))

        text = "Tak" if self.checked else "Nie"
        text_width, text_height = self.font.size(text)
        self.draw_text_with_shadow(screen, text, (self.x - text_width - 10, self.y + (self.height - text_height) // 2))

    def handle_event(self, event):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if event.type == MOUSEBUTTONDOWN and self.x <= mouse_x <= self.x + self.width and self.y <= mouse_y <= self.y + self.height:
            self.checked = not self.checked
            settings['music_on'] = self.checked
            save_settings()  # Zapisujemy ustawienia po zmianie checkboxa

            if self.checked:
                pygame.mixer.music.unpause()
            else:
                pygame.mixer.music.pause()

class Hangman:
    def __init__(self, word, hints):
        self.word = word.upper()
        self.guesses = ["_"] * len(word)
        self.attempts = 10
        self.hints = hints
        self.used_hints = 0  # Liczba użytych podpowiedzi
        self.game_ended = False
        
        # Jeśli w słowie jest spacja, zalicz ją od razu
        for i, char in enumerate(self.word):
            if char == " ":
                self.guesses[i] = " "

    def guess(self, letter):
        if letter in self.word:
            for i in range(len(self.word)):
                if self.word[i] == letter:
                    self.guesses[i] = letter
            return True
        else:
            self.attempts -= 1
            return False

    def is_complete(self):
        return "_" not in self.guesses

    def get_display_word(self):
        return ' '.join(self.guesses)

    def get_attempts_left(self):
        return self.attempts

    def use_hint(self):
        """Zwraca podpowiedź na podstawie liczby użytych podpowiedzi."""
        if self.used_hints < len(self.hints):
            hint = self.hints[self.used_hints]
            self.used_hints += 1
            return hint
        else:
            return "Użyto wskazówek!"
        
    def draw_hangman(self, surface):
        mistakes = 10 - self.attempts
        start_x = 100
        start_y = 100

        # Drawing the base of the gallows
        if mistakes >= 1:
            pygame.draw.line(surface, BLACK, (start_x, start_y + 300), (start_x + 200, start_y + 300), 5)  # bottom horizontal
        if mistakes >= 2:
            pygame.draw.line(surface, BLACK, (start_x + 100, start_y), (start_x + 100, start_y + 300), 5)  # vertical
        if mistakes >= 3:
            pygame.draw.line(surface, BLACK, (start_x, start_y), (start_x + 100, start_y), 5)  # top horizontal
        if mistakes >= 4:
            pygame.draw.line(surface, BLACK, (start_x, start_y), (start_x, start_y + 80), 5)  # vertical line from the beam (rope)

        # Drawing the hanged man
        if mistakes >= 5:
            pygame.draw.circle(surface, BLACK, (start_x, start_y + 120), 40, 3)  # head
        if mistakes >= 6:
            pygame.draw.line(surface, BLACK, (start_x, start_y + 160), (start_x, start_y + 250), 3)  # body
        if mistakes >= 7:
            pygame.draw.line(surface, BLACK, (start_x, start_y + 170), (start_x - 50, start_y + 210), 3)  # left arm
        if mistakes >= 8:
            pygame.draw.line(surface, BLACK, (start_x, start_y + 170), (start_x + 50, start_y + 210), 3)  # right arm
        if mistakes >= 9:
            pygame.draw.line(surface, BLACK, (start_x, start_y + 250), (start_x - 50, start_y + 290), 3)  # left leg
        if mistakes >= 10:
            pygame.draw.line(surface, BLACK, (start_x, start_y + 250), (start_x + 50, start_y + 290), 3)  # right leg

    def end_game(self):
        # Jeśli gra została już zakończona wcześniej, zwróć aktualną różnicę punktacji
        if self.game_ended:
            return self.score_difference

        if self.is_complete():
            win = True
        else:
            win = False
            
        mistakes = 10 - self.attempts
        guessed_percent = self.get_guessed_percent()

        # Liczymy różnicę punktacji
        if win:
            self.score_difference = round(100 - (mistakes * 10))
        else:
            self.score_difference = round(-(100 - guessed_percent))

        current_score = self.load_points()
        
        # Zastosuj ograniczenie tylko podczas zapisywania punktów do pliku
        new_score = current_score + self.score_difference
        if new_score < 0:
            new_score = 0
        
        self.save_points(new_score)
        self.game_ended = True  # Ustawiamy flagę, że gra została zakończona

        return self.score_difference  # Zwracamy faktyczną różnicę punktacji, a nie to, co zostało zapisane




    
    def load_points(self):
        if os.path.exists(savepoints_path):
            with open(savepoints_path, 'r') as f:
                points = json.load(f)
                return points['score']
        return 0

    def save_points(self, points):
        with open(savepoints_path, 'w') as f:
            json.dump({'score': points}, f, indent=4)


    def update_score(self, win, mistakes, guessed_percent):
        current_score = self.load_points()

        if win:
            score_to_add = 100 - (mistakes * 10)
            current_score += score_to_add
        else:
            # Oblicz ile punktów należy odjąć od aktualnego wyniku
            score_to_remove = 100 - int(guessed_percent)
            current_score -= score_to_remove
            current_score = max(current_score, 0)  # Zapewnia, że wynik nie będzie ujemny

        self.save_points(current_score)
        return current_score

    
    def get_guessed_percent(self):
        total_chars = len([ch for ch in self.word if ch != ' '])  # Nie liczymy spacji
        guessed_chars = self.guesses.count("_")
        return round(((total_chars - guessed_chars) / total_chars) * 100)  # Używamy funkcji int() tutaj