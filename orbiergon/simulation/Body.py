import math
import numpy
import random

from typing import Literal

class Body:
    
    def __init__(self, pos: list, vel: float, acc: float, mass: float, fixed:bool=False,type:Literal['star','planet','particle']=None, color:str=None, id=None) -> 'Body':
        self.x = pos[0]
        self.y = pos[1]
        self.pos = [self.x, self.y]
        self.vel = vel
        self.acc = acc
        self.mass = mass
        self.type = type
        self.color = color
        self.fixed = fixed
        
        self.ax = 0
        self.ay = 0
        self.vx = 0
        self.vy = 0
        self.id = id
        
    def print_pos(self):
        print(f'Body <{self.id}> x={self.x} y={self.y}')
    
    def update(self, bodies: list['Body'], kind: Literal['default', 'barnes-hut', 'fast-multipole']='default'):
        match (kind):
            case 'default':
                self.update_default(bodies)
            case 'barnes-hut':
                raise ValueError('kind "barnes-hut" not implemented for .update() in body.')
            case 'fast-multipole':
                raise ValueError('kind "fast-multipole" not implemented for .update() in body.')
        
    def update_default(self, bodies: list['Body']):
        if self.fixed:
            return
        self.ax = 0
        self.ay = 0
        
        for body in bodies:
            if body is self :
                continue
            
            dx = body.x - self.x
            dy = body.y - self.y
            
            distance = math.hypot(dx, dy)
            force = 1 * self.mass * body.mass / distance ** 2
            
            fx = force * dx / distance
            fy = force * dy/distance
            
            self.ax = fx/self.mass
            self.ay = fy/self.mass
            
        self.vx += self.ax
        self.vy += self.ay
        
        self.x += self.vx
        self.y += self.vy
        self.pos = [self.x, self.y]
        self.print_pos()
            