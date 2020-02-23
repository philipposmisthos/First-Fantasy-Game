import pygame
import time
import math
import threading
from PIL import Image

system_condition=pygame.init()

if system_condition[1]!=0:              
    print("Error while running game")
    pygame.quit()

pygame.mixer.init()


class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = simple_camera
        self.state = pygame.Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)
        
            
def simple_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t, _, _ = -l+HALF_WIDTH, -t+HALF_HEIGHT, w, h

    l = min(0, l)                           # left
    l = max(-(camera.width-WIN_WIDTH), l)   #  right
    t = max(-(camera.height-WIN_HEIGHT), t) #  bottom
    t = min(0, t)                           #  top
    return pygame.Rect(l, t, w, h)



    

class Entity(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

class Player(Entity):
    can_attack=True
    direction="right"
    name=""
    last_x=0
    counter=0
    end_of_level=0
    lives=3
    timer=0
    mov_timer=3
    hit=False
    image=None
    x=0
    y=0
    action_sound=True
    key_taken=False
    death_played=False
    
    def __init__(self, x, y, im, name):
        Entity.__init__(self)
        self.name=name
        self.xvel = 0
        self.yvel = 0
        self.onGround = False
        self.image = im
        self.image.convert()
        self.rect = pygame.Rect(x, y, im.get_rect().size[0], im.get_rect().size[1])
        self.x=x
        self.y=y
        
    def update(self, up, left, right, attack, platforms, num):
        
        if self.lives<=0:
            self.kill()
                
        if attack:
            if self.can_attack:
                if self.name=="mage":
                    for i in range(number_of_players):
                        if self==player[i]:
                            hit_channels[i].play(weapon_sounds[2])
                    m=Magic(magic,self)
                
                elif self.name=="warrior":
                    for i in range(number_of_players):
                        if self==player[i]:
                            hit_channels[i].play(weapon_sounds[1])
                    m=Sword(self)
                    
                else:
                    for i in range(number_of_players):
                        if self==player[i]:
                            hit_channels[i].play(weapon_sounds[0])
                    m=Crossbow(self)
                    
                moving_attacks.add(m)
                self.can_attack=False
       
        if up:
            
            if self.onGround: 
                self.yvel -= 11.7
        
        if left:
            self.direction="left"
            self.image=player_sprites_left[num][self.counter]
            if self.mov_timer<=0:
                self.counter = (self.counter + 1) % len(player_sprites_left[num])
                self.mov_timer=3
            else:
                self.mov_timer-=1
            self.xvel = -8
        if right:
            self.direction="right"
            self.image=player_sprites_right[num][self.counter]
            if self.mov_timer<=0:
                self.counter = (self.counter + 1) % len(player_sprites_right[num])
                self.mov_timer=3
            else:
                self.mov_timer-=1
            self.xvel = 8
            
        if not self.onGround:
            
            self.yvel += 0.6
            if self.yvel>0:
                self.yvel+=0.9
            
            if self.yvel > 40:
                self.yvel = 40
        if not(left or right):
            self.counter=0
            self.xvel = 0
        
        
        self.rect.left += self.xvel
        self.x+= self.xvel
        self.collide(self.xvel, 0, platforms,enemies,num) 
        self.rect.top += self.yvel
        self.y+=self.yvel
        self.onGround = False;
        self.collide(0, self.yvel, platforms,enemies,num)
        self.action_sound=True
        
        if self.rect[0] <= 0 :
                self.rect[0]=0
                self.counter=0

        if self.rect[0]+32>=total_level_width:
                self.rect[0]=total_level_width-32
                if index==DessertLevel:
                    self.end_of_level=1
        
        if self.rect[0]+32<total_level_width:
                self.end_of_level=0
        if self.rect[1]+32 > WIN_HEIGHT :
            if not self.key_taken:
                self.play_sound(self,"death")
                self.lives=0
                self.kill()
            else:
                self.end_of_level=1
                self.image=None
                          
        
    def collide(self, xvel, yvel, platforms,enemies,num):
        for p in platforms:
            if p.identity!="keno":
             if pygame.sprite.collide_rect(self, p):
                
                    
                if p.identity=="key":
                    
                    p.kill()
                    platforms.remove(p)
                    entities.remove(p)
                    for i in range(number_of_players):
                        if player[i].alive:
                            player[i].key_taken=True
                    
                if p.identity=="lock":
                    if self.key_taken:
                        p.kill()
                        platforms.remove(p)
                        entities.remove(p)
                if xvel > 0:
                    self.rect.right = p.rect.left
                    xvel=0
                if xvel < 0:
                    self.rect.left = p.rect.right
                    xvel=0
                if yvel > 0:
                    self.rect.bottom = p.rect.top
                    if p.identity!="key":
                        self.onGround = True
                        self.yvel = 0
                if yvel < 0:
                    self.rect.top = p.rect.bottom
                    self.yvel=0
                if p.identity=="spikes":
                    self.play_sound("death",num)
                    self.lives=0
                    self.kill()
                    
                    
                
                    
        if not self.hit:
         for e in enemies:
            if pygame.sprite.collide_rect(self, e):
                self.lives-=1
                if self.lives>0:
                        
                        self.play_sound("hit",num)
                else:
                        
                        self.play_sound("death",num) 
                if self.rect[0]>e.rect[0]:
                    self.rect[0]+=50
                elif self.rect[0]<e.rect[0]:
                    self.rect[0]-=50
                self.hit=True
                self.timer=100
                break
         
        else:
            self.timer-=1
            if self.timer<=0:
                self.hit=False
                
    def play_sound(self,action,num):
        if self.name=="warrior":
            if action=="death":
                channels[num].play(woman_death)
            elif action=="hit":
                channels[num].play(woman_hit)
        elif self.name=="mage":
            if action=="death":
                channels[num].play(old_death)
            elif action=="hit":
                channels[num].play(old_hit)
        else:
            if action=="death":
                channels[num].play(man_death)
            elif action=="hit":
                channels[num].play(man_hit)
        self.action_sound=False
            
        
class Enemy(Entity):
    can_attack=True
    lives=3
    name=""
    x=0
    y=0
    direction="left"
    mov_left=None
    mov_right=None
    xvel=0
    yvel=0
    onGround=False
    vel=0
    distance=0
    counter=0
    timer=0
    up_down=0
    half=False
    rounds=0
    falling=False
    attack_timer=13
    can_move=True
    
    def __init__(self,x,y,name):
        Entity.__init__(self)
        self.x=x
        self.y=y
        self.name=name
        if name=="Boss":
            self.mov_left=boss_left
            self.mov_right=boss_right
            self.image=boss_left[0]
            self.lives=30
        if name=="snake":
            self.mov_left=snake_left
            self.mov_right=snake_right
            self.image=snake_left[0]
            self.xvel=3
            self.yvel=0
        if name=="wolf":
            self.mov_left=wolf_left
            self.mov_right=wolf_right
            self.image=wolf_left[0]
            self.xvel=5
            self.yvel=0
        if name=="dust_fairy":
            self.mov_left=dust_fairy_left
            self.mov_right=dust_fairy_right
            self.image=dust_fairy_left[0]
            self.yvel=0
            self.xvel=0
        if name=="skeleton":
            self.mov_left=skeleton_left
            self.mov_right=skeleton_right
            self.image=skeleton_left[0]
            self.xvel=3
            self.yvel=0
        
        self.image.convert()
        self.rect = pygame.Rect(x, y, self.image.get_rect().size[0], self.image.get_rect().size[1]) 

    def update(self):
        if self.lives<=0:
            if self.name=="Boss":
                level_completed[level_index]=True
                background_channel.play(boss_death)
            enemies.remove(self) 
            self.kill()
            
                
        if self.name in ["wolf","snake"]:
            for i in player:
                if i.alive():
                    self.distance=self.rect[0]-i.rect[0]
                    if self.distance<0:
                        self.direction="right"
                    elif self.distance>0:
                        self.direction="left"
                    else:
                        self.direction=""
                        self.counter=0
                    break
                
            if not self.onGround:
                    self.yvel += 0.6
                    if self.yvel > 40:
                        self.yvel = 40
                    
        if self.name=="dust_fairy":
            for i in player:
                if i.alive():
                    self.distance=self.rect[0]-i.rect[0]
                    if self.distance<0:
                        self.direction="right"
                    elif self.distance>0:
                        self.direction="left"
                    else:
                        self.direction=""
                        self.counter=0
                    if self.distance<250 and self.distance>-250:
                        if self.can_attack:
                            a=Stone(stone,self)
                            moving_attacks.add(a)
                            self.can_attack=False
                        break
            
           
                    
        if self.name=="Boss":
            if self.lives<=15:
                if not self.half:
                    background_channel.stop()
                    self.half=True
                self.xvel=15
            else:
                self.xvel=10



            if self.rounds==3:
                self.can_move=False
                self.xvel=0
                if self.attack_timer>0:
                    self.attack_timer-=1
                else:
                    if not self.falling:
                        self.yvel=-8
                        self.falling=True
                    
        if self.direction=="left":
                self.vel = -self.xvel
                self.image = self.mov_left[self.counter]
                if self.timer<=0:
                    self.counter = (self.counter + 1) % len(self.mov_left)
                    self.timer=7
                else:
                    self.timer-=1
                    
        elif self.direction=="right":
                self.vel = self.xvel
                self.image = self.mov_right[self.counter]
                if self.timer<=0:
                    self.counter = (self.counter + 1) % len(self.mov_right)
                    self.timer=5
                else:
                    self.timer-=1
                    
        else:
                self.vel=0

        if self.can_move:           
            self.rect.left += self.vel
            self.collide(self.vel, 0, platforms) 
        self.rect.top += self.yvel
        if self.yvel==-6:
            self.yvel=2
        self.onGround = False;
        self.collide(0, self.yvel, platforms)

        if self.rect[1]+32 > WIN_HEIGHT :
            self.lives=0
            self.kill()
            
    def collide(self, xvel, yvel, platforms):
        for p in platforms:
            if pygame.sprite.collide_rect(self, p):
                if p.identity=="keno":
                    if self.name in ["skeleton","Boss"]:

                        if self.direction=="right":
                            self.direction="left"
                    
                        elif self.direction=="left":
                            self.direction="right"

                        if self.name=="Boss":
                            self.rounds+=1
                        
                if xvel > 0:
                    self.rect.right = p.rect.left
                    xvel=0
                if xvel < 0:
                    self.rect.left = p.rect.right
                    xvel=0
                if yvel > 0:
                    if self.name=="Boss":
                        if self.rounds==3:
                            boss_attack.play(Quake)
                            z=Boss_Stones(Boss,0)
                            moving_attacks.add(z)
                            self.rounds=0
                            self.falling=False
                            if not self.half:
                                self.attack_timer=13
                            else:
                                self.attack_timer=9
                            
                    self.rect.bottom = p.rect.top
                    self.onGround = True
                    self.yvel = 0
                if yvel < 0:
                    
                    self.rect.top = p.rect.bottom
                    self.yvel=40
                
class Platform(Entity):
    x=0
    y=0
    identity=""
    direction=""
    vel=0
    xvel=0
    yvel=0
    onGround=False
    
    def __init__(self, x, y,identity):
        Entity.__init__(self)
        self.identity=identity
        if identity=="next":
            self.image= pygame.Surface((32,32),pygame.SRCALPHA)
        if identity=="lock":
            self.image=lock
            self.image.convert()
            self.rect = pygame.Rect(x, y, self.image.get_rect().size[0], self.image.get_rect().size[1])
        if identity=="key":
            self.image=key
            self.image.convert()
            self.rect = pygame.Rect(x, y, self.image.get_rect().size[0], self.image.get_rect().size[1])
        if identity=="gate":
            self.image=gate
            self.image.convert()
            self.rect = pygame.Rect(x, y, self.image.get_rect().size[0], self.image.get_rect().size[1])
        if identity=="rock":
            self.image=rock
            self.image.convert()
            self.rect = pygame.Rect(x, y, self.image.get_rect().size[0], self.image.get_rect().size[1])
        elif identity=="spikes":
            self.image=spikes
            self.image.convert()
            self.rect = pygame.Rect(x, y, self.image.get_rect().size[0], self.image.get_rect().size[1])
        elif identity=="sand":
            self.image=sand
        elif identity=="keno":
            self.image= pygame.Surface((32,32),pygame.SRCALPHA)
            
        self.image.convert()
        self.rect = pygame.Rect(x, y, self.image.get_rect().size[0], self.image.get_rect().size[1])
        self.x=x
        self.y=y

class Stone(Entity):
    image=""
    xvel=0
    yvel=0
    x=0
    y=0
    distance_sum=0
    owner=None
    target=None
    degree=0
    
    def __init__(self,im,owner):
        Entity.__init__(self)
        self.image=im
        self.owner=owner
        if owner.direction=="left":
            self.x=owner.rect[0]
            self.xvel=-4
        elif owner.direction=="right":
            self.x=owner.rect[0]
            self.xvel=4
        
        self.image.convert()
        self.y=owner.rect[1]
        self.rect=pygame.Rect(self.x, self.y, im.get_rect().size[0], im.get_rect().size[1])
        for i in player:
            if i.alive():
                self.target=i
                break
        
        
    def update(self):
        self.y=0
            
        if self.distance_sum>=200:
            moving_attacks.remove(self)
            self.owner.can_attack=True
            self.kill()
        else:
            if self.target.alive():
                if self.target.rect[1]>self.rect[1]:
                    self.y+=4
                elif self.target.rect[1]<self.rect[1]:
                    self.y-=4
                
        self.rect.left += self.xvel
        self.rect.top += self.y
        self.distance_sum+=5
        self.collide()

    def collide(self):
        for i in range(number_of_players):
            if player[i].alive():
                if pygame.sprite.collide_rect(self, player[i]):
                    if not player[i].hit:
                        player[i].lives-=1
                        if player[i].lives>0:
                            player[i].play_sound("hit",i)
                        else:
                            player[i].play_sound("death",i)
                    if player[i].rect[0]>self.rect[0]:
                        player[i].rect[0]+=50
                    elif player[i].rect[0]<self.rect[0]:
                        player[i].rect[0]-=50
                    player[i].hit=True
                    self.owner.can_attack=True
                    moving_attacks.remove(self)
                    self.kill()
                
class Magic(Entity):
    image=""
    xvel=0
    x=0
    y=0
    distance_sum=0
    
    def __init__(self,image,owner):
        Entity.__init__(self)
        
        self.owner=owner
        self.image=image
        if owner.direction=="left":
            self.x=owner.rect[0]-50
            self.xvel=-8
        elif owner.direction=="right":
            self.x=owner.rect[0]+7
            self.xvel=8
            
        self.image.convert()
        self.y=owner.rect[1]-5
        self.rect = pygame.Rect(self.x, self.y, image.get_rect().size[0], image.get_rect().size[1])
            
    def update(self, enemies):
        
         self.rect.left += self.xvel
         self.distance_sum += self.xvel

         if self.distance_sum >=250 or self.distance_sum<=-250:
             moving_attacks.remove(self)
             self.owner.can_attack=True
             self.kill()
       
         self.collide(enemies)
        
         if self.rect[0]+32>=total_level_width:
             self.kill()
             self.owner.can_attack=True
             moving_attacks.remove(self)
            
         if self.rect[0] <= 0 :
            moving_attacks.remove(self)
            self.owner.can_attack=True
            self.kill()

    def collide(self, enemies):
        for p in enemies:
            if pygame.sprite.collide_rect(self, p):
               if p.name=="Boss":
                   boss_attack.stop()
                   channel_boss.play(boss_hit)
               p.lives-=1    
               self.kill()
               self.owner.can_attack=True
               moving_attacks.remove(self) 
                    
class Sword(Entity):
    image=""
    owner=None
    timer=2
    def __init__(self,owner):
        Entity.__init__(self)
        
        self.owner=owner
        if owner.direction=="left":
            self.x=owner.rect[0]-43
            self.image=sword_left
        elif owner.direction=="right":
            self.x=owner.rect[0]+15
            self.image=sword_right
        self.image.convert()

        self.y=owner.rect[1]+14
        self.rect = pygame.Rect(self.x, self.y, self.image.get_rect().size[0], self.image.get_rect().size[1])
        self.rect[1]=owner.rect[1]+14
        
    def update(self,enemies):
        self.rect[1]=self.owner.rect[1]+14
        self.timer-=1
        
        if self.timer!=0:
            if self.owner.direction=="left":
                self.rect[0] = self.owner.rect[0]-43
            else: 
                self.rect[0] = self.owner.rect[0]+14
            self.collide(enemies)
            
        else:
            self.kill()
            self.owner.can_attack=True
            moving_attacks.remove(self)
        
    def collide(self, enemies):
        for p in enemies:
            if pygame.sprite.collide_rect(self, p):
                if p.name=="Boss":
                   boss_attack.stop()
                   channel_boss.play(boss_hit)
                p.lives-=1
                
class Crossbow(Entity):
    xvel=0
    shot=False
    image=""
    owner=None
    timer=3
    distance=0
    
    def __init__(self,owner):
        Entity.__init__(self)
        
        self.owner=owner
        if owner.direction=="left":
            self.x=owner.rect[0]-43
            self.image=loaded_left
        elif owner.direction=="right":
            self.x=owner.rect[0]+15
            self.image=loaded_right
        self.image.convert()

        self.y=owner.rect[1]+14
        self.rect = pygame.Rect(self.x, self.y, self.image.get_rect().size[0], self.image.get_rect().size[1])  
        self.rect[1]=owner.rect[1]+14
        
    def update(self,enemies):
        if self.timer>=0:
            self.rect[1]=self.owner.rect[1]+14
            if self.owner.direction=="left":
                self.rect[0] = self.owner.rect[0]-42
            else: 
                self.rect[0] = self.owner.rect[0]+14
            self.timer-=1
        
        elif self.timer<0 and self.timer>=-2:
            self.rect[1]=self.owner.rect[1]+14
            if self.owner.direction=="left":
                self.rect[0] = self.owner.rect[0]-30
                self.image=unloaded_left
            else: 
                self.rect[0] = self.owner.rect[0]+14
                self.image=unloaded_right
            self.timer-=1
            
        elif self.timer<-2 and self.timer>=-6:
            if not self.shot:
             if self.owner.direction=="left":
                self.image=arrow_left
                self.xvel=-1
             else: 
                self.image=arrow_right
                self.xvel=1
             self.rect[1]+=5
             self.shot=True
            self.rect[2],self.rect[3] = self.image.get_rect().size[0], self.image.get_rect().size[1]  
            self.rect.left += self.xvel*9
            self.distance += self.xvel*9
            self.collide(enemies)

            if self.distance >=250 or self.distance<=-250:
                self.owner.can_attack=True
                moving_attacks.remove(self)
                self.kill() 
            
    def collide(self, enemies):
        for p in enemies:
            if pygame.sprite.collide_rect(self, p):
               self.owner.can_attack=True
               if p.name=="Boss":
                   boss_attack.stop()
                   channel_boss.play(boss_hit)
               p.lives-=1     
               moving_attacks.remove(self)            
               self.kill()
  

class Boss_Stones(Entity):
    image=None
    owner=None
    number=0
    creation_timer=2
    xvel=0
    created=False
    
    def __init__(self,owner,number):
        Entity.__init__(self)
        self.image=boss_stone[number]
        self.number=number
        self.owner=owner
        
        if owner.direction=="right":
            self.xvel=32
            self.rect=pygame.Rect(owner.rect[0]+93,owner.rect[1]+23,self.image.get_rect().size[0],self.image.get_rect().size[1])
        else:
            self.xvel=-32
            self.rect=pygame.Rect(owner.rect[0]-25,owner.rect[1]+23,self.image.get_rect().size[0],self.image.get_rect().size[1])

        
    def update(self):
        if self.creation_timer<=0:
                self.rect.left+=self.xvel
                self.collide(platforms)
                if self.number<2:
                    if not self.created:
                        self.created=True
                        moving_attacks.add(Boss_Stones(Boss,self.number+1))
                self.creation_timer=2
                    
        else:
                self.creation_timer-=1

    
    def collide(self,platforms):
        for p in platforms:
                if pygame.sprite.collide_rect(self, p):
                    if p.identity=="keno":
                        moving_attacks.remove(self)
                        if self.number==2:
                            self.owner.can_move=True
                            all_created=False
                            boss_attack.stop()
                        self.kill()
                        
        for i in range(number_of_players):
            if player[i].alive():
                if pygame.sprite.collide_rect(self, player[i]):
                    if not player[i].hit:
                        player[i].lives-=1
                        if player[i].lives>0:
                            player[i].play_sound("hit",i)
                        else:
                            boss_attack.stop()
                            player[i].play_sound("death",i)
                    if player[i].rect[0]>self.rect[0]:
                        player[i].rect[0]+=50
                    elif player[i].rect[0]<self.rect[0]:
                        player[i].rect[0]-=50
                    player[i].hit=True
                    
                    
class ControlButtonField:   #koumpia gia actions x6 (gia kathe player)
    
    player_no=0
    width=120
    height=30
    x_pos=0
    y_pos=0
    text=""
    def __init__(self,player_no,y_pos):    
        self.player_no=player_no
        self.y_pos=y_pos
        if player_no==0:
            self.x_pos=250
        else:
            self.x_pos=1050
        
    def check_click(self,(x,y)):
       if (x>=self.x_pos and x<self.x_pos+self.width) and (y>=self.y_pos and y<self.y_pos+self.height):
           return True
       else:
           return False
    
class ControllerButtonField: #koumpia gia controllers x2
    player_no=0
    x_pos=0
    text=""    
    y_pos=300    
    
    def __init__(self,player_no):
        self.player_no=player_no
        if(player_no==0):
            self.x_pos=330
        else:
            self.x_pos=1120

    def check_click(self,(x,y)): #elegxos gia patima koumpiwn
       if (x>=self.x_pos and x<self.x_pos+185) and (y>=self.y_pos and y<self.y_pos+30):
           pygame.draw.rect(screen,[255,0,0],[self.x_pos,self.y_pos,205,30],0)
           
           return True
       else:
           return False

def MainMenu_check(): #elegxos gia enter stin arxiki othoni
    
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            return True
        else:
            return False

DessertLevel=[
"                    K  B  K                                           ",
"                     RRRRR         P          W                       ",
"                                          RRRRR                       ",
"                                                                      ",
"               K  B K                                                 ",
"                RRRR                                                  ",
"                                    RRRR                  W           ",
"            R               RRRRR               RRRRR    RRRRRR       ",
"          FRR              RRRRRR                        RRRRRRR      ",
"         SSRRRSSSSSSSSSSSRRRRRRRRSSSSS       F           RRRRRRRR     ",
"DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD    RRRRRRRRRRRRR",]


Other_Level=[
"R    DDD  P          K    B   K        P                   W          ",
"R A  DDDD       F     RRRRRRRR      F      DDDDDDDDXXOXXDDDDDDDDDDDDDD",
"RRRRRDDDDD     RRRRR        P   RRRRR     DDDDDDDDD     DDDDDDDDDDDDDD",
"     DDDDDD                              DDDDDDDDDD     DDDDDDDDDDDDDD",
"     DDDDDDD          K B  K           SSDDDDDDDDDD     DDDDDDDDDDDDDD",
"     RRRRRRRRRRRRRR    RRRR           SSDDDDDDDDDDD     DDDDDDDDDDDDDD",
"                           K B  K    SSDDDDDDDDDDDD     DDDDDDDDDDDDDD",
"          KBK        KBK    RRRR    SSDDDDDDDDDDDDD     DDDDDDDDDDDDDD",
"           R          R            SSDDDDDDDDDDDDDD     DDDDDDDDDDDDDD",
"          RRR        RRR          SSDDDDDDDDDDDDDDD     DDDDDDDDDDDDDD",
"DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD     DDDDDDDDDDDDDD",
]


Boss_level=[


"DDDDDDDDDDDDS                SDDDDDDDDDDDDD",
"DDDDDDDDDDDDS      RRRR      SDDDDDDDDDDDDD",
"DDDDDDDDDDDDS                SDDDDDDDDDDDDD",
"DDDDDDDDDDDDS                SDDDDDDDDDDDDD",
"DDDDDDDDDDDDS  RR  SSSS  RR  SDDDDDDDDDDDDD",
"DDDDDDDDDDDDS                SDDDDDDDDDDDDD",
"DDDDDDDDDDDDD                DDDDDDDDDDDDDD",
"DDDDDDDDDDDDD K        J   K DDDDDDDDDDDDDD",
"DDDDDDDDDDDDD  DDDDDDDDDDDD  DDDDDDDDDDDDDD",
"DDDDDDDDDDDDDSSDDDDDDDDDDDDSSDDDDDDDDDDDDDD",
"DDDDDDDDDDDDDSSDDDDDDDDDDDDSSDDDDDDDDDDDDDD",]

level_index=-1
#level_index=1
levels_all=[]

#levels_all.append(DessertLevel)
levels_all.append(Other_Level)
#levels_all.append(Boss_level)



level_completed=[False,False,False]



roles=("warrior","ranger","mage")

Boss=None
old_hit=pygame.mixer.Sound("old_hit.ogg")
old_death=pygame.mixer.Sound("old_death.ogg")
man_death=pygame.mixer.Sound("man_death.ogg")
man_hit=pygame.mixer.Sound("man_hit.ogg")
woman_hit=pygame.mixer.Sound("woman_hit.ogg")
woman_death=pygame.mixer.Sound("woman_death.ogg")
boss_hit=pygame.mixer.Sound("boss_hit.ogg")
boss_death=pygame.mixer.Sound("boss_death.ogg")
gameover_music=pygame.mixer.Sound("Gameover2.ogg")
ad_sel=pygame.mixer.Sound("Adellin.ogg")
dun_sel=pygame.mixer.Sound("Duncan.ogg")
fl_sel=pygame.mixer.Sound("Flint.ogg")


channel_player1=pygame.mixer.Channel(0)
channel_player2=pygame.mixer.Channel(1)
channel_hit1=pygame.mixer.Channel(5)
channel_hit2=pygame.mixer.Channel(6)
channel_boss=pygame.mixer.Channel(2)
channels=[channel_player1,channel_player2]
hit_channels=[channel_hit1,channel_hit2]
background_channel=pygame.mixer.Channel(4)
boss_attack=pygame.mixer.Channel(7)

tsakwnas=pygame.image.load("tsakwnas.png")

background_channel.set_volume(0.8)
hit_channels[0].set_volume(0.3)
hit_channels[1].set_volume(0.3)

victory_sound=pygame.mixer.Sound("Victory.ogg")

gameoveru=pygame.image.load("gameoveru.png")

entities = pygame.sprite.Group()
moving_attacks = pygame.sprite.Group()
enemies= pygame.sprite.Group()
platforms=[]

player_buttons=[]
playersa=[{}]
actions=[{}]

press_attack=pygame.image.load("press_attack.png")
keytaken=False
joysticksa=[]
sum_pushed_buttons=0           
number_of_players=0
number_of_actions=5
selection=0
menu_end=False
button_input=[]
button_settings=0
set_buttons=[0,0]
used_joysticks=[[],[]]
used_keyboards=[]
controllers=[]
gameover=0

player_sprites_right=[]
player_sprites_left=[]
player=[]

avail_controllers=["Keyboard1","Keyboard2"]
not_avail_controllers=[]
controllers_counter=0
joysticks_list=[]

white=(255,255,255)
black=(0,0,0)
red=(255,0,0)

clock = pygame.time.Clock()

game_name="First Fantasy : Quest V"
pygame.display.set_caption(game_name)

font=pygame.font.SysFont("calibri",15)

screen_metrics = pygame.display.Info()
background_metrics=(screen_metrics.current_w,screen_metrics.current_h)

WIN_WIDTH=screen_metrics.current_w
WIN_HEIGHT=screen_metrics.current_h

HALF_WIDTH = int(screen_metrics.current_w / 2)
HALF_HEIGHT = int(screen_metrics.current_h / 2)


#screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
screen = pygame.display.set_mode(background_metrics)



credits2=WIN_HEIGHT
credits_image=pygame.image.load("credits_image.png")
main_menu_images=(pygame.image.load("logo1.png"),pygame.image.load("logo2.png"))
main_menu_images=(pygame.transform.scale(main_menu_images[0],(background_metrics)),pygame.transform.scale(main_menu_images[1],(background_metrics)))

multiplayer_menu_images=(pygame.image.load("1_player.png"),pygame.image.load("2_players.png"))
multiplayer_menu_images=(pygame.transform.scale(multiplayer_menu_images[0],(background_metrics)),pygame.transform.scale(multiplayer_menu_images[1],(background_metrics)))

controls_menu_images=(pygame.image.load("adjust_controls1.png"),pygame.image.load("adjust_controls2.png"))
controls_menu_images=(pygame.transform.scale(controls_menu_images[0],(background_metrics)),pygame.transform.scale(controls_menu_images[1],(background_metrics)))

gameover_screen=pygame.image.load("gameover_screen.png")
level_texts=[pygame.image.load("Text_Dessert_1.png"),pygame.image.load("Text_Dessert_2.png"),pygame.image.load("Text_Boss.png")]

stone=pygame.image.load("DFA.png")
heart=pygame.image.load("heart.png")
heart=pygame.transform.scale(heart,(50,50))

boss_stone=[pygame.image.load("boss_stone_1.png"),pygame.image.load("boss_stone_2.png"),pygame.image.load("boss_stone_3.png")]

woman=pygame.image.load("adellin_down0.png")
woman=pygame.transform.scale(woman,(100,200))
blue_man=pygame.image.load("FSelection1.png")
blue_man=pygame.transform.scale(blue_man,(100,200))
red_man=pygame.image.load("PDSelection2.png")
red_man=pygame.transform.scale(red_man,(100,200))

Quake=pygame.mixer.Sound("Quake.ogg")

adellin=pygame.image.load("Adellin.png")
flint=pygame.image.load("Flint McMorris.png")
padre=pygame.image.load("Padre Duncan.png")

rock=pygame.image.load("rock.png")
spikes=pygame.image.load("spikes.png")
sand=pygame.image.load("sand.png")

key=pygame.image.load("key.png")
gate=pygame.image.load("gate.png")
lock=pygame.image.load("lock.png")

wolf_left=(pygame.image.load("WLF_Left2.png"),pygame.image.load("WLF_Left1.png"),pygame.image.load("WLF_Left2.png"),pygame.image.load("WLF_Left3.png"))
wolf_right=(pygame.image.load("WLF_Right2.png"),pygame.image.load("WLF_Right1.png"),pygame.image.load("WLF_Right2.png"),pygame.image.load("WLF_Right3.png"))
skeleton_left=(pygame.image.load("SKL_Left2.png"),pygame.image.load("SKL_Left1.png"),pygame.image.load("SKL_Left2.png"),pygame.image.load("SKL_Left3.png"))
skeleton_right=(pygame.image.load("SKL_Right2.png"),pygame.image.load("SKL_Right1.png"),pygame.image.load("SKL_Right2.png"),pygame.image.load("SKL_Right3.png"))
snake_left=(pygame.image.load("DS_Left2.png"),pygame.image.load("DS_Left1.png"),pygame.image.load("DS_Left2.png"),pygame.image.load("DS_Left3.png"))
snake_right=(pygame.image.load("DS_Right2.png"),pygame.image.load("DS_Right1.png"),pygame.image.load("DS_Right2.png"),pygame.image.load("DS_Right3.png"))
dust_fairy_left=(pygame.image.load("DF_Left2.png"),pygame.image.load("DF_Left1.png"),pygame.image.load("DF_Left2.png"),pygame.image.load("DF_Left3.png"))
dust_fairy_right=(pygame.image.load("DF_Right2.png"),pygame.image.load("DF_Right1.png"),pygame.image.load("DF_Right2.png"),pygame.image.load("DF_Right3.png"))
boss_left=(pygame.image.load("boss_left_still.png"),pygame.image.load("boss_left_1.png"),pygame.image.load("boss_left_still.png"),pygame.image.load("boss_left_2.png"))
boss_right=(pygame.image.load("boss_right_still.png"),pygame.image.load("boss_right_1.png"),pygame.image.load("boss_right_still.png"),pygame.image.load("boss_right_2.png"))

weapon_sounds=[pygame.mixer.Sound("Crossbow.ogg"),pygame.mixer.Sound("Slash10.ogg"),pygame.mixer.Sound("Skill3.ogg")]


Left1=[pygame.image.load("adellin_left0.png"),pygame.image.load("adellin_left1.png"),pygame.image.load("adellin_left0.png"),pygame.image.load("adellin_left2.png")]
Right1=[pygame.image.load("adellin_right0.png"),pygame.image.load("adellin_right1.png"),pygame.image.load("adellin_right0.png"),pygame.image.load("adellin_right2.png")]
Left2=[pygame.image.load("flint_left0.png"),pygame.image.load("flint_left1.png"),pygame.image.load("flint_left0.png"),pygame.image.load("flint_left1.png")]
Right2=[pygame.image.load("flint_right0.png"),pygame.image.load("flint_right1.png"),pygame.image.load("flint_right0.png"),pygame.image.load("flint_right1.png")]
Left3=[pygame.image.load("padre_left0.png"),pygame.image.load("padre_left1.png"),pygame.image.load("padre_left0.png"),pygame.image.load("padre_left2.png")]
Right3=[pygame.image.load("padre_right0.png"),pygame.image.load("padre_right1.png"),pygame.image.load("padre_right0.png"),pygame.image.load("padre_right2.png")]

sword_left=pygame.image.load("sword_left.png")
sword_right=pygame.image.load("sword_right.png")
loaded_left=pygame.image.load("loaded_left.png")
loaded_right=pygame.image.load("loaded_right.png")
unloaded_left=pygame.image.load("unloaded_left.png")
unloaded_right=pygame.image.load("unloaded_right.png")
arrow_left=pygame.image.load("arrow_left.png")
arrow_right=pygame.image.load("arrow_right.png")
magic=pygame.image.load("M1.png")

selection_music=pygame.mixer.Sound("Selection.ogg")
level_music=[pygame.mixer.Sound("Selection.ogg"),pygame.mixer.Sound("Dessert.ogg"),pygame.mixer.Sound("Boss.ogg"),pygame.mixer.Sound("Boss_fast.ogg")]

level_music[2].set_volume(0.7)
level_music[3].set_volume(0.7)

#dessert_background=pygame.transform.scale(dessert_background,(total_level_width/3,WIN_HEIGHT))

background = pygame.Surface(screen.get_size())
background = background.convert()

level_music[0].set_volume(0.5)
background_channel.play(level_music[0])

while not MainMenu_check(): #arxiki othoni
    
        if not background_channel.get_busy():
            background_channel.play(level_music[0])
        if selection==0:
                background.blit(main_menu_images[0],(0,0))
                selection=1
        else:
                background.blit(main_menu_images[1],(0,0))
                selection=0
        screen.blit(background,(0,0))
        pygame.display.flip()
        clock.tick(2)

selection=0
background.blit(multiplayer_menu_images[0],(0,0))
screen.blit(background,(0,0))
pygame.display.flip()

while selection!=6: #othoni gia epilogi arithmou players
    if not background_channel.get_busy():
            background_channel.play(level_music[0])
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN: #enter pressed
                    number_of_players=selection+1
                    selection=6
                    break
            else:
                if event.key == pygame.K_DOWN:
                    selection=1
                elif event.key == pygame.K_UP:
                    selection=0
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                background.blit(multiplayer_menu_images[selection],(0,0))
                screen.blit(background,(0,0))
                pygame.display.flip()
                clock.tick(60)                
                
for i in range(5):
    button_input.append(ControlButtonField(0,367+(i*55)))
controllers.append(ControllerButtonField(0))

if number_of_players == 2:
    playersa.append({})
    for i in range(5):
        button_input.append(ControlButtonField(1,367+(i*55)))
    controllers.append(ControllerButtonField(1))

if number_of_players==2:
    actions.append({})

for i in range(number_of_players):
    playersa[i]['Left']=None
    player_buttons.append(None)
    playersa[i]['Right']=None
    player_buttons.append(None)
    playersa[i]['Jump']=None
    player_buttons.append(None)
    playersa[i]['Attack']=None
    player_buttons.append(None)
    playersa[i]['Pause']=None
    player_buttons.append(None)
    actions[i]["Up"]=False
    actions[i]["Left"]=False
    actions[i]["Right"]=False
    actions[i]["Attack"]=False
    
pygame.joystick.init()
controllers_counter=0
for i in range(pygame.joystick.get_count()):
    joystick = pygame.joystick.Joystick(i)
    joystick.init()
    joysticks_list.append(joystick)
    avail_controllers.append(joystick.get_name())
    
while sum_pushed_buttons!=number_of_players*5:
    
        sum_pushed_buttons=0
        selection=0
        if not background_channel.get_busy():
            background_channel.play(level_music[0])
        for event in pygame.event.get():
            if event.type==pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                  for i in range(len(button_input)): 
                     
                      if button_input[i].check_click(pygame.mouse.get_pos()):
                          pygame.draw.circle(screen,red,[button_input[i].x_pos+button_input[i].width+20,button_input[i].y_pos+14],10,0)
                          pygame.display.flip()
                          clock.tick(60)
                          if controllers[button_input[i].player_no].text!="":
                           
                           while selection==0: 
                               for event in pygame.event.get():
                                   
                                   if event.type==pygame.KEYDOWN:
                                      if controllers[button_input[i].player_no].text=="Keyboard1" or controllers[button_input[i].player_no].text=="Keyboard2":
                                   
                                           pygame.draw.rect(screen,[255,0,0],[button_input[i].x_pos,button_input[i].y_pos,button_input[i].width,button_input[i].height],0)
                                           
                                           
                                           if button_input[i].text=="":
                                              
                                               if pygame.key.name(event.key) not in used_keyboards:
                                                   button_input[i].text=pygame.key.name(event.key)
                                                   player_buttons[i]=event.key
                                                   used_keyboards.append(pygame.key.name(event.key))
                                                   
                                                   set_buttons[button_input[i].player_no]+=1
                                           else:
                                               if pygame.key.name(event.key) not in used_keyboards:
                                                   
                                                   used_keyboards.remove(button_input[i].text)
                                                   button_input[i].text=pygame.key.name(event.key)
                                                   player_buttons[i]=event.key
                                                   used_keyboards.append(pygame.key.name(event.key))
                                                  
                                           selection+=1
                                           break
                                   elif event.type==pygame.JOYBUTTONDOWN:
                                           
                                              if i!=0 and i!=1 and i!=5 and i!=6: 
                                               
                                                   if controllers[button_input[i].player_no].text==joysticks_list[event.joy].get_name():
                                           
                                                       pygame.draw.rect(screen,[255,0,0],[button_input[i].x_pos,button_input[i].y_pos,button_input[i].width,button_input[i].height],0)
                                                       if button_input[i].text=="":
                                               
                                                           if ("button"+str(event.button)) not in used_joysticks[button_input[i].player_no]:
                                                               button_input[i].text="button"+str(event.button)
                                                               player_buttons[i]=event.button
                                                               used_joysticks[button_input[i].player_no].append("button"+str(event.button))
                                                              
                                                               set_buttons[button_input[i].player_no]+=1
                                                       else:
                                                           if ("button"+str(event.button)) not in used_joysticks[button_input[i].player_no]:
                                                               used_joysticks[button_input[i].player_no].remove(button_input[i].text)
                                                               button_input[i].text="button"+str(event.button)
                                                               player_buttons[i]=event.button
                                                               used_joysticks[button_input[i].player_no].append("button"+str(event.button))
                                                  
                                                       selection+=1
                                                       break
                                                   else:
                                                      selection+=1
                                                      break
                                              else:
                                                  selection+=1
                                                  break
                              
                  for i in range(len(controllers)):
                      if controllers[i].check_click(pygame.mouse.get_pos()):
                         if len(avail_controllers)!=len(not_avail_controllers):
                          if avail_controllers[controllers_counter] not in not_avail_controllers:
                              if controllers[i].text!="":
                                  not_avail_controllers.remove(controllers[i].text)
                                  if controllers[i].text=="Keyboard1" or controllers[i].text=="Keyboard2":
                                      for k in range(5):
                                          if button_input[(controllers[i].player_no*5)+k].text in used_keyboards:
                                             used_keyboards.remove(button_input[(controllers[i].player_no*5)+k].text)
                                      
                                  else:
                                      used_joysticks[controllers[i].player_no]=[]
                                     
                              controllers[i].text=avail_controllers[controllers_counter]
                              
                              for j in range(len(button_input)):
                                  if button_input[j].player_no==controllers[i].player_no:
                                      button_input[j].text=""
                              if controllers[i].text=="Keyboard1" or controllers[i].text=="Keyboard2":
                                  set_buttons[controllers[i].player_no]=0
                              else:
                                  button_input[controllers[i].player_no*5].text="Reserved"
                                  button_input[(controllers[i].player_no*5)+1].text="Reserved"
                                  player_buttons[controllers[i].player_no*5]=None
                                  player_buttons[(controllers[i].player_no*5)+1]=None
                                  set_buttons[controllers[i].player_no]=2
                                  
                              not_avail_controllers.append(avail_controllers[controllers_counter])
                              if controllers_counter==pygame.joystick.get_count()+1:
                                  controllers_counter=0
                              else:
                                  controllers_counter+=1
                          else:
                              while(avail_controllers[controllers_counter] in not_avail_controllers):
                                  if controllers_counter==pygame.joystick.get_count()+1:
                                      controllers_counter=0
                                  else:
                                      controllers_counter+=1
                                  if controllers[i].text!="":
                                      not_avail_controllers.remove(controllers[i].text)
                              if controllers[i].text=="Keyboard1" or controllers[i].text=="Keyboard2":
                                      for k in range(5):
                                          if button_input[(controllers[i].player_no*5)+k].text in used_keyboards:
                                             used_keyboards.remove(button_input[(controllers[i].player_no*5)+k].text)
                              controllers[i].text=avail_controllers[controllers_counter]
                              
                              used_joysticks[controllers[i].player_no]=[]
                              for j in range(len(button_input)):
                                  if button_input[j].player_no==controllers[i].player_no:
                                      button_input[j].text=""
                              
                              if controllers[i].text=="Keyboard1" or controllers[i].text=="Keyboard2":
                                  set_buttons[controllers[i].player_no]=0
                              else:
                                  for k in range(5):
                                          if button_input[(controllers[i].player_no*5)+k].text in used_keyboards:
                                             used_keyboards.remove(button_input[(controllers[i].player_no*5)+k].text)
                                  button_input[controllers[i].player_no*5].text="Reserved"
                                  button_input[(controllers[i].player_no*5)+1].text="Reserved"
                                  player_buttons[controllers[i].player_no*5]=None
                                  player_buttons[(controllers[i].player_no*5)+1]=None
                                  set_buttons[controllers[i].player_no]=2
                              
                              not_avail_controllers.append(avail_controllers[controllers_counter])
                              if controllers_counter==pygame.joystick.get_count()+1:
                                      controllers_counter=0
                              else:
                                      controllers_counter+=1
                  
            else:
               background.blit(controls_menu_images[1],(0,0))
               screen.blit(background,(0,0))
            for i in range(len(button_input)):
                pygame.draw.rect(screen,red,[button_input[i].x_pos,button_input[i].y_pos,button_input[i].width,button_input[i].height],2)
                button=font.render(button_input[i].text,1,red)
                screen.blit(button,(button_input[i].x_pos+40,button_input[i].y_pos+7))
            for i in range(len(controllers)):
                pygame.draw.rect(screen,red,[controllers[i].x_pos,controllers[i].y_pos,button_input[i].width+85,button_input[i].height],2)
                button=font.render(controllers[i].text,1,red)
                screen.blit(button,(controllers[i].x_pos+13,controllers[i].y_pos+7))
        pygame.display.flip()
        clock.tick(60)
        
        for i in range(len(set_buttons)):
            sum_pushed_buttons+=set_buttons[i]
       
for i in range(number_of_players):
        playersa[i]["Left"]=player_buttons[(i*5)]
        playersa[i]["Right"]=player_buttons[(i*5)+1]
        playersa[i]["Jump"]=player_buttons[(i*5)+2]
        playersa[i]["Attack"]=player_buttons[(i*5)+3]
        playersa[i]["Pause"]=player_buttons[(i*5)+4]
        
counter=[[50,50,400,400],[490,50,400,400],[930,50,400,400]]
selections=[]
final=[]

for i in range(number_of_players):
    final.append(3)
    selections.append(i)

for i in range(len(joysticks_list)):
    for j in range(number_of_players):
        if joysticks_list[i].get_name()==controllers[j].text:
            joysticksa.append(joysticks_list[i])

change=False
running=True

while running:
    running=False
    change=True
    if not background_channel.get_busy():
            background_channel.play(level_music[0])
    for event in pygame.event.get():
        if event.type==pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running=False
            for i in range(number_of_players):
                if event.key == playersa[i]["Attack"]:
                 for j in range(number_of_players):
                     if selections[i]==final[j]:
                         change=False
                         break
                 if not change:
                     break
                 else:
                     final[i]=selections[i]
                     if final[i]==0:
                                channels[i].play(ad_sel)
                     elif final[i]==1:
                                channels[i].play(fl_sel)
                     else:
                                channels[i].play(dun_sel)
                                
                if final[i]>2:
                     if event.key == playersa[i]["Left"]:
                         if selections[i]!=0:
                             for j in range(selections[i],0,-1):
                                 for l in range(number_of_players):
                                     if j-1==final[l]:
                                         change=False
                                         break
                                     else:
                                         if l==number_of_players-1:
                                             selections[i]=j-1
                                             change=True
                                             break
                                         else:
                                             continue
                                         
                                 if change:
                                     break
                         
                     if event.key == playersa[i]["Right"]:
                         if selections[i]!=2:
                             for j in range(selections[i],2,1):
                              for l in range(number_of_players):
                                 if j+1==final[l]:
                                    change=False
                                    break
                                 else:
                                     if l==number_of_players-1:
                                         selections[i]=j+1
                                         change=True
                                         break
                                     else:
                                         continue
                              if change:
                                 break
                             
        elif event.type==pygame.JOYBUTTONDOWN:
            
            for i in range(number_of_players):
                if joysticks_list[event.joy].get_name()==controllers[i].text:
                    if event.button==playersa[i]["Attack"]:
                        for j in range(number_of_players):
                            if selections[i]==final[j]:
                                change=False
                                break
                        if not change:
                            break
                        else:
                            final[i]=selections[i]
                            if final[i]==0:
                                channels[i].play(ad_sel)
                            elif final[i]==1:
                                channels[i].play(fl_sel)
                            else:
                                channels[i].play(dun_sel)
            
    for i in range(number_of_players):
        
     if controllers[i].text!="Keyboard1" and controllers[i].text!="Keyboard2":
               
                 for j in range(len(joysticksa)):
                     if joysticksa[j].get_name()==controllers[i].text:
                         axes=joysticksa[j].get_hat(0)
                         axis=joysticksa[j].get_axis(0)
                         if final[i]>2:
                          if axis==-1 or axes[0]==-1:
                            
                            if selections[i]!=0:
                             for j in range(selections[i],0,-1):
                                 for l in range(number_of_players):
                                     if j-1==final[l]:
                                         change=False
                                         break
                                     else:
                                         if l==number_of_players-1:
                                             selections[i]=j-1
                                             time.sleep(0.15)
                                             change=True
                                             break
                                         else:
                                             continue
                                                 
                                 if change:
                                     break
                                
                          if axis==1 or axes[0]==1:
                           
                            if selections[i]!=2:
                             for j in range(selections[i],2,1):
                              for l in range(number_of_players):
                                 if j+1==final[l]:
                                    change=False
                                    break
                                 else:
                                     if l==number_of_players-1:
                                         selections[i]=j+1
                                         time.sleep(0.15)
                                         change=True
                                         break
                                     else:
                                         continue
                              if change:
                                 break
                                
    background.fill(black)
    background.blit(woman,(200,100))
    background.blit(blue_man,(630,100))
    background.blit(red_man,(1070,100))
    background.blit(adellin,(190,350))
    background.blit(flint,(550,350))
    background.blit(padre,(1015,350))
    background.blit(press_attack,(500,500))
    screen.blit(background,(0,0))
    
    if final[0]<3:
        pygame.draw.rect(screen,[255,255,255],counter[selections[0]],4)
    else:
        pygame.draw.rect(screen,[255,0,0],counter[selections[0]],4)
    if number_of_players==2:
        if final[1]<3:
            pygame.draw.rect(screen,[255,255,255],counter[selections[1]],4)
        else:
            pygame.draw.rect(screen,[0,0,255],counter[selections[1]],4)
    for i in range(len(final)):
        if final[i]>2:
            running=True
    pygame.display.flip()
    clock.tick(60)

time.sleep(4)    
background_channel.stop()

for i in range(number_of_players):
    if final[i]==0:
        player_sprites_right.append(Right1)
        player_sprites_left.append(Left1)
    elif final[i]==1:
        player_sprites_right.append(Right2)
        player_sprites_left.append(Left2)
    else:
        player_sprites_right.append(Right3)
        player_sprites_left.append(Left3)
        


bg = pygame.Surface((32,32))
bg.convert()
bg.fill((0,0,0))



for index in levels_all:
    background_channel.stop()
    total_level_width  = len(index[0])*32
    total_level_height = len(index)*32
    camera = Camera(simple_camera, total_level_width, total_level_height)
    level_index+=1
    background.fill(black)
    background.blit(level_texts[level_index],(screen_metrics.current_w/2-250,screen_metrics.current_h/2-180))
    screen.blit(background,(0,0))
    pygame.display.flip()
    clock.tick(60)
    time.sleep(3)
    
    if level_index!=2:
        background_channel.play(level_music[1])
    else:
        background_channel.play(level_music[2])
        
    for i in range(number_of_players):
        
        if index==Boss_level:
            player.append(Player(32*20,1*32,player_sprites_right[i][0],roles[final[i]]))
            entities.add(player[i])
        elif index==DessertLevel:
            player.append(Player(32,32*7,player_sprites_right[i][0],roles[final[i]]))
            entities.add(player[i])
        elif index==Other_Level:
            player.append(Player(32,32*20,player_sprites_right[i][0],roles[final[i]]))
            entities.add(player[i])
            
    x=y=0
    pause=False

    for row in index:
        for col in row:
            if col == "J":
                Boss = Enemy(x,y-6+32*12,"Boss")
                enemies.add(Boss)
                entities.add(Boss)
            
            if col == "N":
                p = Platform(x,y+32*13,"next")
                platforms.append(p)
                entities.add(p)
                
            if col == "A":
                p = Platform(x,y+32*13,"key")
                platforms.append(p)
                entities.add(p)
                
            if col == "X":
                p = Platform(x,y+32*13,"gate")
                platforms.append(p)
                entities.add(p)

            if col == "O":
                p = Platform(x,y+32*13,"lock")
                platforms.append(p)
                entities.add(p)
            
            if col == "K":
                p = Platform(x,y+32*13,"keno")
                platforms.append(p)
                entities.add(p)
                
            if col == "F":
                p = Enemy(x, -16+y+32*13,"snake")
                enemies.add(p)
                entities.add(p)
                
            if col == "B":
                p = Enemy(x, -16+y+32*13,"skeleton")
                enemies.add(p) 
                entities.add(p)
                
            if col == "W":
                p = Enemy(x, -16+y+32*13,"wolf")
                enemies.add(p)
                entities.add(p)
                
            if col == "P":
                p = Enemy(x, y+32*13,"dust_fairy")
                enemies.add(p)
                entities.add(p)
                
            if col == "D":
                p = Platform(x, y+32*13,"sand")
                platforms.append(p)
                entities.add(p)
                
            if col == "S":
                p = Platform(x, y+32*13,"spikes")
                platforms.append(p)
                entities.add(p)
                
            if col == "R":
                p = Platform(x, y+32*13,"rock")
                platforms.append(p)
                entities.add(p)
                
            x += 32
        y += 32
        x = 0
        
    level_end=0

    while not level_completed[level_index]:
        
        if not background_channel.get_busy():
            if level_index!=2:
                background_channel.play(level_music[1])
            else:
                if Boss.lives>15:
                    background_channel.play(level_music[2])
                else:
                    background_channel.play(level_music[3])
           
        level_end=0
        gameover=0
        
        for i in range(number_of_players):
            if player[i].end_of_level==1:
                level_end+=1
        
        for i in range(number_of_players):
            if player[i].lives==0:
                gameover+=1
              
        
        if gameover==number_of_players:
            boss_attack.stop()
            background_channel.play(gameover_music)
            while 1:
                for e in pygame.event.get():
                    if e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE:
                        pygame.quit()
                
                if not background_channel.get_busy():
                    pygame.quit()
                background.fill((0,0,0))
                background.blit(gameoveru,(450,300))
                screen.blit(background,(0,0))
                pygame.display.flip()
                clock.tick(60)
               
        if level_end==number_of_players:
            level_completed[level_index]=True
            break
        
        if gameover==level_end and gameover>0:
            level_completed[level_index]=True
            break

        for i in range(number_of_players):
            for j in range(len(joysticksa)):
                     if joysticksa[j].get_name()==controllers[i].text:
                         axes=joysticksa[j].get_hat(0)
                         axis=joysticksa[j].get_axis(0)
                         if axis==-1 or axes[0]==-1:
                             actions[i]["Left"] = True
                         if axis==1 or axes[0]==1:
                             actions[i]["Right"] = True
                         if axis==0 or axes[0]==0:
                             actions[i]["Left"] = False
                             actions[i]["Right"] = False
    
        for event in pygame.event.get():
            
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
             for i in range(number_of_players):
            
                if controllers[i].text=="Keyboard1" or controllers[i].text=="Keyboard2":
                 if not pause:
                    if event.key==playersa[i]["Left"]:
                        actions[i]["Left"] = True
                    if event.key==playersa[i]["Right"]:
                        actions[i]["Right"] = True
                    if event.key==playersa[i]["Jump"]:
                        actions[i]["Up"] = True
                    if event.key==playersa[i]["Attack"]:
                        actions[i]["Attack"] = True
                    if event.key==pygame.K_m:
                        screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
                    if event.key==pygame.K_l:
                        screen = pygame.display.set_mode(background_metrics)
                                  
                 if event.key==playersa[i]["Pause"]:
                        if pause:
                            pause=False   
                        else:
                            pause=True
                            
            elif event.type == pygame.KEYUP:
             for i in range(number_of_players):
                    if controllers[i].text=="Keyboard1" or controllers[i].text=="Keyboard2":
                        if event.key==playersa[i]["Left"]:
                            actions[i]["Left"] = False
                        if event.key==playersa[i]["Right"]:
                            actions[i]["Right"] = False
                        if event.key==playersa[i]["Jump"]:
                            actions[i]["Up"] = False
                        if event.key==playersa[i]["Attack"]:
                            actions[i]["Attack"] = False
                           
            elif event.type == pygame.JOYBUTTONDOWN:
             for i in range(number_of_players):
                if joysticks_list[event.joy].get_name()==controllers[i].text:
                    if event.button==playersa[i]["Jump"]:
                        actions[i]["Up"] = True
                    if event.button==playersa[i]["Attack"]:
                        actions[i]["Attack"] = True
                    if event.button==playersa[i]["Pause"]:
                        if pause:
                            pause=False   
                        else:
                            pause=True
                            
            elif event.type == pygame.JOYBUTTONUP:
             for i in range(number_of_players):
                    if joysticks_list[event.joy].get_name()==controllers[i].text:
                        if event.button==playersa[i]["Attack"]:
                            actions[i]["Attack"] = False
                        if event.button==playersa[i]["Jump"]:
                            actions[i]["Up"] = False
                            
        if pause:
            background.blit(gameover_screen,(450,150))
            screen.blit(background,(0,0))
            pygame.display.flip()
            clock.tick(60)
        if not pause:
         for x in range(0,(1344+32)/32):
            for y in range(0,(screen_metrics.current_h/32)+(32*18)):
             background.blit(bg, (x * 32, y * 32))
    
         for i in range(number_of_players):
             if player[i].alive():
                 camera.update(player[i])
         
         for i in range(number_of_players):
             if player[i].alive():
                
                 player[i].update(actions[i]["Up"],actions[i]["Left"],actions[i]["Right"],actions[i]["Attack"],platforms,i)
                 if player[i].image!=None:
                     
                  if index==Boss_level:
                    background.blit(player[i].image,(player[i].rect[0],player[i].rect[1]))
                  else:
                     background.blit(player[i].image,camera.apply(player[i]))
                     
         for p in platforms:
             background.blit(p.image, camera.apply(p))
     
         for e in enemies:
            e.update()
            background.blit(e.image, camera.apply(e))

         for m in moving_attacks:
             if m.owner.name in ["dust_fairy","Boss"]:
                m.update()
             else:
                m.update(enemies)
             background.blit(m.image, camera.apply(m))
         font=pygame.font.SysFont("calibri",15)
         for i in range(number_of_players):
             background.blit(heart,(25,40*(i*2)))
             button=font.render(str(player[i].lives),3,[0,0,0])
             background.blit(button,(47,40*(i*2)+17))
         font=pygame.font.SysFont("calibri",20)
         button=font.render("Boss",3,(255,255,255))
         if index==Boss_level and Boss.lives>0:
             background.blit(button,(1204,55))
             pygame.draw.rect(background,(150,155,50),[1150,80,150,25],3)
             if Boss.lives>15:
                 pygame.draw.rect(background,(0,255,0),[1152,82,(Boss.lives*5)-4,21])
             else:
                 pygame.draw.rect(background,(255,0,0),[1152,82,(Boss.lives*5)-4,21])
             
         screen.blit(background,(0,0))
         pygame.display.flip()
         clock.tick(60)

    for i in player:
        i.kill()
        player=[]
    for i in entities:
        i.kill()
        entities.remove(i)
    for i in platforms:
        i.kill()
        platforms=[]    
    
    for i in enemies:
        i.kill()
        enemies.remove(i)

selection=0

credits2=WIN_HEIGHT
time.sleep(2)

background_channel.play(victory_sound)
while selection==0:
    for e in pygame.event.get():
        if e.type==pygame.KEYDOWN:
            if e.key==pygame.K_ESCAPE:
                selection=1
        if e.type==pygame.QUIT:
            selection=1
    background.fill((0,0,0))
    background.blit(credits_image,(0,credits2))
    background.blit(tsakwnas,(350,credits2+1550))
    credits2-=3
    if credits2<-WIN_HEIGHT-1100:
        selection=1
    screen.blit(background,(0,0))
    pygame.display.flip()
    clock.tick(60)

pygame.mixer.quit()
pygame.quit()

