import math
import random
import pandas as pd
import numpy as np
import os

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
        #start_time = random.randint(0, max_t - min_i)
        start_time = random.randint(0, min_i / 10)   # this setting is for online simulation
                                                     # (since the number of active PMs of OPT-LB is relatively small)
        # end_time = random.randint(start_time+min_i, max_t)
        end_time = min(start_time + random.randint(1, num_slots/5), max_t)
        L_MIN = min(end_time - start_time + 1, L_MIN)
        L_MAX = max(end_time - start_time + 1, L_MAX)

        demand = -1.0
        while demand <= 0.0 or demand > 1.0:
            demand = random.normalvariate(0.16, 0.1)
        job = Job(i, start_time, end_time, demand)
        job_set[i] = job
    # print L_MAX

    # generate PMs
    # We assume the number of PMs is equal to the number of jobs.
    num_pms = num_jobs
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


def load_data(num_jobs, num_slots=1000):
    global L_MIN, L_MAX

    # column_names = ['job_id', 'start_time', 'end_time', 'demand']
    # df = pd.read_csv('task_events_out.csv', sep=' ', header=None, names=column_names)
    # df = df.sort("start_time")

    job_set = {}
    count = 0
    min_s = float('inf')
    max_e = 0
    data_file = open("task_events_out.csv")
    '''
    # Read line by line
    for line in data_file:
        [job_id, start_time, end_time, demand] = line.split(' ')
        job_id, start_time, end_time, demand = count+1, int(start_time), int(end_time), float(demand)

        start_time, end_time = int(math.floor(float(start_time) / 60)), int(math.floor(float(end_time) / 60))
        if end_time > num_slots:
            continue
        min_s = min(min_s, start_time)
        max_e = max(max_e, end_time)

        L_MIN = min(end_time - start_time + 1, L_MIN)
        L_MAX = max(end_time - start_time + 1, L_MAX)

        job = Job(job_id, start_time, end_time, demand)
        job_set[job_id] = job

        count += 1
        if count >= num_jobs:
            break
    '''
    # Read random line
    size = 7000000
    while count < num_jobs:
        line = random_line(data_file, size)
        [job_id, start_time, end_time, demand] = line.split(' ')
        job_id, start_time, end_time, demand = count+1, int(start_time), int(end_time), float(demand)

        start_time, end_time = int(math.floor(float(start_time))), int(math.floor(float(end_time)))
        start_time = start_time % 1000
        end_time = end_time % 1000
        if start_time > end_time:
            tmp = start_time
            start_time = end_time
            end_time = tmp

        if end_time > num_slots or demand > 1.0:
            continue

        L_MIN = min(end_time - start_time + 1, L_MIN)
        L_MAX = max(end_time - start_time + 1, L_MAX)

        job = Job(job_id, start_time, end_time, demand)
        #print job_id, start_time, end_time, demand
        job_set[job_id] = job

        count += 1

    data_file.close()

    # print min_s, max_e

    # Generate PMs
    pm_set = {}
    num_pms = num_jobs
    for i in range(1, num_pms+1):
        pm = PhysicalMachine(i, num_slots=num_slots)
        pm_set[i] = pm

    # Generate electricity price
    ele_price = [0.0]*num_slots
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


def random_line(f, size):
    offset = random.randrange(size)
    f.seek(offset)
    f.readline()
    line = f.readline()
    if len(line) == 0:
        f.seek(0)
        line = f.readline()
    return line
