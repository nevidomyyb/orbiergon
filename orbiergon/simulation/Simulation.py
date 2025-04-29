import pygame
import time
import threading
import random
import math
import numpy

from Body import Body

class Simulation:
    def __init__(self, bodies: list[Body]=[], screen_width=800, screen_height=600):
        self.bodies = bodies
        self.running = False
        self.simulation_thread = None
        self.render_thread = None
        self.lock = threading.Lock()
        self.screen = None
        self.trail = False
        
        self.cx = 0
        self.cy = 0
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.cam_pos = pygame.Vector2(0, 0) 
        self.scale   = 1.0                   
        self.zoom_sensitivity = 0.1         
        self.pan_active = False
        self.pan_last = pygame.Vector2(0, 0)
        # random.seed(1000)
        
    def sim(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('Orbiergon')
        self.running = True
        self.simulation_thread = threading.Thread(target=self.run)
        
        self.simulation_thread.start()
        self.run_render()
    
    def create_rand_body(self, sun_mass):
        r = random.uniform(100, 500)
        theta = random.random() * math.tau
        x = math.cos(theta) * r
        y = math.sin(theta) * r
        
        m = random.uniform(0.05 * sun_mass, 0.1 * sun_mass)
        v = math.sqrt(1 * sun_mass/r)
        vx = -math.sin(theta) * v
        vy = math.cos(theta) * v
        
        return Body(
            [x, y],
            [vx, vy],
            [0.0, 0.0],
            m,
            False,
            None,
            (200, 200, 255)
        )
    
    def run(self):
        while self.running:
            with self.lock:
                for body in self.bodies:
                    body.update(self.bodies)
            time.sleep(0.00016)

    def run_render(self):
        clock = pygame.time.Clock()
        while self.running:
            mx, my = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEWHEEL:
                    before = pygame.Vector2(mx, my)
                    world_before = (before - pygame.Vector2(self.screen_width/2, self.screen_height/2)) / self.scale + self.cam_pos
                    zoom_factor = 1 + event.y * self.zoom_sensitivity
                    self.scale *= zoom_factor
                    self.cam_pos = world_before - (before - pygame.Vector2(self.screen_width/2, self.screen_height/2)) / self.scale
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3:
                        self.trail = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 3:
                        self.trail = False
            with self.lock:
                bodies = list(self.bodies)
            anchor = next((b for b in bodies if b.fixed), None)
            if anchor:
                self.cam_pos = pygame.Vector2(anchor.x, anchor.y)
            else:
                avg_x = sum(b.x for b in bodies)/len(bodies)
                avg_y = sum(b.y for b in bodies)/len(bodies)
                self.cam_pos = pygame.Vector2(avg_x, avg_y)
            self.screen.fill((0, 0, 0))
            w, h = self.screen_width, self.screen_height
            for b in bodies:
                rel = pygame.Vector2(b.x, b.y) - self.cam_pos
                screen_pos = rel * self.scale + pygame.Vector2(w/2, h/2)
                b.draw(self.screen, screen_pos, self.scale)
                if self.trail:
                    print('Trail')

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
            
    def add(self, *args):
        """
        Positional argument Body or pos, vel, acc and mass.
        """
        if len(args) == 1 and isinstance(args[0], Body):
            self.bodies.append(args[0])
        elif len(args) == 4:
            self.bodies.append(Body(args[0], args[1], args[2], args[3]))
        else:
            raise ValueError('To add new body with fixed, color or kind value please use a Body instance in .add() method.')
if __name__ == "__main__":
    bodies = []
    sun = Body(
        pos=[0.0, 0.0],
        vel=[0.0, 0.0],
        acc=[0.0, 0.0],
        mass=1000,
        fixed=False,
        color=(255, 255, 0)
    )
    bodies.append(sun)
    for n in range(2):
       bodies.append(Simulation().create_rand_body(1000))
    sim = Simulation(bodies, screen_width=1280, screen_height=720)
    
    sim.sim()