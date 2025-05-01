import numpy as np
import random
import math


from numba import njit
from typing import Sequence

def create_rand_body(sun_mass, rel_pos:list=None):
        
    from Body import Body
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

@njit
def process_vector(vector: Sequence):
    arr = np.array(vector, dtype=np.float64)
    assert arr.shape == (2,), "Must be a 1D vector with 2 floats"
    return arr

@njit
def default_calc_pos_vel(pos, vel, acc, dt):
    pos += vel * dt
    vel += acc * dt
    return pos, vel
    
    
@njit
def default_calc_acc(p2, p1, MIN, m_1, m_2, i_acc, j_acc):
    r = p2 - p1
    mag_sq = np.dot(r, r)
    safe_mag_sq = np.maximum(mag_sq, MIN**2)
    inv_dist_cube = 1.0 / (safe_mag_sq * np.sqrt(safe_mag_sq))
    force = r * inv_dist_cube

    i_acc += m_2 * force
    j_acc -= m_1 * force
    return i_acc, j_acc