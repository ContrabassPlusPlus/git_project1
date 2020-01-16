import pygame, os, math, sys, random


pygame.init()
WIDTH = 500
HEIGHT = 950
FPS = 30
SIZE = WIDTH, HEIGHT
SCORE = 0
screen = pygame.display.set_mode([600, 500], flags=pygame.RESIZABLE)
screen.fill((0, 0, 0))
clock = pygame.time.Clock()
running = False
pygame.display.flip()


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, colorkey=None):
    fullname = os.path.join('game', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image  


def cut_sheet(sheet, columns, rows):
        frames = []
        rectag = pygame.Rect(0, 0, sheet.get_width() // columns, 
                           sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (rectag.w * i, rectag.h * j)
                frames.append(sheet.subsurface(pygame.Rect(frame_location, rectag.size)))
        return frames


intro_text = ["                      SPACESHIP VS. UFOS", "",
              "", "", "",
              "New game", "", "", 
              "Choose difficulty", "", "",
              "Exit"]

fon = pygame.transform.scale(load_image("background.jpg", colorkey=-1), (423, 500))
screen.blit(fon, (600 - 423, 0))
font = pygame.font.Font(None, 30)
text_coord = 20
for line in intro_text:
    string_rendered = font.render(line, 1, pygame.Color('red'))
    intro_rect = string_rendered.get_rect()
    text_coord += 10
    intro_rect.top = text_coord
    intro_rect.x = 50
    text_coord += intro_rect.height
    screen.blit(string_rendered, intro_rect)

while not(running):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if 50 <= pygame.mouse.get_pos()[0] <= 150 and 185 <= pygame.mouse.get_pos()[1] <= 206:
                running = True
            elif 50 <= pygame.mouse.get_pos()[0] <= 95 and 278 <= pygame.mouse.get_pos()[1] <= 299:
                pass
            elif 50 <= pygame.mouse.get_pos()[0] <= 89 and 371 <= pygame.mouse.get_pos()[1] <= 392:
                terminate()
    pygame.display.flip()
    clock.tick(FPS)

screen = pygame.display.set_mode([WIDTH, HEIGHT])
screen.fill((0, 0, 255))
enemies = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
player = pygame.sprite.Group()
effects = pygame.sprite.Group()


class PlayerBullet(pygame.sprite.Sprite):
    image_bullet = load_image("playerlaser.jpg", colorkey=-1)
    image_missile = load_image("playermissile.jpg", colorkey=-1)
    
    def __init__(self, group, x, y, w, h, speed, damage, b_type, increase=True):
        super().__init__(group)
        self.image = pygame.transform.scale(PlayerBullet.image_bullet if b_type == 'bullet' 
                                            else PlayerBullet.image_missile, (w, h))
        if b_type[0] == 'b':
            self.image = pygame.transform.rotate(self.image, -30)            
        self.rect = self.image.get_rect()
        self.speed = speed
        self.damage = damage
        if not(increase):
            if b_type == "bullet":
                self.damage = 5
            else:
                self.damage = 16
        self.b_type = b_type
        self.exist = True
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)
        
    def update(self):
        if self.rect.y < 0 or not(self.exist):
            self.kill()
        self.rect = self.rect.move(0, -self.speed)


class Explosion(pygame.sprite.Sprite):
    image = load_image("explosion.jpg", colorkey=-1)
    image = cut_sheet(image, 5, 3)
    
    def __init__(self, group, x, y, size):
        super().__init__(group)
        self.image = Explosion.image[0]
        self.num_pic = 0
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.size = size
        self.image = pygame.transform.scale(self.image, size)
        
    def update(self):
        if self.num_pic < 14:
            self.num_pic += 1
            self.image = Explosion.image[self.num_pic]
            self.image = pygame.transform.scale(self.image, self.size)
        else:
            self.kill()
    

class Shield(pygame.sprite.Sprite):
    image = load_image("shield.png")
    
    def __init__(self, group):
        super().__init__(group)
        self.image = Shield.image
        self.image = pygame.transform.flip(self.image, False, True)
        self.image = pygame.transform.scale(self.image, (500, 33))
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 500
        self.lives = 500
        self.mask = pygame.mask.from_surface(self.image)
        
    def update(self):
        if pygame.sprite.spritecollide(self, player_bullets, False):
            for collision in pygame.sprite.spritecollide(self, player_bullets, False):
                if pygame.sprite.collide_mask(self, collision):
                    self.lives -= collision.damage
                    collision.exist = False
        if self.lives < 1:
            self.kill()


class LaserBeam(pygame.sprite.Sprite):
    def __init__(self, group, x, y, height):
        super().__init__(group)
        self.image = pygame.Surface((50, height))
        self.rect = self.image.get_rect()
        self.width = 50
        self.height = height
        self.rect.x = x
        self.rect.y = y
        self.damage = 1
        self.exist = False
        self.speed = 50 / FPS
        self.image.fill((255, 255, 255))
        #self.image.blit(screen, (self.rect.x, self.rect.y))
        
    def update(self):
        if self.width > 0:
            self.width = self.width - self.speed
            self.image = pygame.transform.scale(self.image, (round(self.width) if self.width >= 0
                                                             else 0, self.height))
            #self.rect = self.image.get_rect()
            self.rect = self.rect.move(round(self.speed / 2), 0)
            self.rect.width = round(self.width)
            self.mask = pygame.mask.from_surface(self.image)
            #self.image.blit(screen, (self.rect.x, self.rect.y))
        else:
            self.kill()
            
            
class SpinBullet(pygame.sprite.Sprite):
    image = load_image("enemy_bullet.jpg", colorkey=-1)
    
    def __init__(self, group, x, y, angle, rotation=0):
        super().__init__(group)
        self.image = SpinBullet.image
        self.image = pygame.transform.scale(self.image, (15, 15))
        self.angle = -angle + math.pi / 2
        self.rotation = rotation
        self.radius = 650
        if rotation == 0:
            self.rotation = 10 ** -9
            self.radius = 10 ** 10
        self.rect = self.image.get_rect()
        self.damage = 1
        self.exist = True
        self.rect.x = x
        self.rect.y = y
        self.x = self.rect.x - int(self.radius * math.cos(self.angle))
        self.y = self.rect.y + int(self.radius * math.sin(self.angle))
        self.mask = pygame.mask.from_surface(self.image)    
        
    def update(self):
        if -10 <= self.rect.x <= 500 and -100 <= self.rect.y <= 950 and self.exist:
            self.angle -= self.rotation
            self.rect.x = self.x + int(math.cos(self.angle) * self.radius)
            self.rect.y = self.y - int(math.sin(self.angle) * self.radius)
        else:
            self.kill()
            
            
class Meteor(SpinBullet):
    image = load_image("meteor.jpg", colorkey=-1)
    
    def __init__(self, group, x=0, y=-100, angle=math.pi / 2, rotation=0):
        rotation = 0
        super().__init__(group, x, y, angle, rotation)
        self.image = Meteor.image
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface()
        
    def update(self):
        self.exist = True
        super().update()


class Player(pygame.sprite.Sprite):
    image = load_image("spaceship.jpg", colorkey=-1)
    
    def __init__(self, group):
        super().__init__(group)
        self.lives = 10 ** 1 // 2
        self.image = Player.image
        self.image = pygame.transform.scale(self.image, (60, 50))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.vulnerable = True
        self.vulnerable_timer = None
        self.speed = 7
        self.delay = 0
        self.rect.x = 220
        self.rect.y = 900
        
    def update(self, args):
        if not(self.delay):
            if pygame.mouse.get_pressed()[0]:
                PlayerBullet(player_bullets, self.rect.x + 10, self.rect.y + 40, 10, 10, 50, 1, 
                             "bullet", self.vulnerable)
                PlayerBullet(player_bullets, self.rect.x + 40, self.rect.y + 40, 10, 10, 50, 1,
                             "bullet", self.vulnerable)
                self.delay = FPS // 6
            elif pygame.mouse.get_pressed()[2]:
                PlayerBullet(player_bullets, self.rect.x + 8, self.rect.y + 35, 15, 21, 25, 8,
                              "missile", self.vulnerable)
                PlayerBullet(player_bullets, self.rect.x + 37, self.rect.y + 35, 15, 21, 25, 8,
                              "missile", self.vulnerable)
                self.delay = FPS                
        """
        if args:
            for arg in args:
                if arg.type == pygame.MOUSEBUTTONDOWN:
                    if arg[0] and not(self.delay):
                        
                    elif arg[2] and not(self.delay):
                        pass
                elif arg.type == pygame.KEYDOWN:
                    print(arg.key)
        """
        if pygame.key.get_pressed()[119] or pygame.key.get_pressed()[273]:
            self.rect = self.rect.move(0, -self.speed)
        if pygame.key.get_pressed()[97] or pygame.key.get_pressed()[276]:
            self.rect = self.rect.move(-self.speed, 0)
        if pygame.key.get_pressed()[115] or pygame.key.get_pressed()[274]:
            self.rect = self.rect.move(0, self.speed)
        if pygame.key.get_pressed()[100] or pygame.key.get_pressed()[275]:
            self.rect = self.rect.move(self.speed, 0)
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x > WIDTH - 60:
            self.rect.x = WIDTH - 60
        if self.rect.y < 0:
            self.rect.y = 0
        elif self.rect.y > HEIGHT - 50:
            self.rect.y = HEIGHT - 50
        if self.vulnerable_timer:
            self.vulnerable_timer -= 1
        else:
            self.image.set_alpha(255)
            self.vulnerable = True
        if pygame.sprite.spritecollide(self, enemy_bullets, False):
            for collision in pygame.sprite.spritecollide(self, enemy_bullets, False):
                if self.vulnerable:
                    if pygame.sprite.collide_mask(self, collision) or \
                      (pygame.sprite.collide_rect(self, collision) and not(collision.exist)):
                        self.lives -= collision.damage
                        collision.exist = False 
                        self.vulnerable = False
                        self.vulnerable_timer = FPS * 4
                        self.image.set_alpha(128)
                        break
        if self.lives < 1:
            terminate()
        if self.delay:
            self.delay -= 1
            
            
class Ufo(pygame.sprite.Sprite):
    images = load_image("ufo.jpg", colorkey=-1)
    images = cut_sheet(images, 4, 5)
    del images[5]
    del images[9]
    del images[16]
    del images[16]
    
    def __init__(self, group):
        super().__init__(group)
        self.lives = random.randint(20, 35)
        self.image = Ufo.images[0]
        self.num_pic = 0
        self.imupt = 2
        self.image = pygame.transform.scale(self.image, (80, 80))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.vulnerable = False
        self.speed_x = 1
        self.speed_y = 1
        self.delay = -1
        self.attack_type = random.randint(1, 3)
        self.charge_speed = 25 / (FPS * 2)
        self.start_in = FPS * 2
        self.size_now = 0
        self.point = None
        self.rect.x = random.randint(-200, -100)
        self.rect.y = random.randint(-200, -100)
    
    def appear(self):
        if not(self.point):
            self.point = (random.randint(0, 400), random.randint(0, 100))
            self.frames_to_reach = random.randint(FPS // 2, FPS * 3 // 2)
            self.speed_x = int((self.point[0] - self.rect.x) / self.frames_to_reach)
            self.speed_y = int((self.point[1] - self.rect.y) / self.frames_to_reach)
        if self.frames_to_reach:
            self.frames_to_reach -= 1
            self.rect = self.rect.move(self.speed_x, self.speed_y)
        else:
            self.delay = 0
            self.vulnerable = True
            self.speed_x, self.speed_y = 0, 0
        
    """
    def attack1(self):
        if self.start_in:
            pygame.draw.circle(screen, pygame.Color('white'), (self.rect.x + 40, self.rect.y + 150), 
                               round(self.charge_speed * (self.size_now + 1)))
            self.size_now += 1
            self.start_in -= 1
        else:
            LaserBeam(enemy_bullets, self.rect.x + 15, self.rect.y, HEIGHT - self.rect.y)
    """
     
    def update(self, kill_em_all=False, suicide=False):
        global SCORE
        self.suicide = suicide
        if self.speed_x and self.speed_y:
            self.appear()
        if pygame.sprite.spritecollide(self, player_bullets, False):
            for collision in pygame.sprite.spritecollide(self, player_bullets, False):
                if pygame.sprite.collide_mask(self, collision) and self.vulnerable:
                    self.lives -= collision.damage
                    collision.exist = False
        if self.lives > 0 and not(self.delay):
            if self.attack_type == 1:
                if self.start_in:
                    pygame.draw.circle(screen, pygame.Color('white'), (self.rect.x + 40, self.rect.y + 100), 
                                       round(self.charge_speed * (self.size_now + 1)))
                    self.size_now += 1
                    self.start_in -= 1
                else:
                    LaserBeam(enemy_bullets, self.rect.x + 15, self.rect.y + 100, HEIGHT - 
                              self.rect.y)   
                    self.start_in = FPS * 2
                    self.size_now = 0                    
                    self.delay = FPS * 2
                    self.attack_type = random.randint(1, 3)
                    if self.suicide:
                        self.kill()
            elif self.attack_type == 2:
                k = not(random.choice([True, False]))
                if not(k):
                    rot = random.randint(1, 3) / 100
                    p = random.randint(15, 25)
                else:
                    p = random.randint(45, 75)
                for _ in range(p):
                    SpinBullet(enemy_bullets, self.rect.x + 80, self.rect.y + 80, 
                               _ / 180 * math.pi * 180 / p, random.randint(1, 6) / 200 if k else rot)
                self.delay = FPS * 5
                self.attack_type = random.randint(1, 3)
                if self.suicide:
                    self.kill()
            elif self.attack_type == 3:
                p = random.randint(15, 25)
                for _ in range(p):
                    SpinBullet(enemy_bullets, self.rect.x + 80, self.rect.y + 80, 
                               _ / 180 * math.pi * 180 / p)
                self.delay = FPS * 4        
                self.attack_type = random.randint(1, 3)
                if suicide:
                    self.kill()
            elif self.attack_type == 4:
                Meteor(enemy_bullets)
                self.delay = FPS * 5
                self.attack_type = random.randint(1, 3)
                if self.suicide:
                    self.kill()
        self.imupt -= 1
        if not(self.imupt):
            self.num_pic = (self.num_pic + 1) % 16
            self.image = Ufo.images[self.num_pic]
            self.image = pygame.transform.scale(self.image, (80, 80))
            self.mask = pygame.mask.from_surface(self.image)
            self.imupt = 2
        if self.delay:
            self.delay -= 1
        if self.lives < 1 or kill_em_all:
            SCORE += 100
            Explosion(effects, self.rect.x, self.rect.y, (80, 80))
            self.kill()
            
            
class BossUfo(Ufo):
    image = load_image("ufo.jpg")
    
    def __init__(self, group):
        super().__init__(group)
        self.lives = 300
        self.image = pygame.transform.scale(self.image, (500, 500))
        self.rect = self.image.get_rect()
        self.rect.x = -540
        self.rect.y = -540
        self.shield = Shield(enemy_bullets)
        self.vulnerable = True
        self.next_gun = 0
        self.gun_coords = [(100, 500), (200, 500), (300, 500), (400, 500)]
        self.point = (0, 0)
        self.frames_to_reach = FPS * 6
        self.speed_x = int((self.point[0] - self.rect.x) / self.frames_to_reach)
        self.speed_y = int((self.point[1] - self.rect.y) / self.frames_to_reach)
        self.mask = pygame.mask.from_surface(self.image)
        self.attack_type = random.randint(1, 4)
    
    def appear(self):
        super().appear()
        
    def update(self, kill_em_all=False):
        kill_em_all = False
        attack = self.attack_type
        self.attack_type = 0
        ufo = Ufo(enemies)
        ufo.rect.x = self.gun_coords[self.next_gun][0]
        ufo.rect.y = self.gun_coords[self.next_gun][1]
        ufo.vulnerable = False
        ufo.image.set_alpha(0)
        ufo.attack_type = attack
        ufo.update(suicide=True)
        super().update()
        self.next_gun = (self.next_gun + 1) % 4
        self.attack_type = random.randint(1, 4)
        
            
       
background = load_image("sky_background.jpg")
background_x = 0
background_y = 950 - 2752
screen.blit(background, (0, background_y))
font = pygame.font.Font(None, 15)
score_text = [f"SCORE: {SCORE}"]
text_coord = -30
for line in score_text:
    string_rendered = font.render(line, 1, pygame.Color('red'))
    intro_rect = string_rendered.get_rect()
    text_coord += 30
    intro_rect.top = text_coord
    intro_rect.x = 15
    text_coord += intro_rect.height
screen.blit(string_rendered, (5, 5))
Player(player)
player.draw(screen)
Ufo(enemies)
ufo_timer = FPS * 3
pygame.display.flip()
while running:
    """if SCORE % 1500 == 0:
        enemies.empty()
        BossUfo(enemies)
        ufo_timer = -1"""
    screen.blit(background, (background_x, background_y))
    background_y += 2
    if background_y > 0:
        background_y = 950 - 2752
        text_y = 2752 - 945
    if not(ufo_timer):
        Ufo(enemies)
        ufo_timer = FPS * 3
    events_now = pygame.event.get()
    for event in events_now:
        if event.type == pygame.QUIT:
            running = False
    effects.update()
    player.update(events_now)
    enemies.update()
    enemy_bullets.update()
    player_bullets.update()
    score_text = [f"SCORE: {SCORE}"]
    for line in score_text:
        string_rendered = font.render(line, 1, pygame.Color('red'))
        intro_rect = string_rendered.get_rect()
        text_coord += 0
        intro_rect.top = text_coord
        intro_rect.x = 15
        text_coord += 0
    screen.blit(string_rendered, (5, 5))
    player.draw(screen)
    player_bullets.draw(screen)
    enemies.draw(screen)
    enemy_bullets.draw(screen)
    effects.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
    ufo_timer -= 1
pygame.quit()