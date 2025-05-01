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
        self.paused = False
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
        
        
    def sim(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height),)
        
        pygame.display.set_caption('Orbiergon')
        self.running = True
        self.simulation_thread = threading.Thread(target=self.run)
        
        self.simulation_thread.start()
        self.run_render()
    
    def create_rand_body(self, sun_mass, rel_pos:list=None):
        
        r = random.uniform(50, 300)
        theta = random.random() * math.tau
        x = math.cos(theta) * r if not rel_pos else rel_pos[0] + (math.cos(theta) * r)
        y = math.sin(theta) * r if not rel_pos else rel_pos[1] + (math.sin(theta) * r)
        if random.random() < 0.15:
            min_p, max_p = 0.005, 0.01
        else:
            min_p, max_p = 0.001, 0.004
        m = random.uniform(min_p * sun_mass, max_p * sun_mass)
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
            if not self.paused:
                with self.lock:
                    for body in self.bodies:
                        body.update(self.bodies, 'default', self.trail)
                time.sleep(0.00016)

    def run_render(self):
        BLACK = (0, 0, 0)
        RED = (200, 0, 0)
        WHITE = (255, 255, 255)

        font = pygame.font.SysFont("Arial", 18)
        clock = pygame.time.Clock()
        close_button_rect = pygame.Rect(10, 10, 30, 30)
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
                    if event.button == 1 and close_button_rect.collidepoint(event.pos):
                        self.running = False
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 3:
                        self.trail = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.paused = not self.paused        
                
            with self.lock:
                bodies = list(self.bodies)
            anchor = next((b for b in bodies if b.fixed), None)
            if anchor:
                self.cam_pos = pygame.Vector2(anchor.pos[0], anchor.pos[1])
            else:
                avg_x = sum(b.pos[0] for b in bodies)/len(bodies)
                avg_y = sum(b.pos[1] for b in bodies)/len(bodies)
                self.cam_pos = pygame.Vector2(avg_x, avg_y)
            self.screen.fill((0, 0, 0))
            w, h = self.screen_width, self.screen_height
            for b in bodies:
                rel = pygame.Vector2(b.pos[0], b.pos[1]) - self.cam_pos
                screen_pos = rel * self.scale + pygame.Vector2(w/2, h/2)
                b.draw(self.screen, screen_pos, self.scale, self.cam_pos, self.screen_width, self.screen_height)
            
            
            if not close_button_rect.collidepoint((mx, my)):
                pygame.draw.rect(self.screen,BLACK, close_button_rect)    
            else:
                pygame.draw.rect(self.screen, RED, close_button_rect)
            text = font.render("X", True, WHITE)
            self.screen.blit(text, (close_button_rect.x + 8, close_button_rect.y + 5))
            fps = clock.get_fps()
            fps_text = font.render(f"FPS: {fps:.0f}", True, (255, 255, 255))
            self.screen.blit(fps_text, (40, 10))
            if self.paused:
                paused_text = font.render(f"PAUSED", False, (255, 0, 0))
                self.screen.blit(paused_text, (40,60))
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
    random.seed(1000)
    bodies = []
    # sun = Body(
    #     pos=[0.0, 0.0],
    #     vel=[0.1, 0.1],
    #     acc=[0.0, 0.0],
    #     mass=400,
    #     fixed=False,
    #     color=(230, 230, 100),
    #     # type='star'
    # )
    # bodies.append(sun)
    
    # for n in range(2):
    #    bodies.append(Simulation().create_rand_body(250, [0, 0]))
    
    s = Body(
        [0.0,0.0],
        [0.0,0.0],
        [0.0,0.0],
        400,
        fixed=True,
        color=(230,230,0),
        type='star'
    )
    bodies.append(s)
    for n in range(10):
        bodies.append(Simulation().create_rand_body(400, [0,0]))
    
    sim = Simulation(bodies, screen_width=1280, screen_height=720)
    sim.sim()

