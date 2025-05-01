import math
import numpy as np
import random
import pygame
import time

from typing import Literal, Sequence
from utils import process_vector, default_calc_pos_vel, default_calc_acc
class Body:
    
    def __init__(self, pos: Sequence[int], vel: Sequence[int], acc: Sequence[int], mass: float, fixed:bool=False,type:Literal['star','planet','particle']=None, color:str=None, id=None) -> 'Body':
        self.pos = process_vector(pos)
        self.vel = process_vector(vel)
        self.acc = process_vector(acc)
        
        self.fixed = fixed
        self.type = type
        self.color = color
        self.mass = mass
        
        self.id = id
        
        self.first_pos = self.pos
        
    def draw(self, screen, screen_pos: pygame.Vector2, scale: float, cam_pos, screen_width, screen_height):
        color = self.color if (isinstance(self.color, tuple) or isinstance(self.color, list)) else (255,255,255)
        radius = max(1, int(2 * math.sqrt(self.mass) * scale))
        if self.type == "star":
            glow_strength = 6  
            for i in range(glow_strength, 0, -1):
                alpha = int(255 * (i / glow_strength) * 0.2) 
                alpha = min(alpha, 255) 
                glow_color = (*color[:3], alpha)

                glow_radius = radius + i * 1.5
                glow_surf_size = glow_radius * 2
                glow_surf = pygame.Surface((glow_surf_size, glow_surf_size), pygame.SRCALPHA)

                pygame.draw.circle(glow_surf, glow_color, (glow_surf_size // 2, glow_surf_size // 2), glow_radius)
                screen.blit(glow_surf, (screen_pos.x - glow_surf_size // 2, screen_pos.y - glow_surf_size // 2))
        pygame.draw.circle(screen, color,
            (int(screen_pos.x), int(screen_pos.y)),
            radius
        )
    
    def print_pos(self):
        print(f'Body <{self.id}> x={self.pos[0]} y={self.pos[1]}')
    
    def update(self, bodies: list['Body'], kind: Literal['default', 'barnes-hut', 'fast-multipole']='default', trail: bool=False):
        match (kind):
            case 'default':
                self.update_default(bodies, trail)
            case 'barnes-hut':
                raise ValueError('kind "barnes-hut" not implemented for .update() in body.')
            case 'fast-multipole':
                raise ValueError('kind "fast-multipole" not implemented for .update() in body.')
    
    
    def u_update_default(self, dt):
        if self.fixed:
            return
        
        self.pos, self.vel = default_calc_pos_vel(self.pos, self.vel, self.acc, dt)
        self.acc = process_vector([0, 0])
        # self.print_pos()
    
    def update_default(self, bodies: list['Body'], trail: bool =False, dt= 0.005):
      
        MIN = 0.0001
        
        for body in bodies:
            body.acc = np.zeros_like(body.pos)
        
        for i in range(len(bodies)):
            p1 = bodies[i].pos
            m1 = bodies[i].mass
            for j in range(i+1, len(bodies)):
                p2 = bodies[j].pos
                m2 = bodies[j].mass
                
                i_acc, j_acc = default_calc_acc(
                    p2, p1,
                    MIN,
                    m1, m2,
                    bodies[i].acc,
                    bodies[j].acc
                )
                bodies[i].acc = i_acc
                bodies[j].acc = j_acc
        for body in bodies:
            body.u_update_default(dt)
        
        
