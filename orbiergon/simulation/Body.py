import math
import numpy as np
import random
import pygame
import time

from typing import Literal, Sequence
from utils import process_vector, default_calc_pos_vel, default_calc_acc, calculate_all_accelerations, calculate_accelerations_parallel
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
        
        # Extract positions and masses for vectorized calculation
        positions = np.array([body.pos for body in bodies])
        masses = np.array([body.mass for body in bodies])
        fixed = np.array([body.fixed for body in bodies])
        
        # Use parallel calculation for better performance with many bodies
        n_bodies = len(bodies)
        if n_bodies >= 30:  # Use parallel version for larger simulations
            accelerations = calculate_accelerations_parallel(positions, masses, MIN)
        else:  # Use regular version for smaller simulations
            accelerations = calculate_all_accelerations(positions, masses, MIN)
        
        # Update each body with its new acceleration
        for i, body in enumerate(bodies):
            if not body.fixed:  # Skip fixed bodies
                body.acc = accelerations[i]
                body.u_update_default(dt)
        
        
