import pygame, time, random
#import accelerometer_input as acc
from classes import Floor, Snake, Food


pygame.init()
pygame.font.init()

SCREEN_W= 720
SCREEN_H=480
pygame.display.set_caption('Sophie Snake Slay')
window = pygame.display.set_mode((SCREEN_W, SCREEN_H))
"Target window for game"

clock = pygame.time.Clock()



SCORE_COLOUR = (255, 0, 247)

score = 0
floor = Floor('black', SCREEN_W, SCREEN_H)

foods = []

snake = Snake((255, 0, 247), 20, (SCREEN_W // 2) - 10, (SCREEN_H // 2) - 10, 0)

def createNewFood():
    foods.append(Food((0, 255, 166), 20, floor.getRandomRect(20, 20)))

createNewFood()

sounds = { "omnom" : pygame.mixer.Sound("eat_sound.mp3"),
           "oopsydaisy" : pygame.mixer.Sound("collision_sound.mp3"),
           "womp_womp" : pygame.mixer.Sound("womp-womp.mp3")
         }

def gamover():
    sounds["oopsydaisy"].play()
    my_font = pygame.font.SysFont('Times New Roman', 90)
    game_over_surface = my_font.render('YOU DIED', True, (252,3,3) )
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (SCREEN_W/2, SCREEN_H/4)
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
        score_rect.midtop = (SCREEN_W/10, 15)
    else:
        score_rect.midtop = (SCREEN_W/2, SCREEN_H/1.25)
    window.blit(score_surface, score_rect)

def gamerun():
    while True:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        x_move = 0
        y_move = 0

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            y_move -= 10
        if keys[pygame.K_s]:
            y_move += 10
        if keys[pygame.K_a]:
            x_move -= 10
        if keys[pygame.K_d]:
            x_move += 10
        
        snake.move(x_move, y_move)

        foods_to_pop = []
        for i, food in enumerate(foods):
            if snake.asPygameRect().colliderect(food.asPygameRect()):
                score += 1
                sounds["omnom"].play()
                foods_to_pop.insert(0, i)
                createNewFood()
                snake.length += 3
                while random.randint(1, 4) == 1:
                    createNewFood()
        
        for i in foods_to_pop:
            foods.pop(i)
        
        floor.render(window)
        snake.render(window)
        for food in foods:
            food.render(window)

        #game over
        if snake.x < 0 or snake.x > SCREEN_W-snake.w or snake.y < 0 or snake.y > SCREEN_H-snake.h:
            gamover()

        #refresh
        show_score(1, SCORE_COLOUR, 'Comic Sans', 20)

        pygame.display.update()

        clock.tick(60)
                    