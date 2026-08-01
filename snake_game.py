#  my github -----------> "MOHAMAD88AZ"
# .
# .
# .
# .
# .
# .
# .
# " A classic Snake game built for fun. Play with your friends and enjoy your free time! "
import pygame
import random
import sys
from enum import Enum
from collections import deque

pygame.init()
pygame.mixer.init()

WINDOW_SIZE = 800
GRID_SIZE = 20
GRID_COUNT = WINDOW_SIZE // GRID_SIZE

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (40, 40, 40)
DARK_GRAY = (22, 22, 22)
LIGHT_GRAY = (170, 170, 170)

SNAKE1_COLOR = (0, 220, 80)
SNAKE2_COLOR = (50, 150, 255)
HUNTER_COLOR = (220, 50, 50)
FOOD_COLOR = (255, 200, 40)
POWER_COLOR = (180, 80, 255)

SPEEDS = [3,6,9,11,14,17,20]  # frames    


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class Snake:
    def __init__(self, body, direction, color, controls=None, is_hunter=False):
        self.body = body[:]
        self.direction = direction
        self.next_direction = direction
        self.color = color
        self.controls = controls or {}
        self.alive = True
        self.score = 0
        self.is_hunter = is_hunter
        self.invincible = 0          # frames left
        self.speed_boost = 0

    def handle_key(self, key):
        if key not in self.controls:
            return
        new_dir = self.controls[key]
        opposite = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
        }
        if new_dir != opposite.get(self.direction):
            self.next_direction = new_dir

    def move(self, grow=False):
        if not self.alive:
            return
        self.direction = self.next_direction
        hx, hy = self.body[0]
        if self.direction == Direction.UP:
            new_head = (hx, hy - 1)
        elif self.direction == Direction.DOWN:
            new_head = (hx, hy + 1)
        elif self.direction == Direction.LEFT:
            new_head = (hx - 1, hy)
        else:
            new_head = (hx + 1, hy)

        self.body.insert(0, new_head)
        if not grow:
            self.body.pop()

        if self.invincible > 0:
            self.invincible -= 1
        if self.speed_boost > 0:
            self.speed_boost -= 1

    def check_collision(self, other_bodies, ignore_self=False):
        head = self.body[0]
        if not (0 <= head[0] < GRID_COUNT and 0 <= head[1] < GRID_COUNT):
            return True
        if not ignore_self and head in self.body[1:]:
            return True
        for body in other_bodies:
            if head in body:
                return True
        return False


class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 26)
        self.big_font = pygame.font.SysFont("consolas", 46)
        self.small_font = pygame.font.SysFont("consolas", 20)

        self.speed_index = 1
        self.speed = SPEEDS[self.speed_index]
        self.sound_on = True
        self.eat_sound = self._make_beep(880)
        self.power_sound = self._make_beep(1200)
        self.die_sound = self._make_beep(200, 0.15)

        # settings that player chooses
        self.mode = "1p"                 # 1p / 2p
        self.hunters_enabled = False
        self.hunter_count = 1            
        self.difficulty = 1              # 0 easy, 1 medium, 2 hard

        self.state = "menu"               # menu / options / playing / paused / gameover
        self.selected = 0
        self.option_page = 0             #  multi-step options

        self.menu_options = ["1 Player", "2 Players", "Quit"]
        self.pause_options = ["Resume", "Speed", "Sound", "Quit to Menu"]

        self.snakes = []
        self.hunters = []
        self.food = None
        self.power = None                # (x, y, type)
        self.power_timer = 0
        self.high_score = 0
        self.frame = 0

    def _make_beep(self, freq=880, duration=0.07):
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        buf = bytearray()
        for i in range(n_samples):
            t = i / sample_rate
            val = int(90 * (1 if int(t * freq * 2) % 2 == 0 else -1) * (1 - t / duration))
            buf.append(max(0, min(255, val + 128)))
        s = pygame.mixer.Sound(buffer=bytes(buf))
        s.set_volume(0.22)
        return s

    # menu / options ----------> github ------> MOHAMAD88AZ
    def start_options(self, mode):
        self.mode = mode
        self.state = "options"
        self.option_page = 0
        self.selected = 0
        self.hunters_enabled = False
        self.hunter_count = 1
        self.difficulty = 1

    def apply_and_start(self):
        self.state = "playing"
        self.selected = 0
        self.frame = 0
        self.power = None
        self.power_timer = 0
        self._spawn_snakes()
        self.food = self.generate_food()

    def _spawn_snakes(self):
        p1_controls = {
            pygame.K_UP: Direction.UP,
            pygame.K_DOWN: Direction.DOWN,
            pygame.K_LEFT: Direction.LEFT,
            pygame.K_RIGHT: Direction.RIGHT,
        }

        if self.mode == "1p":
            s1 = Snake([(GRID_COUNT//2, GRID_COUNT//2)], Direction.RIGHT, SNAKE1_COLOR, p1_controls)
            self.snakes = [s1]
        else:
            s1 = Snake([(GRID_COUNT//3, GRID_COUNT//2)], Direction.RIGHT, SNAKE1_COLOR, p1_controls)
            p2_controls = {
                pygame.K_w: Direction.UP,
                pygame.K_s: Direction.DOWN,
                pygame.K_a: Direction.LEFT,
                pygame.K_d: Direction.RIGHT,
            }
            s2 = Snake([(2*GRID_COUNT//3, GRID_COUNT//2)], Direction.LEFT, SNAKE2_COLOR, p2_controls)
            self.snakes = [s1, s2]

        self.hunters = []
        if self.hunters_enabled:
            corners = [(2, 2), (GRID_COUNT-3, 2), (2, GRID_COUNT-3), (GRID_COUNT-3, GRID_COUNT-3)]
            random.shuffle(corners)
            for i in range(self.hunter_count):
                pos = corners[i % len(corners)]
                h = Snake([pos], Direction.RIGHT, HUNTER_COLOR, is_hunter=True)
                # hunters start a bit longer
                for _ in range(3):
                    h.body.append(h.body[-1])
                self.hunters.append(h)

    # ------- food & power ----------
    def generate_food(self):
        occupied = set()
        for s in self.snakes + self.hunters:
            occupied.update(s.body)
        if self.power:
            occupied.add((self.power[0], self.power[1]))
        while True:
            pos = (random.randint(0, GRID_COUNT-1), random.randint(0, GRID_COUNT-1))
            if pos not in occupied:
                return pos

    def maybe_spawn_power(self):
        if self.power or random.random() > 0.012:
            return
        occupied = set()
        for s in self.snakes + self.hunters:
            occupied.update(s.body)
        occupied.add(self.food)
        for _ in range(30):
            pos = (random.randint(1, GRID_COUNT-2), random.randint(1, GRID_COUNT-2))
            if pos not in occupied:
                ptype = random.choice(["invincible", "boost", "score", "shrink"])
                self.power = (pos[0], pos[1], ptype)
                self.power_timer = 180   # frames until disappears
                break

    # ---------- AI for hunters ----------github @MOHAMAD88AZ
    def hunter_think(self, hunter):
        """Simple AI: move toward nearest living player, avoid walls a little."""
        if not hunter.alive:
            return
    
        targets = [s.body[0] for s in self.snakes if s.alive]
        if not targets:
            return
    
        hx, hy = hunter.body[0]
        tx, ty = min(targets, key=lambda t: abs(t[0]-hx) + abs(t[1]-hy))
    
        candidates = []
        for d, (dx, dy) in [
            (Direction.UP, (0, -1)),
            (Direction.DOWN, (0, 1)),
            (Direction.LEFT, (-1, 0)),
            (Direction.RIGHT, (1, 0)),
        ]:
            nx, ny = hx + dx, hy + dy
            if not (0 <= nx < GRID_COUNT and 0 <= ny < GRID_COUNT):
                continue
            if (nx, ny) in hunter.body[:-1]:
                continue
            dist = abs(nx - tx) + abs(ny - ty)
            noise = random.randint(0, 3 - self.difficulty)
            candidates.append((dist + noise, d))
    
        if candidates:
            candidates.sort(key=lambda x: x[0])
            hunter.next_direction = candidates[0][1]
    
    # --------- $input ----------
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type != pygame.KEYDOWN:
                continue
            key = event.key

            if self.state == "menu":
                if key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.menu_options)
                elif key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.menu_options)
                elif key == pygame.K_RETURN:
                    choice = self.menu_options[self.selected]
                    if choice == "1 Player":
                        self.start_options("1p")
                    elif choice == "2 Players":
                        self.start_options("2p")
                    else:
                        pygame.quit()
                        sys.exit()

            elif self.state == "options":
                self._handle_options_input(key)

            elif self.state == "paused":
                if key in (pygame.K_UP, pygame.K_w):
                    self.selected = (self.selected - 1) % len(self.pause_options)
                elif key in (pygame.K_DOWN, pygame.K_s):
                    self.selected = (self.selected + 1) % len(self.pause_options)
                elif key == pygame.K_RETURN:
                    self._pause_action()
                elif key in (pygame.K_ESCAPE, pygame.K_p):
                    self.state = "playing"

            elif self.state == "gameover":
                if key == pygame.K_r:
                    self.apply_and_start()
                elif key in (pygame.K_ESCAPE, pygame.K_m):
                    self.state = "menu"
                    self.selected = 0
                elif key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

            elif self.state == "playing":
                if key in (pygame.K_p, pygame.K_ESCAPE):
                    self.state = "paused"
                    self.selected = 0
                    continue
                for s in self.snakes:
                    if s.alive:
                        s.handle_key(key)

    def _handle_options_input(self, key):
        if self.option_page == 0:  # hunter yes/no
            opts = ["No Hunters", "Yes, add Hunters", "Back"]
            if key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % 3
            elif key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % 3
            elif key == pygame.K_RETURN:
                if self.selected == 0:
                    self.hunters_enabled = False
                    self.option_page = 2   # skip to difficulty
                    self.selected = 1
                elif self.selected == 1:
                    self.hunters_enabled = True
                    self.option_page = 1
                    self.selected = 0
                else:
                    self.state = "menu"
                    self.selected = 0

        elif self.option_page == 1:  # how many hunters
            opts = ["1 Hunter", "2 Hunters", "3 Hunters", "Back"]
            if key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % 4
            elif key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % 4
            elif key == pygame.K_RETURN:
                if self.selected == 3:
                    self.option_page = 0
                    self.selected = 1
                else:
                    self.hunter_count = self.selected + 1
                    self.option_page = 2
                    self.selected = 1

        elif self.option_page == 2:  # difficulty
            opts = ["Easy", "Medium", "Hard", "Back"]
            if key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % 4
            elif key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % 4
            elif key == pygame.K_RETURN:
                if self.selected == 3:
                    if self.hunters_enabled:
                        self.option_page = 1
                    else:
                        self.option_page = 0
                    self.selected = 0
                else:
                    self.difficulty = self.selected
                    self.apply_and_start()

    def _pause_action(self):
        opt = self.pause_options[self.selected]
        if opt == "Resume":
            self.state = "playing"
        elif opt == "Speed":
            self.speed_index = (self.speed_index + 1) % len(SPEEDS)
            self.speed = SPEEDS[self.speed_index]
        elif opt == "Sound":
            self.sound_on = not self.sound_on
        elif opt == "Quit to Menu":
            self.state = "menu"
            self.selected = 0

    def update(self):
        if self.state != "playing":
            return

        self.frame += 1

        # hunters think & move (hunters move a bit slower on easy)
        hunter_move = True
        if self.difficulty == 0 and self.frame % 2 == 0:
            hunter_move = False
        elif self.difficulty == 2 and self.frame % 3 != 0:
            # hard: almost every frame + sometimes extra aggressive
            pass

        if hunter_move:
            for h in self.hunters:
                if h.alive:
                    self.hunter_think(h)
                    h.move(grow=False)

        # player snakes
        for snake in self.snakes:
            if not snake.alive:
                continue

            # speed boost = move extra step sometimes
            extra = snake.speed_boost > 0 and self.frame % 2 == 0

            hx, hy = snake.body[0]
            dx = dy = 0
            d = snake.next_direction
            if d == Direction.UP: dy = -1
            elif d == Direction.DOWN: dy = 1
            elif d == Direction.LEFT: dx = -1
            else: dx = 1
            next_pos = (hx + dx, hy + dy)

            grow = next_pos == self.food
            snake.move(grow=grow)

            if grow:
                snake.score += 1
                if self.sound_on:
                    self.eat_sound.play()
                self.food = self.generate_food()
                if self.mode == "1p" and snake.score > self.high_score:
                    self.high_score = snake.score

            # power-up
            if self.power and next_pos == (self.power[0], self.power[1]):
                self._apply_power(snake, self.power[2])
                self.power = None
                if self.sound_on:
                    self.power_sound.play()

            if extra:
                # second move for boost
                snake.move(grow=False)

        # github ------> MOHAMAD88AZ
        if self.power:
            self.power_timer -= 1
            if self.power_timer <= 0:
                self.power = None
        else:
            self.maybe_spawn_power()

        # collisions
        all_bodies = []
        for s in self.snakes + self.hunters:
            if s.alive:
                all_bodies.append(s.body)

        for i, snake in enumerate(self.snakes):
            if not snake.alive or snake.invincible > 0:
                continue
            others = [b for j, b in enumerate(all_bodies) if b is not snake.body]
            if snake.check_collision(others):
                snake.alive = False
                if self.sound_on:
                    self.die_sound.play()

        for h in self.hunters:
            if not h.alive:
                continue
            # hunters die if they hit walls or themselves, but not players (they kill players)
            if h.check_collision([], ignore_self=False):
                h.alive = False

        # end
        alive_players = sum(1 for s in self.snakes if s.alive)
        if alive_players == 0:
            self.state = "gameover"
        elif self.mode == "2p" and alive_players == 1:
            self.state = "gameover"

    def _apply_power(self, snake, ptype):
        if ptype == "invincible":
            snake.invincible = 90
        elif ptype == "boost":
            snake.speed_boost = 100
        elif ptype == "score":
            snake.score += 5
        elif ptype == "shrink":
            if len(snake.body) > 4:
                snake.body = snake.body[:max(3, len(snake.body)//2)]

    #  draw 
    def draw(self):
        self.screen.fill(BLACK)

        if self.state == "menu":
            self.draw_main_menu()
        elif self.state == "options":
            self.draw_options()
        else:
            self.draw_game()
            if self.state == "paused":
                self.draw_pause()
            elif self.state == "gameover":
                self.draw_gameover()

        pygame.display.flip()

    def draw_main_menu(self):
        title = self.big_font.render("SNAKE", True, WHITE)
        self.screen.blit(title, title.get_rect(centerx=WINDOW_SIZE//2, y=160))

        for i, opt in enumerate(self.menu_options):
            color = (100, 255, 130) if i == self.selected else WHITE
            text = self.font.render(opt, True, color)
            rect = text.get_rect(centerx=WINDOW_SIZE//2, y=300 + i*55)
            if i == self.selected:
                pygame.draw.rect(self.screen, (45, 45, 45), rect.inflate(36, 10), border_radius=6)
            self.screen.blit(text, rect)

        hint = self.small_font.render("↑↓  Move     Enter  Select", True, (120, 120, 120))
        self.screen.blit(hint, hint.get_rect(centerx=WINDOW_SIZE//2, y=WINDOW_SIZE-55))

    def draw_options(self):
        title = self.font.render("GAME OPTIONS", True, WHITE)
        self.screen.blit(title, title.get_rect(centerx=WINDOW_SIZE//2, y=120))

        if self.option_page == 0:
            opts = ["No Hunters", "Yes, add Hunters", "Back"]
            subtitle = "Include hunter snakes?"
        elif self.option_page == 1:
            opts = ["1 Hunter", "2 Hunters", "3 Hunters", "Back"]
            subtitle = "How many hunters?"
        else:
            opts = ["Easy", "Medium", "Hard", "Back"]
            subtitle = "Difficulty"

        sub = self.small_font.render(subtitle, True, LIGHT_GRAY)
        self.screen.blit(sub, sub.get_rect(centerx=WINDOW_SIZE//2, y=175))

        for i, opt in enumerate(opts):
            color = (110, 255, 140) if i == self.selected else WHITE
            text = self.font.render(opt, True, color)
            rect = text.get_rect(centerx=WINDOW_SIZE//2, y=240 + i*50)
            if i == self.selected:
                pygame.draw.rect(self.screen, (40, 40, 40), rect.inflate(30, 8), border_radius=5)
            self.screen.blit(text, rect)

    def draw_game(self):
        for i in range(GRID_COUNT+1):
            pygame.draw.line(self.screen, GRAY, (i*GRID_SIZE, 0), (i*GRID_SIZE, WINDOW_SIZE))
            pygame.draw.line(self.screen, GRAY, (0, i*GRID_SIZE), (WINDOW_SIZE, i*GRID_SIZE))

        # food
        fx, fy = self.food
        pygame.draw.rect(self.screen, FOOD_COLOR,
                         (fx*GRID_SIZE+2, fy*GRID_SIZE+2, GRID_SIZE-4, GRID_SIZE-4), border_radius=3)

        # power-up
        if self.power:
            px, py, ptype = self.power
            col = POWER_COLOR
            if ptype == "invincible":
                col = (100, 255, 255)
            elif ptype == "boost":
                col = (255, 180, 50)
            elif ptype == "score":
                col = (255, 80, 200)
            pygame.draw.rect(self.screen, col,
                             (px*GRID_SIZE+3, py*GRID_SIZE+3, GRID_SIZE-6, GRID_SIZE-6), border_radius=4)

        # hunters
        for h in self.hunters:
            if not h.alive:
                continue
            for i, (x, y) in enumerate(h.body):
                c = HUNTER_COLOR if i > 0 else tuple(min(255, c+40) for c in HUNTER_COLOR)
                pygame.draw.rect(self.screen, c,
                                 (x*GRID_SIZE+1, y*GRID_SIZE+1, GRID_SIZE-2, GRID_SIZE-2), border_radius=2)

        # players
        for snake in self.snakes:
            if not snake.alive:
                continue
            for i, (x, y) in enumerate(snake.body):
                c = snake.color
                if i == 0:
                    c = tuple(min(255, v+45) for v in snake.color)
                if snake.invincible > 0 and self.frame % 6 < 3:
                    c = (255, 255, 255)
                pygame.draw.rect(self.screen, c,
                                 (x*GRID_SIZE+1, y*GRID_SIZE+1, GRID_SIZE-2, GRID_SIZE-2), border_radius=2)

        # HUD
        if self.mode == "1p":
            s = self.snakes[0]
            t1 = self.font.render(f"Score: {s.score}", True, WHITE)
            t2 = self.font.render(f"High: {self.high_score}", True, LIGHT_GRAY)
            self.screen.blit(t1, (12, 8))
            self.screen.blit(t2, (12, 36))
        else:
            s1, s2 = self.snakes
            t1 = self.font.render(f"P1: {s1.score}", True, SNAKE1_COLOR)
            t2 = self.font.render(f"P2: {s2.score}", True, SNAKE2_COLOR)
            self.screen.blit(t1, (12, 8))
            self.screen.blit(t2, (WINDOW_SIZE - t2.get_width() - 12, 8))

        # 'difficulty' + 'hunters indicator'
        info = f"Diff: {['Easy','Med','Hard'][self.difficulty]}"
        if self.hunters_enabled:
            info += f"  |  Hunters: {sum(1 for h in self.hunters if h.alive)}/{self.hunter_count}"
        info_s = self.small_font.render(info, True, (110, 110, 110))
        self.screen.blit(info_s, (12, WINDOW_SIZE - 28))

        if self.mode == "2p":
            h1 = self.small_font.render("P1: Arrows", True, (90, 90, 90))
            h2 = self.small_font.render("P2: WASD", True, (90, 90, 90))
            self.screen.blit(h1, (WINDOW_SIZE//2 - 90, WINDOW_SIZE - 28))
            self.screen.blit(h2, (WINDOW_SIZE//2 + 20, WINDOW_SIZE - 28))

    def draw_pause(self):
        overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))
        overlay.set_alpha(165)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        bw, bh = 290, 260
        bx = (WINDOW_SIZE - bw) // 2
        by = (WINDOW_SIZE - bh) // 2
        pygame.draw.rect(self.screen, DARK_GRAY, (bx, by, bw, bh), border_radius=10)
        pygame.draw.rect(self.screen, (70, 70, 70), (bx, by, bw, bh), 2, border_radius=10)

        title = self.font.render("PAUSED", True, WHITE)
        self.screen.blit(title, title.get_rect(centerx=WINDOW_SIZE//2, y=by+18))

        for i, opt in enumerate(self.pause_options):
            y = by + 70 + i * 40
            label = opt
            if opt == "Speed":
                label = f"Speed: {self.speed}"
            elif opt == "Sound":
                label = f"Sound: {'On' if self.sound_on else 'Off'}"
            color = (120, 255, 140) if i == self.selected else WHITE
            if i == self.selected:
                pygame.draw.rect(self.screen, (48, 48, 48), (bx+22, y-4, bw-44, 32), border_radius=5)
            text = self.small_font.render(label, True, color)
            self.screen.blit(text, (bx+40, y))

    def draw_gameover(self):
        overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))
        overlay.set_alpha(155)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        if self.mode == "1p":
            msg = "GAME OVER"
            sub = f"Score: {self.snakes[0].score}"
        else:
            s1, s2 = self.snakes
            if s1.alive and not s2.alive:
                msg = "PLAYER 1 WINS"
            elif s2.alive and not s1.alive:
                msg = "PLAYER 2 WINS"
            else:
                if s1.score > s2.score:
                    msg = "PLAYER 1 WINS"
                elif s2.score > s1.score:
                    msg = "PLAYER 2 WINS"
                else:
                    msg = "DRAW"
            sub = f"P1 {s1.score}   -   P2 {s2.score}"

        title = self.big_font.render(msg, True, WHITE)
        score = self.font.render(sub, True, LIGHT_GRAY)
        tip = self.small_font.render("R Restart     M / ESC Menu", True, (130, 130, 130))

        self.screen.blit(title, title.get_rect(centerx=WINDOW_SIZE//2, y=WINDOW_SIZE//2-55))
        self.screen.blit(score, score.get_rect(centerx=WINDOW_SIZE//2, y=WINDOW_SIZE//2+10))
        self.screen.blit(tip, tip.get_rect(centerx=WINDOW_SIZE//2, y=WINDOW_SIZE//2+65))

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            tick = self.speed if self.state == "playing" else 30
            self.clock.tick(tick)


if __name__ == "__main__":
    game = SnakeGame()
    game.run()
