import pygame, sys, time, random
import accelerometer_input as acc


pygame.init()
pygame.font.init()

SCREEN_X= 720
"Width of the screen"
SCREEN_Y=480
"Height of the screen"

pygame.display.set_caption('Sophie Snake Slay')
window = pygame.display.set_mode((SCREEN_X, SCREEN_Y))
"Target window for game"

clock = pygame.time.Clock()

SNAKE_COLOUR = (255, 0, 247)
FOOD_COLOUR = (0, 255, 166)
SCORE_COLOUR = (255, 0, 247)

class Coord():
    "X and Y coordinates"

    def __init__(self, x, y):
        self.x = x
        self.y = y

FOOD_WIDTH = 20
def generateFood():
    return pygame.Rect(random.randint(0, SCREEN_X - FOOD_WIDTH),
                       random.randint(0, SCREEN_Y - FOOD_WIDTH),
                       FOOD_WIDTH, FOOD_WIDTH)

SNAKE_WIDTH = 20

accurate_x = 100.0
accurate_y = 50.0

snake_pos = pygame.Rect(accurate_x, accurate_y, SNAKE_WIDTH, SNAKE_WIDTH)
"Head of the snake"

snake_body = [Coord(snake_pos.x, snake_pos.y)]
"'Units' of the snake body"

food = generateFood()
score = 0



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

while True:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    """
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
         snake_pos.y -= 10
    if keys[pygame.K_s]:
        snake_pos.y += 10
    if keys[pygame.K_a]:
        snake_pos.x -= 10
    if keys[pygame.K_d]:
        snake_pos.x += 10
    """
    accurate_x -= acc.Input.getX() * 10
    accurate_y += acc.Input.getY() * 10

    snake_pos.x = accurate_x
    snake_pos.y = accurate_y

    snake_body.insert(0, Coord(snake_pos.x, snake_pos.y))

    # snake be getting bigger
    if snake_pos.colliderect(food):
        score += 1
        sounds["omnom"].play()
        food = generateFood()
    else:
        snake_body.pop()
        
    #rendering
    window.fill('black')
    for pos in snake_body:
        pygame.draw.rect(window, SNAKE_COLOUR, pygame.Rect(pos.x, pos.y, SNAKE_WIDTH, SNAKE_WIDTH))

    pygame.draw.rect(window, FOOD_COLOUR, food)

    #game over
    if snake_pos.x < 0 or snake_pos.x > SCREEN_X-SNAKE_WIDTH or snake_pos.y < 0 or snake_pos.y > SCREEN_Y-SNAKE_WIDTH:
        sounds["oopsydaisy"].play()
        gamover()
    

    """for i in range(1,len(snake_body)):
         if snake_pos[0] == snake_body[i]:
            print("ate  myself")
            gamover()"""

    #refresh
    show_score(1, SCORE_COLOUR, 'Comic Sans', 20)
    pygame.display.update()

    # limits FPS to 60
    clock.tick(60)
