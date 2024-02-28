 
import pygame, sys, time
import accelerometer_input as acc
sys.path.append("classes")
import  snake
import Coord 
import floor 
import Food
pygame.init()
pygame.font.init()


SCREEN_X= 720
"Width of the screen"
SCREEN_Y=480
"Height of the screen"
GAME_oBJECT_WIDTH= 20
SCORE_COLOUR = (255, 0, 247)
accurate_x = 100.0
accurate_y = 50.0
score=0
pygame.display.set_caption('Sophie Snake Slay')
window = pygame.display.set_mode((SCREEN_X, SCREEN_Y))
"Target window for game"

clock = pygame.time.Clock()

mysnake=snake((255, 0, 247),GAME_oBJECT_WIDTH,accurate_x,accurate_y)
myfood=Food((0, 255, 166),GAME_oBJECT_WIDTH,window)
myfloor=floor('black',SCREEN_X.SCREEN_Y,SCREEN_X,SCREEN_Y)

sounds = { "omnom" : pygame.mixer.Sound("eat_sound.mp3"),
           "oopsydaisy" : pygame.mixer.Sound("collision_sound.mp3"),
           "womp_womp" : pygame.mixer.Sound("womp-womp.mp3")
         }

def gamover():
    my_font = pygame.font.SysFont('Times New Roman', 90)
    game_over_surface = my_font.render('YOU DIED', True, (252,3,3) )
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (SCREEN_X/2, SCREEN_Y/4)
    window.fill((10,10,10))
    window.blit(game_over_surface, game_over_rect)
    show_score(0, (252,3,3), 'Comic Sans', 20)
    pygame.display.flip()
    sounds["womp_womp"].play()
    time.sleep(3)
    pygame.quit()

def show_score(choice, colour, font, size):
    score_font = pygame.font.SysFont(font, size)
    score_surface = score_font.render('Score : ' + str(score), True, colour)
    score_rect = score_surface.get_rect()
    if choice == 1:
        score_rect.midtop = (SCREEN_X/10, 15)
    else:
        score_rect.midtop = (SCREEN_X/2, SCREEN_Y/1.25)
    window.blit(score_surface, score_rect)


##main program
while True:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    accurate_x -= acc.Input.getX() * 10
    accurate_y += acc.Input.getY() * 10

    snake.x = accurate_x
    snake.y = accurate_y
    mysnake.move(Coord(snake.x,snake.y))

    if mysnake.colliderect(myfood):
        score += 1
        sounds["omnom"].play()
        myfood.render(window)
    else:
        snake.pop()
    
    myfloor.render()
    mysnake.render(window)
    myfood.render(window)

     #game over
    if mysnake.x < 0 or mysnake.x > SCREEN_X-mysnake.width or mysnake.y < 0 or myfood.y > SCREEN_Y-mysnake.width:
        sounds["oopsydaisy"].play()
        gamover()

     #refresh
    show_score(1, SCORE_COLOUR, 'Comic Sans', 20)
    pygame.display.update()
                 