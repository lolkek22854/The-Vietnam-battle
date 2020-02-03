import pygame


class AnimatedSprite(pygame.sprite.Sprite):
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


dragon = AnimatedSprite(pygame.image.load("sprites/boom.bmp"), 4, 4, 50, 50)

pygame.init()
screen = pygame.display.set_mode((500, 500))
running = True
timer = pygame.time.Clock()
while running:
    timer.tick(20)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))

    dragon.update()

    screen.blit(dragon.image, (100, 100))

    pygame.display.flip()
