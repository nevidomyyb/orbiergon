import pygame
import time
import threading
import random
import math

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
        self.trail_surface = None
        self.trail_fade_rate = 2  # Higher values = faster fade
        
        self.frame_skip = 0  
        self.frame_counter = 0
        self.target_fps = 60
        self.adaptive_performance = True
        
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
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.HWSURFACE | pygame.DOUBLEBUF)
        
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
        
        # Create trail surface if trails are enabled
        if self.trail:
            self.trail_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            self.trail_surface.fill((0, 0, 0, 0))
            
        while self.running:
            self.mx, self.my = pygame.mouse.get_pos()
            for event in pygame.event.get():
                self.event_dispatcher.dispatch(event)
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_t:
                    self.trail = not self.trail
                    if self.trail and self.trail_surface is None:
                        self.trail_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
                        self.trail_surface.fill((0, 0, 0, 0))
            
            # Adaptive frame skipping based on body count and current FPS
            if self.adaptive_performance:
                current_fps = clock.get_fps()
                body_count = len(self.bodies)
                
                if body_count > 50 and current_fps < 30:
                    self.frame_skip = 2
                elif body_count > 30 and current_fps < 45:
                    self.frame_skip = 1
                else:
                    self.frame_skip = 0
            
            # Skip frames if needed
            self.frame_counter += 1
            if self.frame_skip > 0 and self.frame_counter % (self.frame_skip + 1) != 0:
                clock.tick(self.target_fps)
                continue
                
            with self.lock:
                bodies = list(self.bodies)
            
            # Clear screen
            self.screen.fill((0, 0, 0))
            
            # Handle trails
            if self.trail and self.trail_surface is not None:
                # Fade existing trails
                fade = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
                fade.fill((0, 0, 0, self.trail_fade_rate))
                self.trail_surface.blit(fade, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
                
                # Draw trails to trail surface
                w, h = self.screen_width, self.screen_height
                for b in bodies:
                    if not b.fixed:  
                        rel = pygame.Vector2(b.pos[0], b.pos[1]) - self.cam_pos
                        screen_pos = rel * self.scale + pygame.Vector2(w/2, h/2)
                        color = b.color if (isinstance(b.color, tuple) or isinstance(b.color, list)) else (255,255,255)
                        trail_color = (*color[:3], 100)  # Semi-transparent
                        pygame.draw.circle(self.trail_surface, trail_color, 
                                        (int(screen_pos.x), int(screen_pos.y)), 
                                        max(1, int(1 * math.sqrt(b.mass) * self.scale / 2)))
                
                # Draw trail surface to screen
                self.screen.blit(self.trail_surface, (0, 0))
            
            # Draw bodies
            w, h = self.screen_width, self.screen_height
            for b in bodies:
                rel = pygame.Vector2(b.pos[0], b.pos[1]) - self.cam_pos
                screen_pos = rel * self.scale + pygame.Vector2(w/2, h/2)
                
                # Only draw bodies that are within or near the screen bounds
                if (-50 <= screen_pos.x <= w+50 and -50 <= screen_pos.y <= h+50):
                    b.draw(self.screen, screen_pos, self.scale, self.cam_pos, self.screen_width, self.screen_height)
            
            self.draw_things(clock)
            pygame.display.flip()
            clock.tick(self.target_fps)

        pygame.quit()
    
    def draw_things(self, clock):
        BLACK = (0, 0, 0)
        RED = (200, 0, 0)
        YELLOW = (255, 255, 0)
        GREEN = (0, 200, 0)
        WHITE = (255, 255, 255)
        
        font = pygame.font.SysFont("Arial", 18)
        small_font = pygame.font.SysFont("Arial", 14)
        
        # FPS counter with color coding
        fps = clock.get_fps()
        fps_color = GREEN if fps >= 55 else (YELLOW if fps >= 30 else RED)
        fps_text = font.render(f"FPS: {fps:.0f}", True, fps_color)
        self.screen.blit(fps_text, (40, 10))

        if self.paused:
            paused_text = font.render("PAUSED", True, RED)
            self.screen.blit(paused_text, (self.screen_width - 120, 10))
    
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
        color=(255,0 , 255),
        type='star'
    )
    p = Body(
        [0.0, 120.0],
        [0.5, 0.5],
        [0.0, 0.0],
        250,
        fixed=False,
        color=(255,0 , 255),
        type='star'
    )
    bodies.append(s)
    # bodies.append(p)
    for n in range(20):
        bodies.append(create_rand_body(400, [0,0]))
    
    sim = Simulation(bodies, screen_width=1280, screen_height=720)
    sim.sim()

