import pygame
from random import randint, randrange, uniform, choice
from inputNeuron import InputNeuron
from ouputNeuron import OutputNeuron
from parameters import edit_params
from math import floor, ceil

pygame.init()
clock = pygame.time.Clock()

BIRD_X = 150
WINDOW_HEIGHT = 800
WINDOW_WIDTH = 500

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Flappy Bird AI")

img_bg = pygame.image.load("imgs/bg.png")
img_pipe = pygame.image.load("imgs/pipe.png")
img_pipe_top = pygame.image.load("imgs/pipe_top.png")
img_bird_flap1 = pygame.image.load("imgs/bird_flap1.png")
img_bird_flap2 = pygame.image.load("imgs/bird_flap2.png")
img_params = pygame.image.load("imgs/params.png")

PIPE_TOP_HEIGHT = 59

bgx1 = 0
bgx2 = WINDOW_WIDTH

font_data = pygame.font.SysFont("Arial", 30, True)

max_gens = 100
gen_lifetime = 20 #seconds
gen_size = 100
pick_rate = 10 #percent


class Bird:

    def __init__(self):
        self.x = BIRD_X
        self.y = 400
        self.width = 35
        self.acc = 0.02
        self.v = 1.5
        self.bird = pygame.Rect(self.x, self.y, self.width, self.width)
        self.jumping = False
        self.jump_time = 1*60
        self.is_alive = True
        self.fitness = 0
        self.anim_state = 0
        self.images = [img_bird_flap1, img_bird_flap2]

        self.input_y = InputNeuron(uniform(-2, 2))
        self.input_ty = InputNeuron(uniform(-2, 2))
        self.input_by = InputNeuron(uniform(-2, 2))

        self.output = OutputNeuron()

    def animate(self):
        self.anim_state += 0.2
        idx = round(self.anim_state)

        if idx > 1:
            self.anim_state = 0
            idx = 0

        return self.images[idx]

    def draw(self):
        self.bird = pygame.Rect(self.x, self.y, self.width, self.width)
        screen.blit(self.animate(), (self.x, self.y))

    def fall(self):
        self.v += self.acc
        self.y += self.v

    def init_jump(self):
        self.jumping = True
        self.jump_time = 0.5*60

    def jump(self):
        if self.jumping:

            self.y -= 4
            self.v = 1.5

            self.jump_time -= 1
            if self.jump_time <= 0:
                self.jumping = False

    def colliding(self):
        for pipe in pipe_list:
            if self.bird.colliderect(pipe.pipe) or self.y <= 0 or self.y >= WINDOW_HEIGHT-self.width:
                self.is_alive = False

        self.fitness += 1

    def should_jump(self):

        self.input_y.input = self.y
        self.input_ty.input = first_pipes[0].y + first_pipes[0].height
        self.input_by.input = first_pipes[1].y

        self.output.get_input([self.input_y, self.input_ty, self.input_by])
        if self.output.get_output() >= 0.5:
            self.init_jump()

    def offsprings(self):

        def weight_sign():
            return choice([-1,1,1,1,1,1,1,1,1,1])

        children = []

        amount = floor(gen_size / (gen_size * pick_rate/100))

        for _ in range(amount):
            yw = self.input_y.weight * uniform(0.95, 1.05) * weight_sign()
            tyw = self.input_ty.weight * uniform(0.95, 1.05) * weight_sign()
            byw = self.input_by.weight * uniform(0.95, 1.05) * weight_sign()

            input_y = InputNeuron(yw)
            input_ty = InputNeuron(tyw)
            input_by = InputNeuron(byw)
            out = OutputNeuron()

            child = Bird()

            child.input_y = input_y
            child.input_ty = input_ty
            child.input_by = input_by
            child.output = out

            children.append(child)

        return children


class Pipe:

    def __init__(self, y, height):
        self.x = 500
        self.y = y
        self.height = height
        self.width = 100
        self.pipe = pygame.Rect(self.x, self.y, self.width, self.height)
        self.color = (0, 255, 0)
        self.pipe_height = self.height - PIPE_TOP_HEIGHT
        self.image_pipe = pygame.transform.scale(img_pipe, (self.width, self.pipe_height))

    def draw(self):
        self.pipe = pygame.Rect(self.x, self.y, self.width, self.height)

        if self.y == 0:
            screen.blit(self.image_pipe, (self.x, self.y))
            screen.blit(img_pipe_top, (self.x, self.height - PIPE_TOP_HEIGHT - 3))
        else:
            screen.blit(self.image_pipe, (self.x, WINDOW_HEIGHT - self.pipe_height))
            screen.blit(img_pipe_top, (self.x, self.y + 3))

    def move(self):
        self.x -= 1.5


def spawn_pipes():
    height_top = randint(200, 450)
    gap = 150
    height_bottom = WINDOW_HEIGHT - gap - height_top
    top_bottom = WINDOW_HEIGHT - height_bottom

    pipe_top = Pipe(0, height_top)
    pipe_bottom = Pipe(top_bottom, height_bottom)

    return [pipe_top, pipe_bottom]

FPS = 60

pipe_list = spawn_pipes()
first_pipes = []
first_pipes += pipe_list
spawn_timer = 4*FPS

score = 0
top_score = 0

bird_list = [Bird() for _ in range(gen_size)]

gen = 1


round_timer_max = gen_lifetime * FPS
round_timer = round_timer_max

button_params = pygame.Rect(WINDOW_WIDTH-120, 45, 100, 50)


def button_clicked(button):
    mx, my = pygame.mouse.get_pos()
    if button.collidepoint(mx, my):
        return True
    return False



while True:

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            exit()

        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if button_clicked(button_params):
                max_gens, gen_size, gen_lifetime, pick_rate = edit_params(max_gens, gen_size, gen_lifetime, pick_rate)

    screen.fill((225, 225, 225))

    """BACKGROUND SCROLLING"""

    bgx1 -= 1.5
    bgx2 -= 1.5

    if bgx1 < -WINDOW_WIDTH:
        bgx1 = WINDOW_WIDTH-2

    if bgx2 < -WINDOW_WIDTH:
        bgx2 = WINDOW_WIDTH-2

    screen.blit(img_bg, (bgx1, 0))
    screen.blit(img_bg, (bgx2, 0))


    """PIPES"""

    first_pipes.clear()

    for idx, pipe in enumerate(pipe_list):
        if idx in [0, 1]:
            first_pipes.append(pipe)

        if pipe.x < -pipe.width:
            pipe_list.remove(pipe)

        pipe.draw()
        pipe.move()

    #IF THE BIRDS HAVE PASSED THE FIRST PIPES, PUT THEM
    #ON THE END OF THE LIST SO THE BIRDS CAN FOCUS ON THE PIPES AHEAD
    if first_pipes[0].x < BIRD_X - first_pipes[0].width:
        pipe_list = pipe_list[2:]
        pipe_list += first_pipes

        score += 1
        if score > top_score:
            top_score = score

    """SPAWN NEW PIPES"""

    spawn_timer -= 1

    if spawn_timer <= 0:

        pipe_list += spawn_pipes()

        spawn_timer = 4*FPS

    """BIRDS"""

    alive = len(bird_list)

    for bird in bird_list:

        if bird.is_alive and bird.fitness < round_timer_max:
            bird.draw()
            bird.fall()

            bird.should_jump()
            bird.jump()
            bird.colliding()
        else:
            alive -= 1

    """NEW GENERATION"""

    round_timer -= 1

    if alive == 0:

        round_timer_max = gen_lifetime * FPS if gen < max_gens else float('inf')

        round_timer = round_timer_max
        spawn_timer = 4 * FPS

        pipe_list = spawn_pipes()
        first_pipes.clear()
        first_pipes += pipe_list

        gen += 1
        score = 0

        winners = sorted(bird_list, key=lambda b: b.fitness, reverse=True)[:int(gen_size * pick_rate/100)]
        bird_list.clear()

        for winner in winners:
            bird_list += winner.offsprings()

        #If winners produce too few offsprings
        while len(bird_list) < gen_size:
            bird_list.append(Bird())

    """BUTTON FOR EDITING PARAMETERS"""

    screen.blit(img_params, (button_params.x, button_params.y))

    """TEXTS"""

    text_gen = font_data.render(f"Gen: {gen}/{max_gens}", True, (230, 230, 230))
    text_next_gen = font_data.render(f"Next gen: {round(round_timer/FPS, 1)} s", True, (230, 230, 230))
    text_alive = font_data.render(f"Alive: {alive}", True, (230, 230, 230))
    text_score = font_data.render(f"Top score: {top_score}", True, (230, 230, 230))

    screen.blit(text_gen, (10, 25))
    screen.blit(text_alive, (10, 75))
    screen.blit(text_next_gen, (175, 25))
    screen.blit(text_score, (175, 75))

    pygame.display.flip()
    clock.tick(FPS)

