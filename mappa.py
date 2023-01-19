import pygame
import time
import sys
from os.path import join

from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)
# cambiare in base a quando grande e' la mappa x2
board = [['0' for i in range(12)] for i in range(12)]
#posizione partenza roboto in matrice
xStart = 6
yStart = 6

xNow = 6
yNow = 6
# variabili test
muro = 1

base = 3

#se vuoto valore 0
#se muro valore !


board[yStart][xStart] = "1"
#cambiare in base a quando grande e' la mappa x2
for i in range(12):
    for j in range(12):
        if i%2 != 0:
            board[i][j] = "-"
        if j%2 != 0:
            board[i][j] = "-"
        if j%2 != 0 and i%2 != 0:
            board[i][j] = "$"

pygame.init()
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen.fill((130, 130, 140))


robot = board[yNow][xNow]


running = True

while running:
    pygame.display.flip()
    pygame.draw.circle(screen, (0, 0, 255), (board[yNow][xNow]), 20)
    for event in pygame.event.get():
        # Check for KEYDOWN event
        if event.type == KEYDOWN:
            # If the Esc key is pressed, then exit the main loop
            if event.key == K_ESCAPE:
                running = False
        # Check for QUIT event. If QUIT, then set running to false.
        elif event.type == QUIT:
            running = False
    #cambiare pressed key con variabile spostamento robot= move        
    pressed_keys = pygame.key.get_pressed()
    if pressed_keys[K_UP] and yNow > 1 and (board[yNow - 1][xNow] != '!'):
        yNow -= 2
    if pressed_keys[K_DOWN] and yNow < 9 and (board[yNow + 1][xNow] != '!'):
        yNow += 2
    if pressed_keys[K_LEFT] and xNow > 1 and (board[yNow][xNow - 1] != '!'):
        xNow -= 2
    if pressed_keys[K_RIGHT] and xNow < 9 and (board[yNow][xNow + 1] != '!'):
        xNow += 2
     # togliere time sleep aggimgi move =0        
    time.sleep(0.2)
    
    if yStart != yNow or xStart != xNow:
        
        #if board[yNow][xNow] != '0'
        if base == 2:
            board[yStart][xStart] = '2'                         # base bianca=2 /base blu=3 /base nera =4 /base lettera= 2+numero lato/ base vittima gialla= 3+numero lato/ base vittima blu= 4+numero lato/ base vittima rossa= 5+numero lato
        elif base == 3:
            board[yStart][xStart] = '3'
        elif base == 4:
            board[yStart][xStart] = '4'
        elif base == 21:
            board[yStart][xStart] = '21'
        elif base == 22:
            board[yStart][xStart] = '22'
        elif base == 23:
            board[yStart][xStart] = '23'
        elif base == 24:
            board[yStart][xStart] = '24'
        elif base == 31:
            board[yStart][xStart] = '31'
        elif base == 32:
            board[yStart][xStart] = '32'
        elif base == 33:
            board[yStart][xStart] = '33'
        elif base == 34:
            board[yStart][xStart] = '34'
        elif base == 41:
            board[yStart][xStart] = '41'
        elif base == 42:
            board[yStart][xStart] = '42'
        elif base == 43:
            board[yStart][xStart] = '43'
        elif base == 44:
            board[yStart][xStart] = '44'
        elif base == 51:
            board[yStart][xStart] = '51'
        elif base == 52:
            board[yStart][xStart] = '52'
        elif base == 53:
            board[yStart][xStart] = '53'
        elif base == 54:
            board[yStart][xStart] = '54'
            
        
        
        board[yNow][xNow] = '1'
        
        yStart = yNow
        xStart = xNow
        
        if muro == 1:
            board[yNow-1][xNow] ='!'                                                  #       1
        elif muro == 2:                                                               #       _
            board[yNow][xNow+1] ='!'                                                  #     4| |2
                                                                                      #       -
        elif muro == 3:                                                               #       3
            board[yNow+1][xNow] ='!'
        
        elif muro == 4:
            board[yNow][xNow-1] ='!'
        
        elif muro == 12:
            board[yNow-1][xNow] ='!'
            board[yNow][xNow+1] ='!'
        
        elif muro == 13:
            board[yNow-1][xNow] ='!'
            board[yNow+1][xNow] ='!'
       
        elif muro == 14:
            board[yNow-1][xNow] ='!'
            board[yNow][xNow-1] ='!'
       
        elif muro == 23:
            board[yNow][xNow+1] ='!'
            board[yNow+1][xNow] ='!'
            
       
        elif muro == 24:
            board[yNow][xNow+1] ='!'
            board[yNow][xNow-1] ='!'
        
        elif muro == 34:
            board[yNow+1][xNow] ='!'
            board[yNow][xNow-1] ='!'
        
        elif muro == 123:
            board[yNow-1][xNow] ='!'
            board[yNow][xNow+1] ='!'
            board[yNow+1][xNow] ='!'
        
        elif muro == 124:
            board[yNow-1][xNow] ='!'
            board[yNow][xNow+1] ='!'
            board[yNow][xNow-1] ='!'
        
        elif muro == 134:
            board[yNow-1][xNow] ='!'
            board[yNow+1][xNow] ='!'
            board[yNow][xNow-1] ='!'
        
        elif muro == 234:
            board[yNow][xNow+1] ='!'
            board[yNow+1][xNow] ='!'
            board[yNow][xNow-1] ='!'
        
            
          
        for i in range(12):
            print(board[i])
        
        print()
        
        
        
pygame.quit()
    
