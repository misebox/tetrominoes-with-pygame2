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

    def empty(self):
        return self.points == set()

    def load(self, shape):
        points = set()
        for y, line in enumerate(shape):
            for x, ch in enumerate(line):
                if ch == "#":
                    points.add((x, y))
        self.points = points

    @property
    def shape(self):
        a = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        for x, y in self.points:
            a[y][((x + self.width) % self.width)] = '#'
        return a

    def dump(self):
        for line in self.shape:
            print(''.join(line))


class Wall(Blocks):
    color = (50, 50, 50)
    def __init__(self, mediator):
        super().__init__()
        self.mediator = mediator
        self.points = set()
        for y in range(cell_rows):
            self.points.add((0, y))
            self.points.add((cell_cols+1, y))
        for x in range(cell_cols+2):
            self.points.add((x, cell_rows))


class Pile(Blocks):
    color = (150, 150, 150)

    def __init__(self, mediator):
        super().__init__()
        self.mediator = mediator
        self.minos = []

    @property
    def points(self):
        all_points = set()
        for m in self.minos:
            all_points |= set(map(lambda p: ((m.x + p[0]) % cell_cols, m.y + p[1]), m.points))
        return all_points

    def add(self, m):
        h, s, l, a = m.color.hsla
        s = s // 2
        m.color.hsla = (h, s, l, a)
        self.minos.append(m)

    def slide(self, dx):
        for m in self.minos:
            m.x = (m.x + dx + cell_cols) % cell_cols

    def draw(self):
        for m in self.minos:
            m.draw()

FALLING = 1
LANDING = 2
LANDED = 3
class Mino(Blocks):
    def __init__(self, mediator, x, y, color, shape):
        super().__init__(x, y)
        self.mediator = mediator
        self.points = set()
        self.state = FALLING
        self.color = pygame.Color(color)
        self.load(shape)

    def _move(self, dx, dy):
        if not self.mediator.collide(self, dx, dy):
            self.x += dx
            self.y += dy
            return True
        return False

    def move_left(self):
        return self._move(-1, 0)

    def move_right(self):
        return self._move(1, 0)

    def move_down(self, land=True):
        success = self._move(0, 1)
        if success:
            if self.mediator.collide(self, 0, 1):
                mino.state = LANDING
            msec = 0
        else:
            if land:
                mino.state = LANDED
        return success
            

    def drop(self, land=True):
        while self.move_down(land):
            self.mediator.display()
            self.draw()
            clock.tick(120)
        self.mediator.display()
        self.draw()
        clock.tick(60)

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
        dry = Mino(self.mediator, self.x, self.y, self.color, self.shape)
        dry.points = points
        if not self.mediator.collide(dry):
            self.points = points

    def rotate_left(self):
        self.rotate_right(reverse=True)

    def delete_line(self, cy):
        lines = self.shape
        for y in reversed(list(range(self.height))):
            if self.y + y == cy:
                lines.pop(y)
                break
        if self.y <= cy:
            self.y += 1
        self.load(lines)

    def draw(self):
        self.mediator.draw_mino(self)

class BlockMediator:
    direction = 1
    border = 1
    bg_color = (30, 30, 30)

    def __init__(self):
        self.wall = Wall(self)
        self.pile = Pile(self)
        self.mino = self.create_mino()
        self.screen = pygame.display.set_mode((480, 840))

    def create_mino(self):
        color, shape = random.choice(shapes)
        x = (cell_cols - len(shape[0])) // 2
        y = 0
        mino = Mino(self, x, y, color, shape)
        self.mino = mino
        return mino

    def _collide_with(self, m, other, px=0, py=0):
        points = set([(px + x, py + y)
                    for x, y in m.points])
        return (points & other.points) != set()

    def collide(self, m, dx=0, dy=0):
        px = m.x + dx
        py = m.y + dy
        return self._collide_with(m, self.wall, px+1, py) \
            or self._collide_with(m, self.pile, px, py)

    def clear_line(self):
        targets = []
        for y, line in enumerate(self.pile.shape):
            if ''.join(line) == '#' * cell_cols:
                targets.append(y)
        # effect
        for i in range(-5, 15):
            s = 255 - i**2
            for y in targets:
                c = (s, s, s)
                pygame.draw.rect(self.screen, c, (cell_size, y * cell_size,
                                             cell_cols * cell_size, cell_size))
            pygame.display.flip()
            clock.tick(60)

        for y in targets:
            for m in self.pile.minos:
                m.delete_line(y)
            for i in reversed(list(range(len(self.pile.minos)))):
                if self.pile.minos[i].empty():
                    self.pile.minos.pop(i)
            self.direction *= -1

    def _draw_cell(self, color, cx, cy, dx, dy):
        px = cx * cell_size + dx
        py = cy * cell_size + dy
        pygame.draw.rect(self.screen, self.bg_color, (px, py, cell_size, cell_size))
        pygame.draw.rect(self.screen, color, (
            px + self.border, py + self.border,
            cell_size-self.border, cell_size-self.border))

    def draw(self, block, sx=0, sy=0, dx=0, dy=0):
        for x, y in block.points:
            cx = sx + x
            cy = sy + y
            self._draw_cell(block.color, cx, cy, dx, dy)

    def draw_mino(self, m):
        global msec
        dx = cell_size
        dy = (cell_size * (msec % interval) // interval ) if m.state == FALLING else 0
        for x, y in m.points:
            cx = ((m.x + x + cell_cols) % cell_cols)
            cy = (m.y + y)
            self._draw_cell(m.color, cx, cy, dx, dy)

    def display(self):
        # clear
        self.screen.fill(self.bg_color)
        # drawing
        self.draw(wall)
        pile.draw()
        if mino.state != LANDED:
            mino.draw()
        pygame.display.flip()

    def gameover(self):
        self.__init__()
        global pile
        pile = self.pile

def main():
    # Initialise screen
    pygame.init()
    pygame.display.set_caption('tetro')
    pygame.key.set_repeat(200,100)

    global clock
    clock = pygame.time.Clock()

    global wall, pile, mino
    mediator = BlockMediator()
    wall = mediator.wall
    pile = mediator.pile
    mino = mediator.mino
    pressed = False

    global msec, interval
    msec = 0
    interval = 1000
    # Event loop
    while 1:
        msec += clock.tick(60)
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                shift = bool(event.mod & KMOD_SHIFT)
                if event.key == K_ESCAPE:
                    return
                elif event.key in (K_SPACE, K_f, K_d) and not pressed:
                    pressed = True
                    land = not (shift or event.key == K_f)
                    mino.drop(land)
                elif not mino:
                    continue
                elif event.key in (K_LEFT, K_a, K_h):
                    mino.move_left()
                elif event.key in (K_DOWN, K_s, K_j):
                    mino.move_down()
                elif event.key in (K_RIGHT, K_d, K_l):
                    mino.move_right()
                elif (not shift and event.key in (K_r, K_UP, K_w, K_k)) \
                or (shift and event.key in (K_e,)):
                    mino.rotate_right()
                elif (not shift and event.key in (K_e,)) \
                or (shift and event.key in (K_UP, K_w, K_k)):
                    mino.rotate_left()
            elif event.type == KEYUP:
                pressed = False
        
        if msec > interval:
            msec -= interval
            if mino.state != LANDED:
                mino.move_down()
                if mino.state == FALLING:
                    pile.slide(mediator.direction)
        if mino.state == LANDED:
            pile.add(mino)
            mino = mediator.create_mino()
            mediator.clear_line()
            # next mino
            if mediator.collide(mino, 0, 0):
                mediator.gameover()
        mediator.display()

if __name__ == '__main__': main()
