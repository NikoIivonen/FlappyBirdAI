import pygame
from random import randint, randrange, uniform, choice
from inputNeuron import InputNeuron
from ouputNeuron import OutputNeuron

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((500, 800))

font_data = pygame.font.SysFont("Arial", 30, True)


class Bird:

    def __init__(self):
        self.x = 150
        self.y = 400
        self.width = 35
        self.acc = 0.02
        self.v = 1.5
        self.bird = pygame.Rect(self.x, self.y, self.width, self.width)
        self.jumping = False
        self.jump_time = 1*60
        self.is_alive = True
        self.fitness = 0

        self.input_y = InputNeuron(uniform(-2, 2))
        self.input_ty = InputNeuron(uniform(-2, 2))
        self.input_by = InputNeuron(uniform(-2, 2))

        self.output = OutputNeuron()

    def draw(self):
        self.bird = pygame.Rect(self.x, self.y, self.width, self.width)
        pygame.draw.rect(screen, (255, 0, 0), self.bird)

    def fall(self):
        if self.y < 1000:
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
            if self.bird.colliderect(pipe.pipe) or self.y <= 0 or self.y >= 800-self.width:
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

        children = []

        for _ in range(10):
            yw = self.input_y.weight * uniform(0.95, 1.05) * choice([-1,1,1,1,1,1,1,1,1,1])
            tyw = self.input_ty.weight * uniform(0.95, 1.05) * choice([-1,1,1,1,1,1,1,1,1,1])
            byw = self.input_by.weight * uniform(0.95, 1.05) * choice([-1,1,1,1,1,1,1,1,1,1])

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

    def draw(self):
        self.pipe = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.color, self.pipe)

    def move(self):
        self.x -= 1.5


def spawn_pipes():
    height_top = randint(200, 450)
    gap = 150
    height_bottom = 800 - gap - height_top
    top_bottom = 800 - height_bottom

    pipe_top = Pipe(0, height_top)
    pipe_bottom = Pipe(top_bottom, height_bottom)

    return [pipe_top, pipe_bottom]

pipe_list = spawn_pipes()
first_pipes = []
first_pipes += pipe_list
spawn_timer = 4*60

bird_list = [Bird() for _ in range(100)]

gen = 1

round_timer_max = 20*60
round_timer = round_timer_max

while True:

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            exit()

    screen.fill((225, 225, 225))

    """PIPES"""

    first_pipes.clear()

    for idx, pipe in enumerate(pipe_list):
        if idx in [0, 1]:
            first_pipes.append(pipe)

        pipe.draw()
        pipe.move()

    #IF THE BIRDS HAVE PASSED THE FIRST PIPES, PUT THEM
    #ON THE END OF THE LIST SO THE BIRDS CAN FOCUS ON THE PIPES AHEAD
    if first_pipes[0].x < 150 - first_pipes[0].width:
        pipe_list = pipe_list[2:]
        pipe_list += first_pipes

    """SPAWN NEW PIPES"""

    spawn_timer -= 1

    if spawn_timer <= 0:

        pipe_list += spawn_pipes()

        spawn_timer = 4*60

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

    """NEW GEN"""

    if alive == 0:

        round_timer = round_timer_max
        spawn_timer = 4 * 60

        pipe_list = spawn_pipes()
        first_pipes.clear()
        first_pipes += pipe_list

        gen += 1

        winners = sorted(bird_list, key=lambda b: b.fitness, reverse=True)[:10]
        bird_list.clear()

        for winner in winners:
            bird_list += winner.offsprings()

    """TEXTS"""

    round_timer -= 1

    text_gen = font_data.render(f"GEN: {gen}", True, (0,0,0))
    text_next_gen = font_data.render(f"Next gen in: {round_timer}", True, (0, 0, 0))
    text_alive = font_data.render(f"Alive: {alive}", True, (0,0,0))

    screen.blit(text_gen, (25, 25))
    screen.blit(text_alive, (25, 75))
    screen.blit(text_next_gen, (25, 125))

    pygame.display.flip()
    clock.tick(60)

