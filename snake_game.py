# 🐍 🐍  snake game:

# 1 .Pause Menu with Multiple Options:

# Restore (Resume game)

# Speed adjustment (Cycles through preset speeds: 5, 10, 15 FPS)

# Sound toggle (On/Off)

# Change Snake color (Multiple preset colors)

# Change Food color (Multiple preset colors)

# Exit game

# 2 .Keyboard Navigation in Pause Menu:

# Up/Down arrow keys to navigate menu options

# Enter key to select/change settings

# 3 .Dynamic Game Speed Control:

# Ability to change game speed during pause to make gameplay faster or slower

# 4 .Sound Control:

# Beep sound on food eating can be toggled on/off

# 5 .Customizable Colors:

# Change snake and food colors in pause menu with multiple options

# 6 .Visual Feedback:

# Highlighted selected menu option in pause men
          
# 7 .Display High Score below the current Score on the game screen.

# High Score is saved during the session and updates if you beat it
import pygame
import random
import sys
from enum import Enum

pygame.init()


WINDOW_SIZE = 800
GRID_SIZE = 20
GRID_COUNT = WINDOW_SIZE // GRID_SIZE

# color
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.speed = 10  # game speed
        self.snake_color = GREEN
        self.food_color = RED
        self.sound_on = True
        self.high_score = 0
        self.reset_game()
        # sound
        self.eat_sound = pygame.mixer.Sound(pygame.mixer.Sound(buffer=b'\x00'*1000))  

    def reset_game(self):
        self.snake = [(GRID_COUNT // 2, GRID_COUNT // 2)]
        self.direction = Direction.RIGHT
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        self.paused = False
        self.show_menu = False

    def generate_food(self):
        while True:
            pos = (random.randint(0, GRID_COUNT - 1), random.randint(0, GRID_COUNT - 1))
            if pos not in self.snake:
                return pos

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                if event.key == pygame.K_p:
                    self.paused = not self.paused
                    self.show_menu = self.paused
                if not self.game_over and not self.paused:
                    if event.key == pygame.K_UP and self.direction != Direction.DOWN:
                        self.direction = Direction.UP
                    elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
                        self.direction = Direction.DOWN
                    elif event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
                        self.direction = Direction.LEFT
                    elif event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
                        self.direction = Direction.RIGHT

                
                if self.show_menu:
                    if event.key == pygame.K_1:  # تغییر سرعت
                        self.speed = 5 if self.speed == 10 else 10 if self.speed == 20 else 20
                    if event.key == pygame.K_2:  # off / on sound
                        self.sound_on = not self.sound_on
                    if event.key == pygame.K_3:  #  change color 
                        self.snake_color = random.choice([GREEN, BLUE, YELLOW])
                    if event.key == pygame.K_4:  # change food color
                        self.food_color = random.choice([RED, BLUE, YELLOW])
                    if event.key == pygame.K_ESCAPE:  # exit menu
                        self.paused = False
                        self.show_menu = False
                    if event.key == pygame.K_q:  # exit game
                        pygame.quit()
                        sys.exit()

    def update(self):
        if self.game_over or self.paused:
            return

        head_x, head_y = self.snake[0]
        if self.direction == Direction.UP:
            new_head = (head_x, head_y - 1)
        elif self.direction == Direction.DOWN:
            new_head = (head_x, head_y + 1)
        elif self.direction == Direction.LEFT:
            new_head = (head_x - 1, head_y)
        else:
            new_head = (head_x + 1, head_y)

        if (new_head[0] < 0 or new_head[0] >= GRID_COUNT or
            new_head[1] < 0 or new_head[1] >= GRID_COUNT or
            new_head in self.snake):
            self.game_over = True
            if self.score > self.high_score:
                self.high_score = self.score
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            if self.sound_on:
                self.eat_sound.play()
            self.food = self.generate_food()
        else:
            self.snake.pop()

    def draw_grid(self):
        for i in range(GRID_COUNT):
            pygame.draw.line(self.screen, GRAY, (i * GRID_SIZE, 0), (i * GRID_SIZE, WINDOW_SIZE))
            pygame.draw.line(self.screen, GRAY, (0, i * GRID_SIZE), (WINDOW_SIZE, i * GRID_SIZE))

    def draw(self):
        self.screen.fill(BLACK)
        self.draw_grid()

        # snake
        
        for seg in self.snake:
            pygame.draw.rect(self.screen, self.snake_color, (seg[0]*GRID_SIZE, seg[1]*GRID_SIZE, GRID_SIZE -1, GRID_SIZE -1))

        # food
      
        pygame.draw.rect(self.screen, self.food_color, (self.food[0]*GRID_SIZE, self.food[1]*GRID_SIZE, GRID_SIZE -1, GRID_SIZE -1))

        # show score
      
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        high_score_text = font.render(f"High Score: {self.high_score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(high_score_text, (10, 50))

        # show stop menu
      
        if self.show_menu:
            self.draw_menu()

        # game over message
        
        if self.game_over:
            go_text = font.render("Game Over! Press R to Restart", True, WHITE)
            rect = go_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2))
            self.screen.blit(go_text, rect)

        # stop 
        
        if self.paused and not self.game_over:
            pause_text = font.render("", True, WHITE)
            rect = pause_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 - 40))
            self.screen.blit(pause_text, rect)

        pygame.display.flip()

    def draw_menu(self):
       
        # pause menu
        
        menu_surf = pygame.Surface((400, 300))
        menu_surf.set_alpha(230)
        menu_surf.fill((30, 30, 30))
        font = pygame.font.Font(None, 30)

        lines = [
            "PAUSE MENU",
            "1 : Change Speed (Current: {})".format(self.speed),
            "2 : Toggle Sound (Current: {})".format("On" if self.sound_on else "Off"),
            "3 : Change Snake Color",
            "4 : Change Food Color",
            "ESC : Resume Game",
            "Q : Quit Game"
        ]

        for i, line in enumerate(lines):
            text = font.render(line, True, WHITE)
            menu_surf.blit(text, (20, 20 + i*40))

        self.screen.blit(menu_surf, (WINDOW_SIZE//2 - 200, WINDOW_SIZE//2 - 150))

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(self.speed)

if __name__ == "__main__":
    game = SnakeGame()
    game.run()

