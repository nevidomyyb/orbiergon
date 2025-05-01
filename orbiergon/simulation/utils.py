from numba import njit
import numpy as np

from typing import Sequence

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