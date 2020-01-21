import pygame, os, math, sys, random


pygame.init()
WIDTH = 500
HEIGHT = 950
FPS = 30
SIZE = WIDTH, HEIGHT
SCORE = 0
LIVES = 5
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


intro_text = ["SPACESHIP VS. UFOS", "",
              "", "", "",
              "New game", "", "", 
              "Choose difficulty", "", "",
              "Exit"]

fon = pygame.transform.scale(load_image("background.jpg", colorkey=-1), (423, 500))
screen.blit(fon, (600 - 423, 0))
font = pygame.font.Font(None, 30)
text_coord = 20
for line in intro_text:
    string_rendered = font.render(line, 1, pygame.Color('White'))
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
            elif 50 <= pygame.mouse.get_pos()[0] <= 220 and 278 <= pygame.mouse.get_pos()[1] <= 299:
                inner_running = True
                dif_text = ["", "", "", "", "", "Hard", "", "", "Hard", "", "", "Hard"]
                screen.fill((0, 0, 0))
                screen.blit(fon, (600 - 423, 0))
                text_coord = 20
                for line in dif_text:
                    string_rendered = font.render(line, 1, pygame.Color('White'))
                    intro_rect = string_rendered.get_rect()
                    text_coord += 10
                    intro_rect.top = text_coord
                    intro_rect.x = 50
                    text_coord += intro_rect.height
                    screen.blit(string_rendered, intro_rect)
                pygame.display.flip()                
                while inner_running:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            terminate()
                        elif event.type == pygame.MOUSEBUTTONDOWN: 
                            if 50 <= pygame.mouse.get_pos()[0] <= 95 and \
                               (185 <= pygame.mouse.get_pos()[1] <= 206 or \
                                278 <= pygame.mouse.get_pos()[1] <= 299 or \
                                371 <= pygame.mouse.get_pos()[1] <= 392):
                                screen.fill((0, 0, 0))
                                screen.blit(fon, (600 - 423, 0))                            
                                text_coord = 20
                                for line in intro_text:
                                    string_rendered = font.render(line, 1, pygame.Color('White'))
                                    intro_rect = string_rendered.get_rect()
                                    text_coord += 10
                                    intro_rect.top = text_coord
                                    intro_rect.x = 50
                                    text_coord += intro_rect.height
                                    screen.blit(string_rendered, intro_rect)  
                                inner_running = False
                    pygame.display.flip()
                    clock.tick(FPS)                
            elif 50 <= pygame.mouse.get_pos()[0] <= 89 and 371 <= pygame.mouse.get_pos()[1] <= 392:
                terminate()
    pygame.display.flip()
    clock.tick(FPS)

screen = pygame.display.set_mode([WIDTH, HEIGHT])
screen.fill((0, 0, 255))
EXPLOSION_SOUND = pygame.mixer.Sound(file="explosionsound.wav")
SHIELD_SOUND = pygame.mixer.Sound(file="shieldbreaks.wav")
BACKGROUND_MUSIC = pygame.mixer.Sound(file="backgroundmusic.wav")
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
    image = load_image("shield.png", colorkey=-1)
    
    def __init__(self, group):
        super().__init__(group)
        self.image = Shield.image
        self.image = pygame.transform.flip(self.image, False, True)
        self.image = pygame.transform.scale(self.image, (500, 33))
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 150
        self.lives = 500
        self.mask = pygame.mask.from_surface(self.image)
        self.damage = 0
        self.exist = True
        
    def update(self):
        if pygame.sprite.spritecollide(self, player_bullets, False):
            for collision in pygame.sprite.spritecollide(self, player_bullets, False):
                if pygame.sprite.collide_mask(self, collision):
                    self.lives -= collision.damage
                    collision.exist = False
        if pygame.sprite.spritecollide(self, player, False):
            for collision in pygame.sprite.spritecollide(self, player, False):
                if pygame.sprite.collide_mask(self, collision):
                    collision.rect.y = pygame.sprite.collide_mask(self, collision)[0]
        if self.lives < 1:
            SHIELD_SOUND.play()
            self.kill()
            
            
class Wall(pygame.sprite.Sprite):
    image = load_image("lightning_wall.png", colorkey=-1)
    image = cut_sheet(image, 9, 1)
    
    def __init__(self, group, speed, x, y, verge):
        super().__init__(group)
        self.image = Wall.image[0]
        self.num_pic = 0
        self.image = pygame.transform.scale(self.image, (40, 1200))
        self.speed = speed
        self.damage = 0
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.exist = False
        self.rect.x = x
        self.rect.y = y
        self.verge = verge
    
    def update(self):
        if pygame.sprite.spritecollide(self, player, False):
            for collision in pygame.sprite.spritecollide(self, player, False):
                collision.rect.x += 10 * math.copysign(1, self.speed)
        if (self.rect.x - self.verge < 0 and self.speed > 0) or \
           (self.rect.x - self.verge > 0 and self.speed < 0):
            self.rect = self.rect.move(self.speed, 0)
        else:
            self.rect.x = self.verge
        x, y = self.rect.x, self.rect.y
        self.num_pic = (self.num_pic + 1) % 8
        self.image = Wall.image[self.num_pic]
        self.image = pygame.transform.scale(self.image, (40, 1200))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)  
        self.rect.x = x
        self.rect.y = y


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
        
    def update(self):
        if self.width > 0:
            self.width = self.width - self.speed
            self.image = pygame.transform.scale(self.image, (round(self.width) if self.width >= 0
                                                             else 0, self.height))
            self.rect = self.rect.move(round(self.speed / 2), 0)
            self.rect.width = round(self.width)
            self.mask = pygame.mask.from_surface(self.image)
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
        self.mask = pygame.mask.from_surface(self.image)
        
    def update(self):
        self.exist = True
        super().update()


class Player(pygame.sprite.Sprite):
    image = load_image("spaceship.jpg", colorkey=-1)
    
    def __init__(self, group):
        super().__init__(group)
        self.lives = 5
        self.image = Player.image
        self.image = pygame.transform.scale(self.image, (60, 50))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.vulnerable = True
        self.vulnerable_timer = None
        self.death_timer = 15
        self.speed = 7
        self.delay = 0
        self.rect.x = 220
        self.rect.y = 900
        
    def update(self, args):
        global LIVES
        if not(self.delay):
            if pygame.mouse.get_pressed()[0]:
                PlayerBullet(player_bullets, self.rect.x + 10, self.rect.y + 40, 10, 50, 50, 1, 
                             "bullet", self.vulnerable)
                PlayerBullet(player_bullets, self.rect.x + 40, self.rect.y + 40, 10, 50, 50, 1,
                             "bullet", self.vulnerable)
                self.delay = FPS // 6
            elif pygame.mouse.get_pressed()[2]:
                PlayerBullet(player_bullets, self.rect.x + 8, self.rect.y + 35, 15, 25, 25, 8,
                              "missile", self.vulnerable)
                PlayerBullet(player_bullets, self.rect.x + 37, self.rect.y + 35, 15, 25, 25, 8,
                              "missile", self.vulnerable)
                self.delay = FPS                
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
        if self.rect.y < 200:
            self.rect.y = 200
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
                        if collision.damage:
                            self.lives -= collision.damage
                            LIVES -= 1
                            collision.exist = False 
                            self.vulnerable = False
                            self.vulnerable_timer = FPS * 4
                            self.image.set_alpha(128)
                            break
        if self.lives < 1:
            if self.death_timer == 15:
                EXPLOSION_SOUND.play()
                Explosion(effects, self.rect.x, self.rect.y, (60, 50))
                self.vulnerable = False
                self.image.set_alpha(0)
                self.death_timer -= 1
            elif self.death_timer == 0:
                terminate()
            else:
                self.death_timer -= 1
        if self.delay:
            self.delay -= 1
            
            
class Ufo(pygame.sprite.Sprite):
    images = load_image("ufo.jpg", colorkey=-1)
    images = cut_sheet(images, 4, 5)
    del images[5]
    del images[9]
    del images[16]
    del images[16]
    
    def __init__(self, group, is_boss=False):
        super().__init__(group)
        self.lives = random.randint(20, 35)
        self.image = Ufo.images[0]
        self.num_pic = 0
        self.imupt = 2 #image update
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
        self.is_boss = False
        if is_boss:
            self.lives = 500
            self.image = pygame.transform.scale(self.image, (500, 100))
            self.rect = self.image.get_rect()
            self.rect.x = 0
            self.rect.y = -500
            self.mask = pygame.mask.from_surface(self.image)
            self.attack_type = random.randint(1, 4)
            self.is_boss = True
            self.gun_coords = [(100, 100), (200, 100), (300, 100), (400, 100)]
            self.next_gun = 0   
    
    def appear(self):
        if not(self.point):
            self.point = (random.randint(0, 400), random.randint(0, 100))
            if self.is_boss:
                self.point = (0, 25)
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
            if self.is_boss:
                Shield(enemy_bullets)
                self.wall1 = Wall(enemy_bullets, 2, -40, 50, 60)
                self.wall2 = Wall(enemy_bullets, -2, 540, 50, 400)
     
    def update(self, kill_em_all=False):
        global SCORE, boss_on_screen, ufo_timer
        attack_x, attack_y = self.rect.x, self.rect.y
        if self.is_boss:
            attack_x, attack_y = self.gun_coords[self.next_gun]
        if self.speed_x or self.speed_y:
            self.appear()
        if pygame.sprite.spritecollide(self, player_bullets, False):
            for collision in pygame.sprite.spritecollide(self, player_bullets, False):
                if pygame.sprite.collide_mask(self, collision) and self.vulnerable:
                    self.lives -= collision.damage
                    collision.exist = False
        if self.lives > 0 and not(self.delay):
            if self.attack_type == 1:
                if self.start_in:
                    pygame.draw.circle(screen, pygame.Color('white'), (attack_x + 40, attack_y + 100), 
                                       round(self.charge_speed * (self.size_now + 1)))
                    self.size_now += 1
                    self.start_in -= 1
                else:
                    LaserBeam(enemy_bullets, attack_x + 15, attack_y + 100, HEIGHT - 
                              self.rect.y)   
                    self.start_in = FPS * 2
                    self.size_now = 0                    
                    self.delay = FPS // 6 if self.is_boss else FPS * 2
                    self.attack_type = random.randint(1, 3 if not(self.is_boss) else 4)
                    if self.is_boss:
                        self.next_gun = random.randint(0, 3)
            elif self.attack_type == 2:
                k = not(random.choice([True, False]))
                if not(k):
                    rot = random.randint(1, 3) / 100
                    p = random.randint(15, 25)
                else:
                    p = random.randint(45, 75)
                for _ in range(p):
                    SpinBullet(enemy_bullets, attack_x + 80, attack_y + 80, 
                               _ / 180 * math.pi * 180 / p, random.randint(1, 6) / 200 if k else rot)
                self.delay = FPS if self.is_boss else FPS * 5
                self.attack_type = random.randint(1, 3 if not(self.is_boss) else 4)
                if self.is_boss:
                    self.next_gun = random.randint(0, 3)
            elif self.attack_type == 3:
                p = random.randint(15, 25)
                for _ in range(p):
                    SpinBullet(enemy_bullets, attack_x + 80, attack_y + 80, 
                               _ / 180 * math.pi * 180 / p)
                self.delay = FPS if self.is_boss else FPS * 4        
                self.attack_type = random.randint(1, 3 if not(self.is_boss) else 4)
                if self.is_boss:
                    self.next_gun = random.randint(0, 3)
            elif self.attack_type == 4:
                Meteor(enemy_bullets, x=self.gun_coords[self.next_gun][0])
                self.delay = FPS // 3
                self.attack_type = random.randint(1, 3 if not(self.is_boss) else 4)
                if self.is_boss:
                    self.next_gun = random.randint(0, 3)
        self.imupt -= 1
        if not(self.imupt):
            self.num_pic = (self.num_pic + 1) % 16
            self.image = Ufo.images[self.num_pic]
            self.image = pygame.transform.scale(self.image, (500, 100) if self.is_boss else (80, 80))
            self.mask = pygame.mask.from_surface(self.image)
            self.imupt = 2
        if self.delay:
            self.delay -= 1
        if self.lives < 1 or kill_em_all:
            if not(kill_em_all):
                SCORE += 100
            EXPLOSION_SOUND.play()
            Explosion(effects, self.rect.x, self.rect.y, (500, 100) if self.is_boss else (80, 80))
            if self.is_boss:
                ufo_timer = FPS * 5
                self.wall1.kill()
                self.wall2.kill()
                boss_on_screen = False
                SCORE += 1500
            self.kill()
        
       
background = load_image("sky_background.jpg")
background_x = 0
background_y = 950 - 2752
screen.blit(background, (0, background_y))
font = pygame.font.Font(None, 15)
score_text = [f"SCORE: {SCORE} LIVES: {LIVES}"]
text_coord = -30
for line in score_text:
    string_rendered = font.render(line, 1, pygame.Color('red'))
    intro_rect = string_rendered.get_rect()
    text_coord += 30
    intro_rect.top = text_coord
    intro_rect.x = 15
    text_coord += intro_rect.height
    screen.blit(string_rendered, intro_rect)
Player(player)
player.draw(screen)
boss_on_screen = False
ufo_timer = FPS * 3
BACKGROUND_MUSIC.play(loops=9999)
pygame.display.flip()
while running:
    if SCORE and SCORE % 1500 == 0 and not(boss_on_screen):
        enemies.update(True)
        Ufo(enemies, is_boss=True)
        ufo_timer = -1
        boss_on_screen = True
    screen.blit(background, (background_x, background_y))
    background_y += 2
    if background_y > 0:
        background_y = 950 - 2752
        text_y = 2752 - 945
    if not(ufo_timer):
        Ufo(enemies)
        ufo_timer = FPS * 3
    pygame.draw.line(screen, (255, 255, 255), (460, 10), (490, 40))
    pygame.draw.line(screen, (255, 255, 255), (460, 40), (490, 10))
    events_now = pygame.event.get()
    for event in events_now:
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP:
            if pygame.mouse.get_pressed()[0]:
                if 460 <= pygame.mouse.get_pos()[0] <= 500 and 0 <= pygame.mouse.get_pos()[1] <= 40:
                    running = False
    effects.update()
    player.update(events_now)
    enemies.update()
    enemy_bullets.update()
    player_bullets.update()
    score_text = [f"SCORE: {SCORE} LIVES: {LIVES}"]
    for line in score_text:
        string_rendered = font.render(line, 1, pygame.Color('red'))
        intro_rect = string_rendered.get_rect()
        text_coord += 0
        intro_rect.top = text_coord
        intro_rect.x = 15
        text_coord += 0
        screen.blit(string_rendered, intro_rect)
    player.draw(screen)
    player_bullets.draw(screen)
    enemies.draw(screen)
    enemy_bullets.draw(screen)
    effects.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
    ufo_timer -= 1
pygame.quit()
