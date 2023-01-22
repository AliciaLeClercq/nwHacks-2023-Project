import pygame
import cv2
import numpy
import ctypes
from datetime import datetime

# Accesses the camera
cam = cv2.VideoCapture(0)

# Contains image names
img_names = []
shown_img = []

# img_names.append("22_01_2023_04_40_39")
# img_names.append("22_01_2023_04_40_40")
# img_names.append("22_01_2023_04_40_41")
# img_names.append("22_01_2023_04_40_42")
# img_names.append("22_01_2023_04_40_43")
# img_names.append("22_01_2023_04_40_44")
# img_names.append("22_01_2023_04_40_45")

pygame.init()

# Screen
width, height = 350, 640
screen = pygame.display.set_mode((width,height))
pygame.display.set_caption("screen")

# FPS
clock = pygame.time.Clock()

crashed = False

# Loading Images
button_image = pygame.image.load("GraphicImg/button.png")
camera_image = pygame.image.load("GraphicImg/Camera.png").convert_alpha()
cancel_image = pygame.image.load("GraphicImg/Cancel Button.png").convert_alpha()
large_image = pygame.image.load("GraphicImg/largeFrame.png").convert_alpha()
small_image = pygame.image.load("GraphicImg/smallFrame.png").convert_alpha()
tbaFolder_image = pygame.image.load("GraphicImg/tbaFile.png").convert_alpha()
deleteButton_image = pygame.image.load("GraphicImg/Delete Button.png").convert_alpha()
delete_image = pygame.image.load("GraphicImg/Delete Images.png").convert_alpha()
folderCam_image = pygame.image.load("GraphicImg/camFolder.png").convert_alpha()
folder_image = pygame.image.load("GraphicImg/filesFolder.png").convert_alpha()
x_image = pygame.image.load("GraphicImg/x.png").convert_alpha()
fileBG_img = pygame.image.load("GraphicImg/Files.png").convert()
monthly_img = pygame.image.load("GraphicImg/Monthly Gallery.png").convert()
tint_image = pygame.image.load("GraphicImg/tint.png").convert_alpha()

state = 0

start = datetime.now()
sec_start = start.second
timer = 10

closeup = False

# Mouse over rect
def collision (x1,y1,w1,h1,x2,y2):
    if x2>=x1 and x2<=x1+w1 and y2>y1 and y2<y1+h1:
        return True
    return False

# OpenCV Vid to PyGame
def toPyGame(frame):
    frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    frame=numpy.rot90(frame)
    frame=pygame.surfarray.make_surface(frame)
    return frame

# Gets camera, resizes and crops
def getCamFrame(camera):
    global origFrame

    retval,frame=camera.read()

    cam_w = 304
    cam_h = 359

    #Gets the width and height of the screen
    user32 = ctypes.windll.user32
    screen_width, screen_height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

    # Gets the scale for w and h
    # scalebgWidth = float(cam_w)/float(screen_width)
    scalebgHeight = float(cam_h)/float(screen_height)

    newX,newY = screen_width*scalebgHeight,screen_height*scalebgHeight
    
    frame = cv2.resize(frame,(int(newX),int(newY)))
    # 574.4 x 359
    # print(newX," | ",newY)

    # Cropped
    halfX = int(newX/2)
    new_topleft = int(halfX-cam_w/2)
    new_topright = int(halfX+cam_w/2)
    frame = frame[0:int(newY), new_topleft:new_topright]

    origFrame = frame

    frame = toPyGame(frame)

    return frame

# puts camera on screen
def blitCamFrame(frame,screen):
    screen.blit(frame,(22,121))
    return screen

# Saves the image with date and time
def saveImg():
    # gets the date and time
    now = datetime.now()
    dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
    # print("date and time =", dt_string)
    if (len(img_names)<=0 or img_names[-1] != dt_string):
        img_names.append(dt_string)
        # sets file name
        imgName = f"Images/{dt_string}.png"
        # creates image
        cv2.imwrite(imgName, origFrame)
        print("{} written!".format(imgName))

# the photo screen
def screen_photo():
    global state

    # Puts the camera on
    frame=getCamFrame(cam)
    blitCamFrame(frame,screen)

    screen.blit(camera_image,(0,0)) #The screen
    screen.blit(button_image,(111,547))
    screen.blit(folderCam_image,(276,552))

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    # Camera button
    if click[0]:
        if collision(111,547,button_image.get_width(),button_image.get_height(),mouse[0],mouse[1]):
            # print("hi")
            saveImg()
        if collision(276,552,folderCam_image.get_width(),folderCam_image.get_height(),mouse[0],mouse[1]):
            # print("hi")
            state = 1

    pygame.display.update()
    clock.tick(60)
    return state

def screen_file():
    global state

    screen.blit(fileBG_img,(0,0))
    screen.blit(tbaFolder_image,(32,90))
    screen.blit(folder_image,(131, 90))
    screen.blit(x_image,(322, 5))

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if click[0]:
        # Folder
        if collision(131, 90,folder_image.get_width(),folder_image.get_height(),mouse[0],mouse[1]):
            # print("folder")
            state = 2
        if collision(322, 5,x_image.get_width(),x_image.get_height(),mouse[0],mouse[1]):
            # print("x")
            state = 0

    pygame.display.update()
    clock.tick(60)
    return state

def screen_closeup(ind, img_names):
    global closeup
    # global ind
    screen.blit(tint_image,(0,0))

    img = cv2.imread(f"Images/{img_names[ind]}.png",cv2.IMREAD_COLOR)
    img = cv2.resize(img,(221,261))
    img = toPyGame(img)
    screen.blit(img,(64,179))

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    screen.blit(large_image,(56,153))
    screen.blit(x_image,(322, 5))

    if click[0] and collision(322, 5,x_image.get_width(),x_image.get_height(),mouse[0],mouse[1]):
        screen_gallery(sec_start,timer,img_names)
        closeup=False
    return closeup

def screen_gallery(sec_start,timer,img_names):
    global state
    global closeup
    ind=-1

    screen.blit(monthly_img,(0,0))
    screen.blit(x_image,(322, 5))

    now = datetime.now()
    sec_now = now.second
    # print("sec_now: ",sec_now)
    h_int = 0
    w_int=0
    t = 0
    y=0

    # if sec_now>=sec_start+timer:
    for i in range(len(img_names)): 
        img = cv2.imread(f"Images/{img_names[i]}.png",cv2.IMREAD_COLOR)
        img = cv2.resize(img,(85,101))
        img = toPyGame(img)

        # int of 3 is on new row
        if(i>0 and i%3==0): 
            h_int = 132
            w_int = 0
            t+=1
            y=0
        else:
            w_int=104
        
        screen.blit(img,(20+(y*w_int),91+(t*h_int))) #20,223 #20,355
        screen.blit(small_image,(16+(y*w_int), 80+(t*h_int))) #16,212 #16,344
        # print(i,"| ",y," | ",16+(y*w_int)," | ",80+(t*h_int))

        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if click[0] and collision(16+(y*w_int), 80+(t*h_int),small_image.get_width(),small_image.get_height(),mouse[0],mouse[1]):
            # print(i,"| ",y," | ",16+(y*w_int)," | ",80+(t*h_int))
            closeup=True
            ind = i
            # screen_closeup(i,img_names)
            # screen.blit(tint_image,(0,0))
            # screen.blit(large_image,(0,0))
            # if closeup:
            closeup = screen_closeup(ind,img_names)
        
        y+=1
    
    # screen_closeup()

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if click[0] and collision(322, 5,x_image.get_width(),x_image.get_height(),mouse[0],mouse[1]):
        # print("x")
        state = 1

    pygame.display.update()
    clock.tick(60)
    return state

# Runs the entire thing (loops)
while not crashed:

    for event in pygame.event.get():
        # Quits the game
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
    if state == 0:
        state = screen_photo()
    elif state == 1:
        state = screen_file()
    elif state == 2:
        state = screen_gallery(sec_start,timer,img_names)
    
pygame.quit()
quit()