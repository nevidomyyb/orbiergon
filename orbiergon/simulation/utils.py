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
    safe_mag_sq = max(mag_sq, MIN**2)
    mag = np.sqrt(safe_mag_sq)
    
    temp = r / (np.maximum(mag_sq, MIN) * mag)
    i_acc += m_2 * temp
    j_acc -= m_1 * temp
    return i_acc, j_acc