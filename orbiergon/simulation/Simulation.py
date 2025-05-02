import pygame
import time
import threading
import random

from Body import Body
from utils import create_rand_body
from EventDispatcher import EventDispatcher

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
        
        self.event_dispatcher = EventDispatcher()
        self.register_events()
        
    def register_events(self,):
        self.event_dispatcher.register(pygame.MOUSEWHEEL, self.zoom)
        self.event_dispatcher.register(pygame.MOUSEBUTTONDOWN, self.pam)
        self.event_dispatcher.register(pygame.MOUSEBUTTONUP, self.pam)
        self.event_dispatcher.register(pygame.MOUSEMOTION, self.pam)
    def sim(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        
        pygame.display.set_caption('Orbiergon')
        icon = pygame.image.load('orbiergon/orbiergon.png')
        pygame.display.set_icon(icon)
        self.running = True
        self.simulation_thread = threading.Thread(target=self.run)
        
        self.simulation_thread.start()
        self.run_render()
    
    def run(self):
        while self.running:
            if not self.paused:
                with self.lock:
                    for body in self.bodies:
                        body.update(self.bodies, 'default', self.trail)
                time.sleep(0.00016)

    def run_render(self):
        clock = pygame.time.Clock()
            
        while self.running:
            self.mx, self.my = pygame.mouse.get_pos()
            for event in pygame.event.get():
                self.event_dispatcher.dispatch(event)
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.paused = not self.paused   
                
            with self.lock:
                bodies = list(self.bodies)
                
            self.screen.fill((0, 0, 0))
            w, h = self.screen_width, self.screen_height
            for b in bodies:
                rel = pygame.Vector2(b.pos[0], b.pos[1]) - self.cam_pos
                screen_pos = rel * self.scale + pygame.Vector2(w/2, h/2)
                b.draw(self.screen, screen_pos, self.scale, self.cam_pos, self.screen_width, self.screen_height)
            
            
            self.draw_things(clock)
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
    
    def draw_things(self,clock):
        BLACK = (0, 0, 0)
        RED = (200, 0, 0)
        WHITE = (255, 255, 255)
        font = pygame.font.SysFont("Arial", 18)
        fps = clock.get_fps()
        fps_text = font.render(f"FPS: {fps:.0f}", True, (255, 255, 255))
        self.screen.blit(fps_text, (40, 10))
        if self.paused:
            paused_text = font.render(f"PAUSED", False, (255, 0, 0))
            self.screen.blit(paused_text, (40,60))
    
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

    def pam(self, event: pygame.event.Event):
        if event.type in (pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN) and event.button == 2 and pygame.mouse.get_pressed()[1]:
            self.pan_active = True
            self.pan_last = pygame.Vector2(pygame.mouse.get_pos())
        elif event.type in (pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN) and  event.button == 2 and pygame.mouse.get_pressed()[1] is False:
            self.pan_active = False
        elif event.type == pygame.MOUSEMOTION and self.pan_active:
            current_mouse_pos = pygame.Vector2(event.pos)
            delta = current_mouse_pos - self.pan_last
            self.cam_pos -= (delta / self.scale)
            self.pan_last = current_mouse_pos
        

    def zoom(self, event):
        before = pygame.Vector2(self.mx, self.my)
        world_before = (before - pygame.Vector2(self.screen_width/2, self.screen_height/2)) / self.scale + self.cam_pos
        zoom_factor = 1 + event.y * self.zoom_sensitivity
        self.scale *= zoom_factor
        self.cam_pos = world_before - (before - pygame.Vector2(self.screen_width/2, self.screen_height/2)) / self.scale
        
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
    #    bodies.append(create_rand_body(250, [0, 0]))
    
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
    for n in range(30):
        bodies.append(create_rand_body(400, [0,0]))
    
    sim = Simulation(bodies, screen_width=1280, screen_height=720)
    sim.sim()

