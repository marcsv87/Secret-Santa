"""
This simple example is used for the line-by-line tutorial
that comes with pygame. It is based on a 'popular' web banner.
Note there are comments here, but for the full explanation,
follow along in the tutorial.
"""


#Import Modules
import os, pygame
from pygame.locals import *
from pygame.compat import geterror
import random, time
from functools import reduce

if not pygame.font: print ('Warning, fonts disabled')
if not pygame.mixer: print ('Warning, sound disabled')

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')

#functions to create our resources
def load_image(name, colorkey=None):
    fullname = os.path.join(data_dir, name)
    try:
        image = pygame.image.load(fullname)
        image = pygame.transform.scale(image, (40,80))
    except pygame.error:
        print ('Cannot load image:', fullname)
        raise SystemExit(str(geterror()))
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join(data_dir, name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error:
        print ('Cannot load sound: %s' % fullname)
        raise SystemExit(str(geterror()))
    return sound


#classes for our game objects
class Fist(pygame.sprite.Sprite):
    """moves a clenched fist on the screen, following the mouse"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect = load_image('fist.bmp', -1)
        self.punching = 0

    def update(self):
        "move the fist based on the mouse position"
        pos = pygame.mouse.get_pos()
        self.rect.midtop = pos
        
#        if self.punching:
#            self.rect.move_ip(5, 10)

    def punch(self, target):
        "returns true if the fist collides with the target"
        if not self.punching:
            self.punching = 1
            hitbox = self.rect.inflate(-5, -5)
            return hitbox.colliderect(target.rect)

    def unpunch(self):
        "called to pull the fist back"
        self.punching = 0


class Character(pygame.sprite.Sprite):
    """moves a monkey critter across the screen. it can spin the
       monkey when it is punched."""
    def __init__(self, img='chimp.bmp', move=9, init_x = 10, init_y = 10):
        pygame.sprite.Sprite.__init__(self) #call Sprite intializer
        self.image, self.rect = load_image(img, -1)
        self.screen = pygame.display.get_surface()
        self.area = self.screen.get_rect()
        self.rect.topleft = init_x, init_y
        self.move = move
        self.speed = [move, move]
        self.dizzy = 0

    def update(self):
        "walk or spin, depending on the monkeys state"
        if self.dizzy:
            self._spin()
        else:
            self._walk2()

    def _walk(self):
        "move the monkey across the screen, and turn at the ends"
        newpos = self.rect.move((self.move, 0))
        if self.rect.left < self.area.left or \
            self.rect.right > self.area.right:
            self.move = -self.move
            newpos = self.rect.move((self.move, 0))
            self.image = pygame.transform.flip(self.image, 1, 0)
        self.rect = newpos
    
    def _walk2(self):
        width, height = self.screen.get_size()
        #speed = [self.move, self.move]
        newpos = self.rect.move(self.speed)
        bounce = False
        if self.rect.left <0 or self.rect.right>width:
            self.speed[0] = -self.speed[0]
            bounce = True
        if self.rect.top<0 or self.rect.bottom>height:
            self.speed[1] = -self.speed[1]
            bounce = True
        if bounce: 
            newpos = self.rect.move(self.speed)
        self.rect = newpos
        
    def _spin(self):
        "spin the monkey image"
        center = self.rect.center
        self.dizzy = self.dizzy + 12
        if self.dizzy >= 360:
            self.dizzy = 0
            self.image = self.original
        else:
            rotate = pygame.transform.rotate
            self.image = rotate(self.original, self.dizzy)
        self.rect = self.image.get_rect(center=center)

    def punched(self):
        "this will cause the monkey to start spinning"
        if not self.dizzy:
            self.dizzy = 1
            self.original = self.image


def main():
    """this function is called when the program starts.
       it initializes everything it needs, then runs in
       a loop until the function returns."""
    #Initialize Everything
    pygame.init()
    screen = pygame.display.set_mode((960, 640))
    pygame.display.set_caption('Monkey Fever')
    pygame.mouse.set_visible(0)

    #Create The Backgound
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))
    
    # initialize punctiation
    puntuacio = 0

    #Put Text On The Background, Centered
    if pygame.font:
        font = pygame.font.Font(None, 36)
        text = font.render("Puntuacio: "+str(puntuacio), 1, (10, 10, 10))
        textpos = text.get_rect(centerx=background.get_width()/2)
        #background.blit(text, textpos)

    #Display The Background
    screen.blit(background, (0, 0))
    screen.blit(text, textpos)
    pygame.display.flip()

    #Prepare Game Objects
    clock = pygame.time.Clock()
    whiff_sound = load_sound('whiff.wav')
    punch_sound = load_sound('punch.wav')
    chimp = Character(move = random.randint(2,10))
    fist = Fist()
    allsprites = pygame.sprite.RenderPlain((fist, chimp))
    enemies = [chimp]
    init_time = time.time()
    #Main Loop
    going = True
    there = False
    while going:
        clock.tick(60)
        if time.time()-init_time>5 and not there:
            there = True
            chimp2 = Character(img='erola.png', move = random.randint(2,10))
            allsprites.add(chimp2)
            enemies.append(chimp2)
            #enemies.reverse()
        
        if pygame.font:
            font = pygame.font.Font(None, 36)
            text = font.render("Puntuacio: "+str(puntuacio), 1, (10, 10, 10))
            textpos = text.get_rect(centerx=background.get_width()/2)

        #Handle Input Events
        for event in pygame.event.get():
            if event.type == QUIT:
                going = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                going = False
            elif event.type == MOUSEBUTTONDOWN:
                punched = False
                for x in enemies:
                    if fist.punch(x):
                        punch_sound.play()
                        x.punched()
                        puntuacio = puntuacio+10
                        punched = True
                    fist.unpunch()
                if not punched:
                    whiff_sound.play() #miss
                    puntuacio -= 5                   
#                if fist.punch(chimp):
#                    #if punch:
#                    punch_sound.play() #punch
#                    chimp.punched()
#                    puntuacio = puntuacio + 10
#                else:
#                    whiff_sound.play() #miss
#                    puntuacio -= 5
            elif event.type == MOUSEBUTTONUP:
                fist.unpunch()

        allsprites.update()
        if puntuacio <=-200:
            #print('game over')
            going = False
        elif puntuacio >= 200:
            #print('winner')
            going = False
#        else:
        #Draw Everything
        screen.blit(background, (0, 0))
        screen.blit(text, textpos)

        allsprites.draw(screen)
        pygame.display.flip()

    pygame.quit()

#Game Over


#this calls the 'main' function when this script is executed
if __name__ == '__main__':
    main()
