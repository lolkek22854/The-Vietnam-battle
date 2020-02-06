from pygame import *
import pygame
from config import *

PLATFORM_WIDTH = 32
PLATFORM_HEIGHT = 32
PLATFORM_COLOR = "#FF6262"
# reload_sound = pygame.mixer.Sound("/sounds/03038.mp3")



class Platform(sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.image = Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
        self.image.fill(Color(PLATFORM_COLOR))
        self.image = image.load("%s/blocks/platform.png" % ICON_DIR)
        self.rect = Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)


class Lattice(sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.image = Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
        self.image.fill(Color(PLATFORM_COLOR))
        self.image = image.load("%s/blocks/lattice.png" % ICON_DIR)
        self.rect = Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)


class Ladder(sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.image = Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
        self.image.fill(Color(PLATFORM_COLOR))
        self.image = image.load("%s/blocks/ladder.png" % ICON_DIR)
        self.image.set_colorkey((255, 255, 255))
        self.rect = Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)


class Perk(Platform):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        Platform.__init__(self, x, y)
        self.image = image.load("%s/blocks/beacon.bmp" % ICON_DIR)
        self.image.set_colorkey((255, 255, 255))


class End(sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.image = image.load("%s/blocks/end.png" % ICON_DIR)
        self.image.set_colorkey((255, 255, 255))
        self.rect = Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT * 2)


class Door(sprite.Sprite):
    def __init__(self, x, y,ch):
        sprite.Sprite.__init__(self)
        self.ch = ch
        self.image = image.load("%s/blocks/end.png" % ICON_DIR)
        self.image.set_colorkey((255, 255, 255))
        self.rect = Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT * 2)
        self.is_opened = False

    def open(self):
        self.is_opened = True
        self.image = Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))


class Medkit(Platform):
    def __init__(self, x, y):
        Platform.__init__(self, x, y)
        self.image = image.load("%s/blocks/heal.png" % ICON_DIR)


class Beacon(sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.spx = 0
        self.spy = 0
        self.sound = mixer.Sound('sounds/beep.wav')
        self.change_flag = True
        self.image = image.load("%s/blocks/beacon.bmp" % ICON_DIR)
        self.image.set_colorkey((255, 255, 255))
        self.rect = Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)


class Helicopter(sprite.Sprite):
    def __init__(self, x, y):
        self.spy = 5
        self.shoot_flag = True
        self.sound = mixer.Sound('sounds/helicopter.ogg')
        self.spx = 5
        self.steps = 0
        sprite.Sprite.__init__(self)
        self.image = image.load("%s/sprites/helicopter.png" % ICON_DIR)
        self.image.set_colorkey((255, 255, 255))
        self.rect = Rect(x, y, 100, PLATFORM_HEIGHT)

    def fly_away(self):
        self.rect.x += self.spx
        self.rect.y -= self.spy

    def update(self, pos, bombs):
        self.spx = 5
        self.spy = 5
        x, y = pos
        if self.rect.y < y and self.shoot_flag:
            self.spy = 5
        else:
            self.spy = -5
            if self.shoot_flag:
                self.shoot_flag = False
        if abs(x - self.rect.x) < 200 and self.steps % 10 == 0:
            self.shoot(bombs)
        self.rect.y += self.spy
        self.rect.x += self.spx
        self.steps += 1

    def shoot(self, bombs):
        bombs.append(Bomb(self.rect.x, self.rect.y - 200))


class Button(sprite.Sprite):
    def __init__(self, x, y, ch):
        sprite.Sprite.__init__(self)
        self.ch = ch
        self.sound = mixer.Sound('sounds/turn.ogg')
        self.image = image.load("%s/blocks/button_off.png" % ICON_DIR)
        self.rect = Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)
        self.is_on = False

    def push(self):
        self.is_on = True
        self.sound.play()
        self.image = image.load("%s/blocks/button_on.png" % ICON_DIR)


class Bomb(sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.rect = Rect(x - 50, y - 100, 150, 100)
        self.boom = False
        self.sound = mixer.Sound('sounds/bahh.ogg')
        self.boom_count = 10
        self.sprite = AnimatedSprite(image.load("sprites/boom.bmp"), 4, 4, 50, 50)
        self.image = image.load('sprites/bomb.bmp')
        self.image.set_colorkey((255, 255, 255))

    def update(self, y):
        if self.rect.y < y - 50:
            self.rect.y += 5
        else:
            if not self.boom:
                self.sound.play()
            self.boom = True
            self.sprite.update()
            self.image = self.sprite.image
            self.boom_count -= 1


class AnimatedSprite(sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__()
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        sheet.set_colorkey((255, 255, 255))
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        self.image.set_colorkey((255, 255, 255))
