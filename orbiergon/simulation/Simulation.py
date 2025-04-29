import pygame
import time
import threading
import random

from Body import Body

class Simulation:
    def __init__(self, bodies: list[Body]=[]):
        self.bodies = bodies
        self.running = False
        self.simulation_thread = None
        self.render_thread = None
        self.lock = threading.Lock()
        self.screen = None
        random.seed(1000)
        
    def run(self):
        self.running = True
        while self.running:
            with self.lock:
                for body in self.bodies:
                    body.update(self.bodies)
            time.sleep(0.001)
            
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
    sim = Simulation()
    sim.add(Body([10, 5], 5, 2, 10, id=random.randint(0,10000000)))
    sim.add(Body([15, 8], 4, 7, 29,id=random.randint(0,10000000)))
    sim.run()