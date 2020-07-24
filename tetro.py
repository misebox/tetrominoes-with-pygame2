import sys
import random
import math
import os
import getopt
import pygame
from socket import *
from pygame.locals import *


# config
cell_size = 40
bg_color = (30, 30, 30)
mino_color = (50, 50, 240)
bw = 1
cell_cols = 10
cell_rows = 20

shapes = [
    (
        (140, 200, 240),
        [
            "####",
        ]
    ),
    (
        (240, 240, 100),
        [
            "##",
            "##",
        ]
    ),
    (
        (140, 240, 140),
        [
            " ##",
            "## ",
        ],
    ),
    (
        (240, 40, 40),
        [
            "## ",
            " ##",
        ],
    ),
    (
        (50, 50, 200),
        [
            "#  ",
            "###",
        ],
    ),
    (
        (240, 200, 40),
        [
            "  #",
            "###",
        ],
    ),
    (
        (240, 100, 150),
        [
            " # ",
            "###",
        ],
    ),
]


class Blocks:
    color = (150, 150, 150)

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.points = set()

    @property
    def width(self):
        if self.points:
            return max([x for x, _ in self.points]) + 1
        else:
            return 0

    @property
    def height(self):
        if self.points:
            return max([y for _, y in self.points]) + 1 
        else:
            return 0

    def load(self, shape):
        points = set()
        for y, line in enumerate(shape):
            for x, ch in enumerate(line):
                if ch == "#":
                    points.add((x, y))
        self.points = points
    
    def draw(self, dx=0, dy=0):
        for x, y in self.points:
            px = self.x + dx + x
            py = self.y + dy + y
            pygame.draw.rect(screen, bg_color, (px*cell_size, py*cell_size, cell_size, cell_size))
            pygame.draw.rect(screen, self.color, (px*cell_size+bw, py*cell_size+bw, cell_size-bw, cell_size-bw))

class Wall(Blocks):
    color = (50, 50, 50)
    def __init__(self):
        super().__init__()
        for y in range(cell_rows):
            self.points.add((0, y))
            self.points.add((cell_cols+1, y))
        for x in range(cell_cols+2):
            self.points.add((x, cell_rows))


class Pile(Blocks):
    color = (150, 150, 150)

    def __init__(self):
        super().__init__()

    def add(self, mino):
        for x, y in mino.points:
            self.points.add((mino.x + x, mino.y + y))

    def clear_line(self):
        sh = [[' ' for _ in range(cell_cols)] for _ in range(cell_rows)] 
        for x, y in self.points:
            sh[y][x] = '#'

        targets = []
        for y, line in enumerate(sh):
            if line == ['#'] * cell_cols:
                targets.append(y)
        for y in reversed(targets):
            sh.pop(y)
        for _ in targets:
            sh.insert(0, [' ' for _ in range(cell_cols)])
        if targets:
            pile.load(sh)

    def draw(self):
        super().draw(1, 0)

class Mino(Blocks):
    color = mino_color
    def __init__(self, x, y):
        super().__init__(x, y)
        color, shape = random.choice(shapes)
        self.color = color
        self.load(shape)

    def _move(self, dx, dy):
        if not self.collide(dx, dy):
            self.x += dx
            self.y += dy
            return True
        return False

    def move_left(self):
        return self._move(-1, 0)

    def move_right(self):
        return self._move(1, 0)

    def move_down(self):
        return self._move(0, 1)

    def drop(self):
        while self.move_down():
            pass

    def _calc_rotate(self, reverse=False):
        points = set()
        for x, y in self.points:
            if reverse:
                px = y
                py = self.width - x - 1
            else:
                px = self.height - y - 1
                py = x
            points.add((px, py))
        return points

    def rotate_right(self, reverse=False):
        points = self._calc_rotate(reverse)
        dry = Mino(self.x, self.y)
        dry.points = points
        if not dry.collide():
            self.points = points

    def rotate_left(self):
        self.rotate_right(reverse=True)

    def _collide_with(self, other, px=0, py=0):
        points = set([(px + x, py + y)
                    for x, y in self.points])
        return (points & other.points) != set()

    def collide(self, dx=0, dy=0):
        px = self.x + dx
        py = self.y + dy
        return self._collide_with(wall, px+1, py) \
            or self._collide_with(pile, px, py)

    def draw(self):
        super().draw(1, 0)

def gameover():
    global pile
    pile = Pile()


def main():
    # Initialise screen
    pygame.init()
    global screen
    screen = pygame.display.set_mode((480, 840))
    pygame.display.set_caption('tetro')

    # Fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill(bg_color)

    # Blit everything to the screen
    screen.blit(background, (0, 0))
    pygame.display.flip()

    # Initialise clock
    clock = pygame.time.Clock()

    global wall, pile
    wall = Wall()
    pile = Pile()
    mino = Mino(5, 0)

    msec = 0
    interval = 1000
    # Event loop
    while 1:
        msec += clock.tick(60)
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                shift = event.mod == KMOD_SHIFT
                if event.key == K_ESCAPE:
                    return
                if event.key == K_SPACE:
                    mino.drop()
                if not mino:
                    continue
                if event.key in (K_LEFT, K_a, K_h):
                    mino.move_left()
                if event.key in (K_DOWN, K_s, K_j):
                    mino.move_down()
                if event.key in (K_RIGHT, K_d, K_l):
                    mino.move_right()
                if event.key in (K_r, K_UP, K_w, K_k) \
                or (shift and event.key in (K_e,)):
                    mino.rotate_right()
                if event.key in (K_e,) \
                or (shift and event.key in (K_UP, K_w, K_k)):
                    mino.rotate_left()
            elif event.type == KEYUP:
                if event.key == K_a or event.key == K_z:
                    pass
                if event.key == K_UP or event.key == K_DOWN:
                    pass
        
        if msec > interval:
            msec -= interval
            if mino:
                if mino.collide(0, 1):
                    pile.add(mino)
                    mino = Mino(5, 0)
                    if mino.collide(0, 0):
                        gameover()
                else:
                    mino.move_down()
            pile.clear_line()
        # clear
        screen.fill(bg_color)
        # drawing
        wall.draw()
        pile.draw()
        if mino:
            mino.draw()

        pygame.display.flip()

if __name__ == '__main__': main()
