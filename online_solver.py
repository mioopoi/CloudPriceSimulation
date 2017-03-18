import math

from machine import Job, PhysicalMachine
from generate_input import L_MIN, L_MAX


class Group:
    def __init__(self, min_length, max_length):
        """
        :param min_length:
        :param max_length:
        :type min_length: int
        :type max_length: int
        :return: None
        """
        self.min_length = min_length
        self.max_length = max_length


class OnlineSolver:

    def __init__(self, job_set, pm_set, ele_price):
        """
        :param job_set: VMs
        :param pm_set: PMs
        :param ele_price: electricity price
        :return: cost
        :type job_set: dict[int, Job]
        :type pm_set: dict[int, PhysicalMachine]
        :type ele_price: list[float]
        """
        self.job_set = job_set
        self.pm_set = pm_set
        self.ele_price = ele_price
        self.group = {}

        # Init the group set
        k_max = int(math.ceil(math.log(float(L_MAX) / float(L_MIN))))
        min_length = L_MIN
        max_length = min_length * 2 - 1
        for k in range(k_max):
            self.group[k] = Group(min_length, max_length)
            min_length = max_length + 1
            max_length = min_length * 2 - 1


    def solve_online_alg(self):
        """
        Online algorithm Partition-Round.
        :rtype: float
        """
        # We first partition the VMs according to the lengths of their execution time intervals.
        # If length of J_i is among [L_MIN * 2^k, L_MIN * 2^(k+1)], then J_i is grouped into set G_k where
        # 0 <= k <= ceil(log(L_MAX / L_MIN)) - 1

