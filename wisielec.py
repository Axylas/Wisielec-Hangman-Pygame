import pygame
import json
from pygame.locals import *
import os
import sys
import random

from assets.inc.components import Slider, CheckBox, Text, Button, Hangman, InputBox

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

pygame.init()

# Rozmiary ekranu
WIDTH, HEIGHT = 920, 640
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wisielec")

# Kolory
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (52, 73, 94)
DARK_GRAY = (44, 62, 80)
LIGHT_GRAY = (200, 200, 200)
HOVER_COLOR = (100, 141, 181)

# Ustawienia ścieżek
background_image = resource_path('assets/images/b.jpg')
settings_path = resource_path('assets/settings/settings.json')
music_path = resource_path('assets/music/background_music.mp3')
savegame_path = resource_path('assets/player/savegame.json')
savepoints_path = resource_path('assets/player/points.json')
words_path = resource_path('assets/settings/words.json')
icon_path = resource_path('assets/images/ikonka.png')

# Ładowanie tła
bg_image = pygame.image.load(background_image)

# Ładowanie ikonki
icon = pygame.image.load(icon_path)
pygame.display.set_icon(icon)

# Ładowanie ustawień z pliku
with open(settings_path, 'r') as f:
    settings = json.load(f)

# Ustawienia muzyki na podstawie pliku settings.json
pygame.mixer.music.load(music_path)
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(settings['music_volume'])
if not settings['music_on']:
    pygame.mixer.music.pause()

screen = pygame.display.set_mode((WIDTH, HEIGHT))



        
class Menu:
    def __init__(self):
        if settings['first_start']:
            self.active_menu = 'name'
        else:
            self.active_menu = 'main'
        self.game = None  # Instancja klasy Hangman
        self.current_hint = ""
        self.selected_category = None

        self.version = Text("Wersja: 1.0", 820, 620, 16)
        self.author = Text("Autor: Krzysztof Ambroziak", 40, 620, 16)
        

        # Główne Menu
        self.start_game_button = Button("Rozpocznij Grę", 50, 200, 200, 50, action=self.start_game) 
        self.load_game_button = Button("Wczytaj", 50, 260, 200, 50, action=self.load_game)
        self.settings_button = Button("Ustawienia", 50, 320, 200, 50, action=self.settings)
        self.back_button = Button("Wstecz", 670, 540, 200, 50, action=self.draw_main_menu)
        self.points_button = Button(f"Punkty: {self.load_points()}", 560, 200, 250, 50)
        self.continue_button = Button("Kontynuuj", WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50, action=self.choose_category)
        self.greeting_text = Text(f"Witaj {settings['player_name']}!", 360, 50)
        self.text_width = self.greeting_text.get_text_width()
        self.button_width = self.text_width + 20
        self.centered_x = 920 // 2 - (self.button_width / 2)
        self.playername_button = Button(self.greeting_text.text, self.centered_x, 50, self.button_width, 50)

        # Ustawienia
        self.back_settings_button = Button("Wstecz", 670, 540, 200, 50, action=self.draw_main_menu)
        self.volume_slider = Slider(100, 350, 300, 0, 1, settings['music_volume'])
        self.music_checkbox = CheckBox(150, 170, settings['music_on'])
        self.settings_volume_text = Text("Głośność Muzyki", 100, 250)
        self.settings_music_text = Text("Włączyć Muzykę?", 100, 100)
        self.reset_points_button = Button("Resetuj Punkty", 100, 420, 200, 50, action=self.reset_points)
        self.reset_message_visible = False
        self.reset_message_timestamp = None
        self.reset_confirm_text = Text("Punkty zostały zresetowane", 100, 490)
        self.player_name_inputbox = InputBox(450, 150, 300, 40) 
        self.player_name_inputbox.text = settings['player_name']
        self.player_name_inputbox.txt_surface_white = self.player_name_inputbox.font.render(self.player_name_inputbox.text, True, WHITE)
        self.player_name_inputbox.txt_surface_black = self.player_name_inputbox.font.render(self.player_name_inputbox.text, True, BLACK)
        self.save_name_button = Button("Zapisz", 760, 150, 100, 40, action=self.save_player_name)
        self.save_message_visible = False
        self.save_message_timestamp = None
        self.save_confirm_text = Text("Zmieniono nazwę gracza", 450, 200)
        self.playername_text = Text("Nazwa Gracza:", 450, 100)
        self.first_text = Text("Witaj w grze w Wisielca!", 300, 50)
        self.second_text = Text("Jest to Twoje pierwsze uruchomienie gry, zmień nazwę gracza!", 160, 100, 28)
        self.player_name_inputbox_first = InputBox(300, 230, 300, 40)
        self.player_name_inputbox_first.text = settings['player_name']
        self.player_name_inputbox_first.txt_surface_white = self.player_name_inputbox_first.font.render(self.player_name_inputbox_first.text, True, WHITE)
        self.player_name_inputbox_first.txt_surface_black = self.player_name_inputbox_first.font.render(self.player_name_inputbox_first.text, True, BLACK)

        # Wybór Kategorii
        self.categories = {}  # Słownik kategorii wczytany z JSON
        

        # Gra
        self.hint_button = Button("Podpowiedź", 650, 50, 200, 50, action=self.show_hint)
        self.save_button = Button("Zapisz", 650, 110, 200, 50, action=self.save_game)
        self.load_words()  # Wczytanie słów
        self.back_save_button = Button("Wstecz", 670, 540, 200, 50, action=self.back_to_main)

    def save_exists(self):
        return os.path.exists(savegame_path)
    
    def back_to_main(self):
        self.save_game()
        self.draw_main_menu()

    def name(self):
        self.active_menu = 'name'
        self.playername_text.x = 360
        self.playername_text.y = 190
        self.playername_text.display(screen)
        self.player_name_inputbox_first.display(screen)
        self.save_name_button.action = self.save_player_name_first
        self.save_name_button.x = 620
        self.save_name_button.y = 230
        self.save_name_button.display(screen)
        self.first_text.display(screen)
        self.second_text.display(screen)

    def draw_main_menu(self):
        self.active_menu = 'main'
        self.start_game_button.display(screen)
        if self.save_exists():
            self.load_game_button.display(screen)
            self.settings_button.y = 320
        else:
            self.settings_button.y = 260
        self.settings_button.display(screen)
        self.points_button.display(screen)
        self.playername_button.display(screen)

        #final
        self.version.display(screen)
        self.author.display(screen)
        

    def settings(self):
        self.active_menu = 'settings'
        self.volume_slider.display(screen)
        self.music_checkbox.display(screen)
        self.back_settings_button.display(screen)
        self.settings_volume_text.display(screen)
        self.settings_music_text.display(screen)
        self.reset_points_button.display(screen)
        if self.reset_message_visible:
            current_time = pygame.time.get_ticks()  # Pobiera aktualny czas w milisekundach
            if current_time - self.reset_message_timestamp < 2000:  # Jeśli minęło mniej niż 2 sekund
                self.reset_confirm_text.display(screen)
            else:
                self.reset_message_visible = False

        self.playername_text.display(screen)
        self.player_name_inputbox.display(screen)
        self.save_name_button.display(screen)
        if self.save_message_visible:
            current_time = pygame.time.get_ticks()  # Pobiera aktualny czas w milisekundach
            if current_time - self.save_message_timestamp < 2000:  # Jeśli minęło mniej niż 2 sekund
                self.save_confirm_text.display(screen)
            else:
                self.save_message_visible = False

        #final
        self.version.display(screen)
        self.author.display(screen)

    def choose_category(self):
        self.active_menu = 'choose_category'
        
        # Tworzymy przyciski dla każdej kategorii
        self.category_buttons = []
        
        max_rows = 6
        max_cols = 3
        btn_width = 200
        btn_height = 50
        spacing_x = 20 # odstęp między przyciskami w poziomie
        spacing_y = 60 # odstęp między przyciskami w pionie

        start_x = (WIDTH - (max_cols * btn_width + (max_cols - 1) * spacing_x)) // 2
        start_y = 100

        col = 0
        row = 0

        for category in self.categories.keys():
            if row >= max_rows:
                row = 0
                col += 1
            if col >= max_cols:
                break

            x_position = start_x + col * (btn_width + spacing_x)
            y_position = start_y + row * spacing_y

            button = Button(category, x_position, y_position, btn_width, btn_height, action=lambda cat=category: self.start_category_game(cat))
            self.category_buttons.append(button)

            row += 1

        self.back_button.display(screen)

        #final
        self.version.display(screen)
        self.author.display(screen)



    def draw_win_screen(self):
        self.active_menu = 'win'
        win_text = Text(f"Brawo! Odgadnięto słowo {self.game.word}", WIDTH // 2 - 200, HEIGHT // 2 - 100)
        win_text.display(screen)
        self.back_button.display(screen)
        self.current_hint = ""
        self.continue_button.display(screen)

        score_difference = self.game.end_game()
        updated_score_text = Text(f"Zdobyte punkty: +{score_difference}", WIDTH // 2 - 120, HEIGHT // 2 + 20)
        updated_score_text.display(screen)
        self.points_button.text = f"Punkty: {self.load_points()}"

        #final
        self.version.display(screen)
        self.author.display(screen)

        
        
    def draw_lose_screen(self):
        self.active_menu = 'lose'
        lose_text = Text(f"Przegrana! Prawidłowe słowo to: {self.game.word}", WIDTH // 2 - 180, HEIGHT // 2 - 50, max_width=470)
        lose_text.display(screen)
        self.back_button.display(screen)
        self.current_hint = ""
        self.continue_button.display(screen)
        self.points_button.text = f"Punkty: {self.load_points()}"

        score_difference = self.game.end_game()
        updated_score_text = Text(f"Stracone punkty: {score_difference}", WIDTH // 2 - 120, HEIGHT // 2 + 20)
        updated_score_text.display(screen)

        #final
        self.version.display(screen)
        self.author.display(screen)

    def start_game(self):
        self.choose_category()

    def start_category_game(self, category):
        self.active_menu = 'game'
        
        # Wybieramy losowe słowo z wybranej kategorii
        word, hints = random.choice(list(self.categories[category].items()))
        self.game = Hangman(word, hints)
        self.selected_category = category  # Zapisujemy wybraną kategorię
        


        #final
        self.version.display(screen)
        self.author.display(screen)

    def display(self):
        if self.active_menu == 'main':
            self.draw_main_menu()
        elif self.active_menu == 'name':
            self.name()
        elif self.active_menu == 'settings':
            self.settings()
        elif self.active_menu == 'game':
            # Tutaj dodaj kod wyświetlający słowo, próby itp.
            word_display = Text(self.game.get_display_word(), WIDTH // 2 - 50, HEIGHT // 2)
            word_display.display(screen)
            
            attempts_display = Text(f"Pozostałe próby: {self.game.get_attempts_left()}", WIDTH // 2 - 50, HEIGHT // 2 + 50)
            attempts_display.display(screen)
            
            # Wyświetlanie aktualnej podpowiedzi pod "Pozostałe próby"
            hint_display = Text(f"Podpowiedź: {self.current_hint}", WIDTH // 2 - 50, HEIGHT // 2 + 100, max_width=450)
            hint_display.display(screen)

            # Wyświetlanie przycisków w menu gry
            self.hint_button.display(screen)
            self.save_button.display(screen)
            self.back_save_button.display(screen)

            self.game.draw_hangman(screen)  # rysowanie szubienicy i wisielca

            self.show_category = Text(f"Kategoria: {self.selected_category}", 290, 50)
            self.show_category.display(screen)

            #final
            self.version.display(screen)
            self.author.display(screen)
        elif self.active_menu == 'choose_category':
            for button in self.category_buttons:
                button.display(screen)
            self.back_button.display(screen)
            #final
            self.version.display(screen)
            self.author.display(screen)
        elif self.active_menu == 'win':
            self.draw_win_screen()
        elif self.active_menu == 'lose':
            self.draw_lose_screen()
            self.game.draw_hangman(screen)  # rysowanie szubienicy i wisielca

    def handle_event(self, event):
        if self.active_menu == 'main':
            self.start_game_button.handle_event(event)
            if self.save_exists():
                self.load_game_button.handle_event(event)
                self.settings_button.handle_event(event)
            else:
                self.settings_button.handle_event(event)
            self.points_button.handle_event(event)
        elif self.active_menu == 'settings':
            self.back_settings_button.handle_event(event)
            self.volume_slider.handle_event(event)
            self.music_checkbox.handle_event(event)
            self.reset_points_button.handle_event(event)
            self.player_name_inputbox.handle_event(event)
            self.save_name_button.handle_event(event)
        elif self.active_menu == 'game':
            # Tutaj dodaj logikę zgadywania liter
            if event.type == KEYDOWN:
                letter_to_guess = event.unicode.upper()

                if letter_to_guess:
                    if self.game.guess(letter_to_guess):
                        print("Dobrze!")
                    else:
                        print("Źle!")

                # Sprawdzamy, czy gra się zakończyła
                if self.game.is_complete():
                    self.draw_win_screen()
                    self.back_button.handle_event(event)
                    if self.save_exists():
                        os.remove(savegame_path)
                elif self.game.get_attempts_left() == 0:
                    self.draw_lose_screen()
                    self.back_button.handle_event(event)
                    if self.save_exists():
                        os.remove(savegame_path)
            
            # Obsługa zdarzeń przycisków w menu gry
            self.hint_button.handle_event(event)
            self.save_button.handle_event(event)
            self.back_save_button.handle_event(event)
        elif self.active_menu == 'choose_category':
            for button in self.category_buttons:
                button.handle_event(event)
            self.back_button.handle_event(event)
        elif self.active_menu == 'win':
            self.back_button.handle_event(event)
            self.continue_button.handle_event(event)
        elif self.active_menu == 'lose':
            self.back_button.handle_event(event)
            self.continue_button.handle_event(event)
        elif self.active_menu == 'name':
            self.player_name_inputbox_first.handle_event(event)
            self.save_name_button.handle_event(event)

    def load_words(self):
        with open(words_path, 'r', encoding='utf-8') as f:
            self.categories = json.load(f)

    def save_game(self):
        """Zapisuje stan gry do pliku JSON."""
        save_data = {
            "category": self.selected_category,  # Zapisujemy wybraną kategorię
            "word": self.game.word,
            "guesses": self.game.guesses,
            "attempts": self.game.attempts,
            "used_hints": self.game.used_hints,
        }
        with open(savegame_path, 'w') as f:
            json.dump(save_data, f)
        self.current_hint = ""

    def load_game(self):
        """Wczytuje stan gry z pliku JSON."""
        try:
            with open(savegame_path, 'r') as f:
                save_data = json.load(f)
            
            # Wczytywanie kategorii i ustawianie jako aktualnie wybranej
            self.selected_category = save_data["category"]
            
            word = save_data["word"]
            hints = self.categories[self.selected_category][word.capitalize()]  # Wczytywanie podpowiedzi na podstawie słowa i kategorii
            self.game = Hangman(word, hints)
            self.game.guesses = save_data["guesses"]
            self.game.attempts = save_data["attempts"]
            self.game.used_hints = save_data["used_hints"]
            
            # Usuwanie zapisu gry po wczytaniu
            os.remove(savegame_path)

            # Przejście do ekranu gry po wczytaniu zapisu
            self.active_menu = 'game'
            
        except FileNotFoundError:
            print("Brak zapisanej gry.")

    def show_hint(self):
        """Wyświetla podpowiedź dla gracza."""
        hint = self.game.use_hint()
        self.current_hint = hint  # Ustawiamy aktualną podpowiedź

    def load_points(self):
        if os.path.exists(savepoints_path):
            with open(savepoints_path, 'r') as f:
                points = json.load(f)
                return points['score']
        return 0

    def save_points(self, points):
        with open(savepoints_path, 'w') as f:
            json.dump({'score': points}, f, indent=4)

    def reset_points(self):
        self.save_points(0)
        self.points_button.text = f"Punkty: 0"
        self.reset_message_visible = True
        self.reset_message_timestamp = pygame.time.get_ticks()  # Ustawia czas w momencie resetowania punktów

    def save_player_name(self):
        settings['player_name'] = self.player_name_inputbox.text
        save_settings()
        self.player_name_inputbox.text = settings['player_name']
        self.save_message_visible = True
        self.save_message_timestamp = pygame.time.get_ticks()

        # Aktualizacja tekstu powitalnego
        self.greeting_text.text = f"Witaj {settings['player_name']}!"

        # Obliczenie nowej szerokości tekstu
        self.text_width = self.greeting_text.get_text_width()

        # Aktualizacja szerokości przycisku
        self.button_width = self.text_width + 20

        # Aktualizacja położenia przycisku, aby był wycentrowany
        self.centered_x = 920 // 2 - (self.button_width / 2)

        # Aktualizacja tekstu i położenia przycisku
        self.playername_button.text = self.greeting_text.text
        self.playername_button.x = self.centered_x
        self.playername_button.width = self.button_width

    def save_player_name_first(self):
        settings['player_name'] = self.player_name_inputbox_first.text
        settings['first_start'] = False
        save_settings()
        self.player_name_inputbox_first.text = settings['player_name']

        # Aktualizacja tekstu powitalnego
        self.greeting_text.text = f"Witaj {settings['player_name']}!"

        # Obliczenie nowej szerokości tekstu
        self.text_width = self.greeting_text.get_text_width()

        # Aktualizacja szerokości przycisku
        self.button_width = self.text_width + 20

        # Aktualizacja położenia przycisku, aby był wycentrowany
        self.centered_x = 920 // 2 - (self.button_width / 2)

        # Aktualizacja tekstu i położenia przycisku
        self.playername_button.text = self.greeting_text.text
        self.playername_button.x = self.centered_x
        self.playername_button.width = self.button_width
        self.playername_text.x = 450
        self.playername_text.y = 100
        self.save_name_button.x = 760
        self.save_name_button.y = 150
        self.save_name_button.action = self.save_player_name
        self.player_name_inputbox.text = settings['player_name']
        self.player_name_inputbox.txt_surface_white = self.player_name_inputbox.font.render(self.player_name_inputbox.text, True, WHITE)
        self.player_name_inputbox.txt_surface_black = self.player_name_inputbox.font.render(self.player_name_inputbox.text, True, BLACK)
        self.draw_main_menu()


def save_settings():
    """Zapisuje ustawienia do pliku settings.json."""
    with open(settings_path, 'w') as f:
        json.dump(settings, f, indent=4)

def main():
    running = True
    clock = pygame.time.Clock()
    menu = Menu()

    while running:
        win.blit(bg_image, (0, 0))

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            menu.handle_event(event)

        menu.display()
        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()

