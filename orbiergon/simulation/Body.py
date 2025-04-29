import math
import numpy
import random
import pygame
import time

from typing import Literal

class Body:
    
    def __init__(self, pos: list, vel: float, acc: float, mass: float, fixed:bool=False,type:Literal['star','planet','particle']=None, color:str=None, id=None) -> 'Body':
        self.x = pos[0]
        self.y = pos[1]
        
        self.vx = vel[0]
        self.vy = vel[1]
        
        self.ax = acc[0]
        self.ay = acc[1]
        
        self.fixed = fixed
        self.type = type
        self.color = color
        self.mass = mass
        
        self.id = id
    
        
    def draw(self, screen, screen_pos: pygame.Vector2, scale: float, cam_pos, screen_width, screen_height):
        if isinstance(self.color, tuple) or isinstance(self.color, list):
            color = self.color
        else:
            color = (255,255,255)
        radius = max(1, int(2 * math.sqrt(self.mass) * scale))
        pygame.draw.circle(screen, color,
                           (int(screen_pos.x), int(screen_pos.y)),
                           radius)
    
    def print_pos(self):
        print(f'Body <{self.id}> x={self.x} y={self.y}')
    
    def update(self, bodies: list['Body'], kind: Literal['default', 'barnes-hut', 'fast-multipole']='default', trail: bool=False):
        match (kind):
            case 'default':
                self.update_default(bodies, trail)
            case 'barnes-hut':
                raise ValueError('kind "barnes-hut" not implemented for .update() in body.')
            case 'fast-multipole':
                raise ValueError('kind "fast-multipole" not implemented for .update() in body.')
    
    def update_default(self, bodies: list['Body'], trail: bool =False, dt=0.1):
        if self.fixed:
            return
        self.ax = 0.0
        self.ay = 0.0
        self.trail = trail
        if self.trail:
            self.trail_tmp.append((self.x, self.y, time.time()))
            current_time = time.time()
            self.trail_tmp = [point for point in self.trail_tmp if current_time - point[2] <= self.trail_duration]
        a_max_global = 0.0
        for other in bodies:
            if other is self:
                continue
            dx = other.x - self.x
            dy = other.y - self.y
            dist_sq = dx*dx + dy*dy + 1e-5 ** 2
            inv_dist = 1.0 / math.sqrt(dist_sq)
            inv_dist3 = inv_dist * inv_dist * inv_dist
            f = 1 * other.mass * inv_dist3
            self.ax += f * dx
            self.ay += f * dy
        max_a = 50.0
        a_mag = math.hypot(self.ax, self.ay)
        if a_mag > max_a:
            factor = max_a/a_mag
            self.vx += factor * dt
            self.vy += factor * dt
        else:
            self.vx += self.ax * dt
            self.vy += self.ay * dt
        self.x  += self.vx * dt
        self.y  += self.vy * dt
        self.print_pos()
