import pygame
from pygame import *
from player import Player
from blocks import *
# from shot import Shot
from enemy import Enemy
from attack import Attack
from interface import *
from weapon import *
from levels import Board
from config import *

DISPLAY = (WIN_WIDTH, WIN_HEIGHT)

levels = ['level2.txt', 'level.txt', 'level_1.txt']


# BACKGROUND_COLOR = "#004400"


class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = Rect(0, 0, width, height)

    def apply(self, target):
        if type(target) == pygame.Surface:
            return self.state.topleft
        else:
            return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)


def camera_configure(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t = -l + WIN_WIDTH / 2, -t + WIN_HEIGHT / 2

    l = min(0, l)
    l = max(-(camera.width - WIN_WIDTH), l)
    t = max(-(camera.height - WIN_HEIGHT), t)
    t = min(0, t)

    return Rect(l, t, w, h)


def main():
    pygame.init()
    # screen = pygame.display.set_mode(DISPLAY, FULLSCREEN)
    screen = pygame.display.set_mode(DISPLAY)
    pygame.display.set_caption("The Nekitos")
    stage = 'menu'
    level_num = -1
    run = True
    play_flag = False
    menu_color = (28, 91, 237)

    while run:
        if stage == 'menu':
            stage, run = menu(screen, run)

        if stage == 'levels':
            running = True
            pos_move = (0, 0)
            pos_push = (0, 0)
            board = Board(5, 7)
            board.set_view(100, 100, 70)
            while running:
                for e in pygame.event.get():
                    if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                        running = False
                        run = False
                    if e.type == pygame.MOUSEMOTION:
                        pos_move = e.pos
                    if e.type == pygame.MOUSEBUTTONDOWN:
                        pos_push = e.pos

                for cell in board.board:
                    cell.in_cell(pos_move, True)
                    if cell.in_cell(pos_push):
                        print(cell.num)
                        level_num = cell.num
                        stage = 'main_game'
                        running = False
                        break

                screen.fill(menu_color)
                board.render(screen)
                pygame.display.flip()

        if stage == 'main_game':
            bg = pygame.image.load('back.png').convert()
            hero = Player(55, 55)
            left = right = False
            up = False
            ctrl = False
            down = True
            hero_alive = True
            hit = ''
            hel = -1
            pos_call = (-1, -1)
            helicopter = Helicopter(0, 0)
            shots = []
            enemy_bullits = []
            beacon = -1

            enemies = []
            lattices = []
            stairs = []
            ends = []
            perks = []
            bombs = []
            buttons = []
            doors = []
            doors_to_buttons = {}
            medkits = []
            # doors = {}

            entities = pygame.sprite.Group()
            platforms = []

            fl = open(LEVELS[level_num - 1], 'r')
            level = fl.read().split('\n')
            fl.close()

            timer = pygame.time.Clock()
            x = 0
            y = 0

            enemies_ind = []
            coords = {}
            for row in level:
                for col in row:
                    if col == "-":
                        pf = Platform(x, y)
                        entities.add(pf)
                        platforms.append(pf)
                    elif col in 'ABC':
                        d = Door(x, y, col)
                        doors.append(d)
                    elif col in 'abc':
                        bt = Button(x, y, col)
                        buttons.append(bt)
                    elif col == "@":
                        pf = End(x, y)
                        entities.add(pf)
                        ends.append(pf)
                    elif col == "/":
                        pf = Perk(x, y)
                        perks.append(pf)
                    elif col == "*":
                        bt = Medkit(x, y)
                        medkits.append(bt)
                    elif col == "+":
                        helicopter = Helicopter(x, y)
                        platforms.append(helicopter)
                        helicopter.sound.play()
                    elif col == '|':
                        pf = Lattice(x, y)
                        lattices.append(pf)
                        entities.add(pf)
                    elif col == '~':
                        hero = Player(x, y)
                    elif col == '=':
                        stairs.append(Ladder(x, y))
                    elif col != ' ':
                        if coords.get(col, ' ') == ' ':
                            enemies_ind.append(col)
                            coords[col] = x
                        else:
                            coords[col] = (coords.get(col), x, y)

                    x += PLATFORM_WIDTH
                y += PLATFORM_HEIGHT
                x = 0

            for i in range(len(doors)):
                d = doors[i]
                for b in buttons:
                    if d.ch.lower() == b.ch:
                        doors_to_buttons[b] = i

            total_level_width = len(level[0]) * PLATFORM_WIDTH
            total_level_height = len(level) * PLATFORM_HEIGHT

            entities.add(hero)

            camera = Camera(camera_configure, total_level_width, total_level_height)
            running = True
            for i in enemies_ind:
                pos = coords.get(i)
                enemies.append(Enemy(pos[0], pos[2], pos))
            while running:
                for e in pygame.event.get():
                    if not hero_alive and e.type == KEYDOWN:
                        running = False
                        stage = 'menu'
                    if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                        running = False
                        run = False
                    if e.type == KEYDOWN and e.key == K_1:
                        hero.weapon = hero.weapons[0]
                    if e.type == KEYDOWN and e.key == K_2:
                        hero.weapon = hero.weapons[1]
                    if e.type == KEYDOWN and e.key == K_3:
                        hero.weapon = hero.weapons[2]
                    if e.type == KEYDOWN and e.key == K_w:
                        up = True
                    if e.type == KEYDOWN and e.key == K_a:
                        left = True
                    if e.type == KEYDOWN and e.key == K_d:
                        right = True
                    if e.type == KEYDOWN and e.key == K_s:
                        down = False
                    if e.type == KEYUP and e.key == K_s:
                        down = True
                    if e.type == KEYDOWN and e.key == K_r:
                        hero.weapon.reload()
                        hero.weapon.reload_sound.play()

                    if e.type == KEYDOWN and e.key == K_e:
                        for b in buttons:
                            if b.rect.colliderect(hero):
                                b.push()
                                doors[doors_to_buttons.get(b, 0)].open()

                    if e.type == KEYDOWN and e.key == K_p and hero.perks > 0:
                        hero.perks -= 1
                        x, y = hero.rect.center
                        beacon = Beacon(x, y - 10)
                        beacon.direction = hero.direction
                        beacon.spx = 20
                        beacon.spy = 10
                        beacon.sound.play()
                    if e.type == KEYUP and e.key == K_w:
                        up = False
                    if e.type == KEYUP and e.key == K_d:
                        right = False
                    if e.type == KEYUP and e.key == K_a:
                        left = False

                    if hero.weapon.ammo > 0:
                        x, y, = hero.rect.center
                        y1 = -13
                        s = True
                        shoots = []
                        if e.type == KEYDOWN and e.key == 32:
                            if hero.direction:
                                s = Shot((x + 100, y + y1), (x + (hero.wx_l * 2), y + y1))
                                if hero.weapon.bullet_num != 1:
                                    for i in range(hero.weapon.bullet_num):
                                        shoot = Shot((x + 100, y - 20 + 10 * i), (x + (hero.wx_l * 2), y + y1))
                                        shoot.image = pygame.image.load('bullit_r.png').convert()
                                        shoots.append(shoot)
                                s.image = pygame.image.load('bullit_r.png').convert()
                            else:
                                s = Shot((x - 100, y + y1), (x + hero.wx_r * 2, y + y1))
                                if hero.weapon.bullet_num != 1:
                                    for i in range(hero.weapon.bullet_num):
                                        shoots.append(Shot((x - 100, y - 20 + 10 * i), (x + hero.wx_r * 2, y + y1)))

                        if type(s) == Shot:
                            hero.weapon.sound.play()
                            hero.weapon.shoot()
                            shots.append(s)
                            if shoots != []:
                                shots += shoots

                    if e.type == KEYDOWN and e.key == K_DOWN:
                        x, y, = hero.rect.center
                        hit = Attack(x, y)

                screen.blit(bg, camera.apply(bg))

                for b in buttons:
                    screen.blit(b.image, camera.apply(b))

                for m in medkits:
                    screen.blit(m.image, camera.apply(m))
                    if m.rect.colliderect(hero.rect):
                        hero.hp += 20
                        medkits.remove(m)

                for d in doors:
                    if not d.is_opened and d not in platforms:
                        platforms.append(d)
                    if d.is_opened and d in platforms:
                        platforms.remove(d)
                    screen.blit(d.image, camera.apply(d))

                if beacon != -1:
                    if beacon.change_flag:
                        if not beacon.direction:
                            beacon.rect.x -= beacon.spx
                            beacon.spx -= 1
                        else:
                            beacon.rect.x += beacon.spx
                            beacon.spx -= 1
                        if beacon.spy < 0:
                            beacon.spy = -6
                        if beacon.spx < 0:
                            beacon.spx = 0
                            for p in platforms:
                                if p.rect.colliderect(beacon.rect):
                                    beacon.spy = 0
                                    beacon.spx = 0
                                    beacon.change_flag = False
                                    pos_call = beacon.rect.center
                                    hel = Helicopter(pos_call[0] - 1000, pos_call[1] - 1000)
                                    hel.sound.play()
                        beacon.rect.y -= beacon.spy
                        beacon.spy -= 1
                    else:
                        beacon.dead_frames -= 1
                    screen.blit(beacon.image, camera.apply(beacon))
                    if beacon.dead_frames < 0:
                        beacon = -1

                if hel != -1:
                    # print('g')
                    hel.update(pos_call, bombs)
                    screen.blit(hel.image, camera.apply(hel))

                for b in bombs:
                    b.update(pos_call[1])
                    if b.boom_count == 0:
                        bombs.remove(b)
                    screen.blit(b.image, camera.apply(b))

                if abs(hero.rect.x - helicopter.rect.x) in range(20, 1000):
                    helicopter.fly_away()

                # if abs(hero.rect.x - helicopter.rect.x) > 1000:
                #     helicopter = -1

                screen.blit(helicopter.image, (camera.apply(helicopter)[0] - 580, camera.apply(helicopter)[1] - 280))

                camera.update(hero)
                if hero.hp >= 0:
                    if down:
                        hero.update(left, right, up, platforms + lattices, stairs, ctrl, down)
                    else:
                        hero.update(left, right, up, platforms, stairs, ctrl, down)

                    if hit != '':
                        hit.update(hero)
                        if hit.frames_count < 10:
                            screen.blit(hit.image, camera.apply(hit))
                        else:
                            hit = ''

                for s in stairs:
                    if check_and_draw(s, hero, WIN_WIDTH, WIN_HEIGHT, total_level_width, total_level_height):
                        screen.blit(s.image, camera.apply(s))

                for s in shots:
                    s.move_shot()
                    if s.collide(platforms):
                        shots.remove(s)
                    for en in enemies:
                        if pygame.sprite.collide_rect(s, en):
                            if s in shots:
                                shots.remove(s)
                            en.hp -= hero.weapon.hit
                    screen.blit(s.image, camera.apply(s))

                for e in enemies:
                    e.can_see(hero)
                    if e.alarm:
                        l, r, u = e.rule_enemy(hero)
                        if abs(e.rect.centerx - hero.rect.centerx) < 200:
                            if not enemy_shoot(e, enemy_bullits):
                                e.shoot_count -= 1
                    else:
                        u = False
                        l, r = e.patrol()
                    e.update(l, r, u, platforms + lattices, stairs)
                    if check_and_draw(e, hero, WIN_WIDTH, WIN_HEIGHT, total_level_width, total_level_height):
                        screen.blit(e.image, camera.apply(e))
                    if hit != '':
                        if hit.rect.colliderect(e.rect):
                            e.hp = 0

                    if e.dead_count == 0:
                        enemies.remove(e)

                    for b in bombs:
                        if e.rect.colliderect(b.rect) and b.boom:
                            e.hp = 0

                    if e.direction:
                        screen.blit(e.weapon.image,
                                    (camera.apply(e)[0] + e.wx_l, camera.apply(e)[1] + e.wy))
                    else:
                        screen.blit(e.weapon.image,
                                    (camera.apply(e)[0] + e.wx_r, camera.apply(e)[1] + e.wy))

                for e in entities:
                    if check_and_draw(e, hero, WIN_WIDTH, WIN_HEIGHT, total_level_width, total_level_height):
                        screen.blit(e.image, camera.apply(e))

                for b in enemy_bullits:
                    b.move_shot()
                    if b.collide(platforms):
                        enemy_bullits.remove(b)
                    if b.collide([hero]):
                        hero.hp -= b.damage
                        hero.hit_sound.play()
                        try:
                            enemy_bullits.remove(b)
                        except:
                            pass
                    screen.blit(b.image, camera.apply(b))

                hero.image.set_colorkey((255, 255, 255))

                if hero.direction:
                    screen.blit(hero.weapon.image, (camera.apply(hero)[0] + hero.wx_l, camera.apply(hero)[1] + hero.wy))
                else:
                    screen.blit(hero.weapon.image, (camera.apply(hero)[0] + hero.wx_r, camera.apply(hero)[1] + hero.wy))

                if hero.hp <= 0:
                    hero_alive = False
                    hero.die()
                    udied(screen)

                for e in ends:
                    if hero.rect.colliderect(e.rect):
                        running = False
                        stage = 'main_game'
                        level_num += 1

                for p in perks:
                    if p.rect.colliderect(hero.rect):
                        perks.remove(p)
                        hero.perks += 1
                    screen.blit(p.image, camera.apply(p))

                draw_params(screen, hero, WIN_WIDTH, WIN_HEIGHT)
                timer.tick(60)
                pygame.display.flip()

        pygame.display.flip()


if __name__ == "__main__":
    main()
