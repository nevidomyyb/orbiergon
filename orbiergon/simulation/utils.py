import numpy as np
import random
import math
import concurrent.futures
import os

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

@njit
def calculate_all_accelerations(positions, masses, min_distance):
    n = len(positions)
    accelerations = np.zeros_like(positions)
    
    for i in range(n):
        for j in range(i+1, n):
            p1, p2 = positions[i], positions[j]
            m1, m2 = masses[i], masses[j]
            
            r = p2 - p1
            mag_sq = np.dot(r, r)
            safe_mag_sq = np.maximum(mag_sq, min_distance**2)
            inv_dist_cube = 1.0 / (safe_mag_sq * np.sqrt(safe_mag_sq))
            force = r * inv_dist_cube
            
            accelerations[i] += m2 * force
            accelerations[j] -= m1 * force
    
    return accelerations

@njit
def calculate_acceleration_chunk(start_idx, end_idx, positions, masses, min_distance):
    n = len(positions)
    accelerations = np.zeros_like(positions)
    
    for i in range(start_idx, end_idx):
        for j in range(i+1, n):
            p1, p2 = positions[i], positions[j]
            m1, m2 = masses[i], masses[j]
            
            r = p2 - p1
            mag_sq = np.dot(r, r)
            safe_mag_sq = np.maximum(mag_sq, min_distance**2)
            inv_dist_cube = 1.0 / (safe_mag_sq * np.sqrt(safe_mag_sq))
            force = r * inv_dist_cube
            
            accelerations[i] += m2 * force
            accelerations[j] -= m1 * force
    
    return accelerations

def calculate_accelerations_parallel(positions, masses, min_distance, num_threads=None):
    if num_threads is None:
        num_threads = max(1, os.cpu_count() - 1)  # Leave one CPU for other tasks
    
    n = len(positions)
    if n < 20 or num_threads <= 1:  # For small number of bodies, use the sequential version
        return calculate_all_accelerations(positions, masses, min_distance)
    
    # Divide work into chunks
    chunk_size = max(1, n // num_threads)
    chunks = [(i, min(i + chunk_size, n)) for i in range(0, n, chunk_size)]
    
    # Calculate accelerations in parallel
    accelerations = np.zeros_like(positions)
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_chunk = {executor.submit(calculate_acceleration_chunk, start, end, positions, masses, min_distance): (start, end) 
                          for start, end in chunks}
        
        for future in concurrent.futures.as_completed(future_to_chunk):
            chunk_acc = future.result()
            accelerations += chunk_acc
    
    return accelerations