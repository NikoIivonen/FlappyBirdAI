import pygame
from random import randint, randrange, uniform, choice
from inputNeuron import InputNeuron
from ouputNeuron import OutputNeuron
from parameters import edit_params, show_error, show_info
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
img_load = pygame.image.load("imgs/load.png")
img_new_training = pygame.image.load("imgs/new_training.png")
img_mutate = pygame.image.load("imgs/mutate.png")
img_reset = pygame.image.load("imgs/reset.png")


PIPE_TOP_HEIGHT = 59

bgx1 = 0
bgx2 = WINDOW_WIDTH

font_data = pygame.font.SysFont("Arial", 28, True)

max_gens = 100
gen_lifetime = 20 #seconds
gen_size = 100
pick_rate = 10 #percent


class Bird:

    def __init__(self):
        self.x = BIRD_X
        self.y = WINDOW_HEIGHT/2
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

        self.init_w1 = self.input_y.weight
        self.init_w2 = self.input_ty.weight
        self.init_w3 = self.input_by.weight

        self.output = OutputNeuron()

    def init_start(self):
        self.y = WINDOW_HEIGHT/2
        self.acc = 0.02
        self.v = 1.5
        self.jumping = False
        self.jump_time = 1*60
        self.is_alive = True
        self.anim_state = 0

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

    def weight_sign(self):
        return choice([-1, 1, 1, 1, 1, 1, 1, 1, 1, 1])

    def reset_weights(self):
        self.input_y.weight = self.init_w1
        self.input_ty.weight = self.init_w2
        self.input_by.weight = self.init_w3

    def mutate_weights(self):
        self.input_y.weight *= uniform(0.95, 1.05) * self.weight_sign()
        self.input_ty.weight *= uniform(0.95, 1.05) * self.weight_sign()
        self.input_by.weight *= uniform(0.95, 1.05) * self.weight_sign()

    def offsprings(self):

        children = []

        amount = floor(gen_size / (gen_size * pick_rate/100))

        for _ in range(amount):
            yw = self.input_y.weight * uniform(0.95, 1.05) * self.weight_sign()
            tyw = self.input_ty.weight * uniform(0.95, 1.05) * self.weight_sign()
            byw = self.input_by.weight * uniform(0.95, 1.05) * self.weight_sign()

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
    height_top = randint(150, 500)
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


round_timer = gen_lifetime * FPS

button_params = pygame.Rect(WINDOW_WIDTH-120, 20, 110, 50)
button_load = pygame.Rect(WINDOW_WIDTH-120, 75, 110, 50)
button_new_training = pygame.Rect(WINDOW_WIDTH-120, 20, 110, 50)
button_mutate = pygame.Rect(WINDOW_WIDTH-120, 75, 110, 50)
button_reset = pygame.Rect(WINDOW_WIDTH-120, 130, 110, 50)


def button_clicked(button):
    mx, my = pygame.mouse.get_pos()
    if button.collidepoint(mx, my):
        return True
    return False

trained_bird = None

while True:

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            exit()

        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if button_clicked(button_params) and trained_bird is None:
                max_gens, gen_size, gen_lifetime, pick_rate = edit_params(max_gens, gen_size, gen_lifetime, pick_rate)

            elif button_clicked(button_mutate) and trained_bird is not None:
                trained_bird.mutate_weights()

            elif button_clicked(button_reset) and trained_bird is not None:
                trained_bird.reset_weights()

            elif button_clicked(button_new_training) and trained_bird is not None:
                trained_bird = None

                FPS = 60

                pipe_list = spawn_pipes()
                first_pipes = []
                first_pipes += pipe_list
                spawn_timer = 4 * FPS

                score = 0
                top_score = 0

                bird_list = [Bird() for _ in range(gen_size)]

                gen = 1

                round_timer = gen_lifetime * FPS

            elif button_clicked(button_load) and trained_bird is None:
                try:
                    with open("trained_weights.txt", "r") as file:
                        lines = file.readlines()
                        w1 = float(lines[0][3:-1]) #newline char
                        w2 = float(lines[1][3:-1]) #newline char
                        w3 = float(lines[2][3:])

                        trained_bird = Bird()
                        trained_bird.input_y = InputNeuron(w1)
                        trained_bird.input_ty = InputNeuron(w2)
                        trained_bird.input_by = InputNeuron(w3)

                        trained_bird.init_w1 = w1
                        trained_bird.init_w2 = w2
                        trained_bird.init_w3 = w3

                        bird_list.clear()
                        bird_list.append(trained_bird)
                        round_timer = float('inf')

                        score = 0

                except:
                    show_error("Invalid configuration file")

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

        if bird.is_alive:
            bird.draw()
            bird.fall()

            bird.should_jump()
            bird.jump()
            bird.colliding()
        else:
            alive -= 1

    """NEW GENERATION"""

    round_timer -= 1

    if alive == 0 or round_timer <= 0:

        spawn_timer = 4 * FPS

        pipe_list = spawn_pipes()
        first_pipes.clear()
        first_pipes += pipe_list
        score = 0

        if trained_bird is None:

            round_timer = gen_lifetime * FPS

            gen += 1

            winners = sorted(bird_list, key=lambda b: b.fitness, reverse=True)[:int(gen_size * pick_rate/100)]
            bird_list.clear()

            """IF THE TRAINING IS COMPLETE, UPDATE THE WEIGHTS IN THE SAVE FILE"""

            if gen == max_gens + 1:
                with open("trained_weights.txt", "w") as file:
                    best = winners[0]
                    file.write(f"w1:{best.input_y.weight}\n")
                    file.write(f"w2:{best.input_ty.weight}\n")
                    file.write(f"w3:{best.input_by.weight}")

                show_info("Training complete!\nLoading a trained bird now available.")

            for winner in winners:
                bird_list += winner.offsprings()

            #If winners produce too few offsprings
            while len(bird_list) < gen_size:
                bird_list.append(Bird())

        else:
            trained_bird.init_start()

    """BUTTONS"""

    if trained_bird is None:
        screen.blit(img_params, (button_params.x, button_params.y))
        screen.blit(img_load, (button_load.x, button_load.y))
    else:
        screen.blit(img_new_training, (button_new_training.x, button_new_training.y))
        screen.blit(img_mutate, (button_mutate.x, button_mutate.y))
        screen.blit(img_reset, (button_reset.x, button_reset.y))

    """TEXTS"""

    text_gen = font_data.render(f"Gen: {gen}/{max_gens}", True, (230, 230, 230))
    text_next_gen = font_data.render(f"Next gen: {round(round_timer/FPS, 1)} s", True, (230, 230, 230))
    text_alive = font_data.render(f"Alive: {alive}", True, (230, 230, 230))
    text_top_score = font_data.render(f"Top score: {top_score}", True, (230, 230, 230))
    text_score = font_data.render(f"Score: {score}", True, (230, 230, 230))

    if trained_bird is None:
        screen.blit(text_gen, (10, 25))
        screen.blit(text_alive, (10, 75))
        screen.blit(text_next_gen, (175, 25))
        screen.blit(text_top_score, (175, 75))
    else:
        screen.blit(text_score, (10, 25))
        screen.blit(text_top_score, (10, 75))

    pygame.display.flip()
    clock.tick(FPS)

