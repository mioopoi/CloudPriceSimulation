import math
import random

from machine import *


L_MIN = 1    # minimum length of a job
L_MAX = 100  # maximum length of a job


def gen_data(num_jobs, num_slots):
    global L_MIN, L_MAX

    job_set = {}
    pm_set = {}
    ele_price = [0.0]*num_slots

    max_t = num_slots - 1
    min_i = int(math.ceil(max_t / 5))

    # generate VMs
    for i in range(1, num_jobs+1):
        start_time = random.randint(0, max_t - min_i)
        # end_time = random.randint(start_time+min_i, max_t)
        end_time = min(start_time + random.randint(1, num_slots/20), max_t)
        L_MIN = min(end_time - start_time + 1, L_MIN)
        L_MAX = max(end_time - start_time + 1, L_MAX)

        demand = -1.0
        while demand <= 0.0 or demand > 1.0:
            demand = random.normalvariate(0.16, 0.1)
        job = Job(i, start_time, end_time, demand)
        job_set[i] = job

    # generate PMs
    # We assume the number of PMs is equal to the number of jobs.
    num_pms = num_jobs / 2
    for i in range(1, num_pms+1):
        pm = PhysicalMachine(i, num_slots=num_slots)
        pm_set[i] = pm

    # generate electricity price
    """
    for i in range(0, num_slots):
        price = 0.0
        while price <= 0.0 or price > 16.0:
            price = random.normalvariate(0.5, 0.2)
        ele_price[i] = price
    """
    i = 0
    while i < num_slots:
        price = 0.0
        while price <= 0.0 or price > 16.0:
            price = random.normalvariate(0.5, 0.2)
        j = i + 6
        while i < num_slots and i < j:
            ele_price[i] = price
            i += 1

    return [job_set, pm_set, ele_price]


def load_data():
    pass
    ## TODO
