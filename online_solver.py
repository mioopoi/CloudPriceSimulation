import math
import sys

from machine import Job, PhysicalMachine


class Group:

    def __init__(self, min_length, max_length, jobs=None):
        """
        :param min_length:
        :param max_length:
        :param jobs:
        :type min_length: int
        :type max_length: int
        :type jobs: list[Job]
        :return: None
        """
        self.min_length = min_length
        self.max_length = max_length
        if jobs is None:
            self.jobs = list()
        else:
            self.jobs = jobs


class OnlineSolver:

    def __init__(self, num_pms, len_slots, ele_price, groups=None):
        """
        :param num_pms: number of PMs
        :param len_slots: T
        :param ele_price: electricity price
        :return: cost
        :type num_pms: int
        :type len_slots: int
        :type ele_price: list[float]
        :type groups: dict[int, Group]
        """

        self.num_pms = num_pms
        self.job_set = {}
        """:type : dict[int, Job]"""

        self.ele_price = ele_price
        if groups is None:
            self.groups = {}
        else:
            self.groups = groups

        self.refined_groups = {}

        self.cur_pm_id = 1
        self.active_pm_id = set()

        from generate_input import L_MIN, L_MAX  # Notice: Must import after calling the function gen_data()!

        self.l_min = L_MIN
        self.l_max = L_MAX

        # Create PMs
        self.pm_set = {}
        for i in range(self.num_pms):
            pm_id = i + 1
            pm = PhysicalMachine(pm_id, num_slots=len_slots)
            self.pm_set[pm_id] = pm

        # Create refined PMs (for virtual allocation)
        self.refined_pm_set = {}
        for i in range(self.num_pms):
            pm_id = i + 1
            refined_pm = PhysicalMachine(pm_id, num_slots=len_slots)
            self.refined_pm_set[pm_id] = refined_pm

    def __init_groups(self):
        # Init the group set
        self.groups = {}
        self.refined_groups = {}
        # Notice: DO NOT use math.log(x), the default base is e = 2.718...!
        k_max = int(math.ceil(math.log(float(self.l_max) / float(self.l_min), 2)))
        min_length = self.l_min
        max_length = min_length * 2 - 1
        for k in range(k_max):
            self.groups[k] = Group(min_length, max_length)
            min_length = max_length + 1
            max_length = min_length * 2 - 1

    def partition_round(self):
        """
        Online algorithm Partition-Round.
        :rtype: float
        """

        self.__init_groups()

        # We first partition the VMs according to the lengths of their execution time intervals.
        # If length of J_i is among [L_MIN * 2^k, L_MIN * 2^(k+1)], then J_i is grouped into set G_k where
        # 0 <= k <= ceil(log(L_MAX / L_MIN)) - 1
        for i in self.job_set:
            job = self.job_set[i]
            length = job.end_time - job.start_time + 1
            sign = False
            for k in self.groups:
                group = self.groups[k]
                if group.min_length <= length <= group.max_length:
                    job.group_id = k
                    group.jobs.append(job)
                    sign = True
                    break
            if not sign:
                print "Error: cannot put a job into some group"
                print i
                print "length: %d, L_MIN: %d, L_MAX: %d" % (length, self.l_min, self.l_max)
                sys.exit(-1)

        # For each VM J_i, if it belongs to set G_k, then we construct a corresponding refined instance
        # J'_i which has a length L_MIN * 2^k of execution time interval. Moreover, its starting time is set to be
        # s'_i = arg min_{t in [s_i, e_i - L_MIN * 2^k]} sum_{t <= t' <= t+L_MIN*2^k} c(t') and its ending time is
        # set to be e'_i = s'_i + L_MIN*2^k
        # Correspondingly, let G'_k be the refined VMs that are constructed from VMs in G_k
        for k in self.groups:
            group = self.groups[k]
            for job in group.jobs:
                self.__make_refined_job(job, k)

        # Now all the refined VMs in the same set G'_k have the same length L_MIN*2^k.
        # We apply NextFit to each set G'_k to get a virtual allocation for each refined VM J'_i in G'_k
        for k in self.refined_groups:
            refined_group = self.refined_groups[k]
            # print "len refined_group: %d" % (len(refined_group.jobs))
            self.__next_fit(refined_group)

        #self.reset()

        # Finally, by keeping the allocation for J_i same as that of J'_i in the virtual allocation, we obtain
        # the desired final allocation.
        for k in self.groups:
            group = self.groups[k]
            self.__real_fit(group)

    def __make_refined_job(self, job, k):
        """
        :param job: VM
        :param k: id of original group
        :return: refined VM
        :type job: Job
        :type k: int
        :rtype: Job
        """
        length = self.l_min * 2**k
        start_time = job.start_time
        min_price = float('inf')
        for t in range(job.start_time, job.end_time - length + 2):
            l, r = t, t + length - 1
            tmp_price = 0.0
            for t_dash in range(l, r + 1):
                tmp_price += self.ele_price[t_dash]
            if tmp_price < min_price:
                min_price = tmp_price
                start_time = t
        end_time = start_time + length - 1

        refined_job = Job(job.id, start_time, end_time, job.demand, min_price)
        if k in self.refined_groups:
            self.refined_groups[k].jobs.append(refined_job)
        else:
            new_refined_group = Group(0, 0)
            new_refined_group.jobs.append(refined_job)
            self.refined_groups[k] = new_refined_group

    def __next_fit(self, refined_group):
        """
        :param refined_group: G'_k
        :return: None
        :type refined_group: Group
        """
        for refined_job in refined_group.jobs:
            if self.can_schedule(refined_job, self.cur_pm_id, self.refined_pm_set):
                self.schedule(refined_job, self.cur_pm_id, self.refined_pm_set)
            else:
                self.cur_pm_id += 1
                self.schedule(refined_job, self.cur_pm_id, self.refined_pm_set)
            # set the schedule of real job same as that of the virtual job
            self.job_set[refined_job.id].scheduled_pm_id = self.cur_pm_id

    @staticmethod
    def can_schedule(job, pm_id, pm_set):
        pm = pm_set[pm_id]
        for t in range(job.start_time, job.end_time + 1):
            if pm.utilization[t] + job.demand > pm.capacity:
                return False
        return True

    @staticmethod
    def schedule(job, pm_id, pm_set):
        """
        :param job: VM
        :param pm_id:
        :param pm_set
        :return:
        :type job: Job
        :type pm_id: int
        :type pm_set: dict[int, PhysicalMachine]
        :rtype: bool
        """
        pm = pm_set[pm_id]
        for t in range(job.start_time, job.end_time + 1):
            pm.utilization[t] += job.demand

    def reset(self):
        for i in self.pm_set:
            pm = self.pm_set[i]
            for t in range(len(pm.utilization)):
                pm.utilization[t] = 0.0
        self.cur_pm_id = 1

    def __real_fit(self, group):
        """
        :param group: G_k
        :return: None
        :type group: Group
        """
        for job in group.jobs:
            # print "original pm id: %d" % (job.scheduled_pm_id),
            # if not write like the following, it may cause an error
            while not self.can_schedule(job, job.scheduled_pm_id, self.pm_set):
                job.scheduled_pm_id += 1
            self.schedule(job, job.scheduled_pm_id, self.pm_set)
            self.active_pm_id.add(job.scheduled_pm_id)  # update the active pm set
            # print "can! new pm id: %d" % (job.scheduled_pm_id)
            '''
            if self.__can_schedule(job, job.scheduled_pm_id):
                print "can!"
                self.__schedule(job, job.scheduled_pm_id)
            else:
                print "Error: cannot schedule the job on planned PM."
                sys.exit(-2)
            '''

    def evaluate_ele_cost(self):
        return self.evaluate_cost(self.active_pm_id, self.pm_set, self.ele_price)

    def evaluate_pms_num(self):
        return self.evaluate_pm_num(self.active_pm_id)

    @staticmethod
    def evaluate_cost(active_pm_id, pm_set, ele_price):
        """
        :param active_pm_id:
        :param pm_set:
        :param ele_price:
        :return: cost
        :type active_pm_id: set[int]
        :type pm_set: dict[int, PhysicalMachine]
        :type ele_price: list[float]
        :rtype: float
        """
        e_i = 0.1
        e_p = 0.2
        cost = 0.0
        for i in active_pm_id:
            pm = pm_set[i]
            for t in range(0, len(pm.utilization)):
                if pm.utilization[t] > 0.0:
                    power_consumption = e_i + (e_p - e_i) * pm.utilization[t]
                    cost += (power_consumption * ele_price[t])
        return cost

    @staticmethod
    def evaluate_pm_num(active_pm_id):
        """
        :param active_pm_id:
        :type active_pm_id: set[int]
        :return: number of active PM
        :rtype: int
        """
        return len(active_pm_id)


class OnlineDemandFirst:

    def __init__(self, num_pms, len_slots, ele_price):
        """
        :param num_pms: num of PMs
        :param len_slots: length of the simulation time
        :param ele_price: electricity price
        :return: cost
        :type num_pms: int
        :type len_slots: int
        :type ele_price: list[float]
        """
        self.num_pms = num_pms
        self.job_set = {}
        self.ele_price = ele_price

        self.cur_pm_id = 1
        self.active_pm_id = set()

        # Create PMs
        self.pm_set = {}
        for i in range(num_pms):
            pm_id = i + 1
            pm = PhysicalMachine(pm_id, num_slots=len_slots)
            self.pm_set[pm_id] = pm

    def demand_first(self):
        sorted_job_set = sorted(self.job_set.values(), key=lambda x: x.demand, reverse=True)
        for job in sorted_job_set:
            while not OnlineSolver.can_schedule(job, self.cur_pm_id, self.pm_set):
                self.cur_pm_id += 1
            OnlineSolver.schedule(job, self.cur_pm_id, self.pm_set)
            self.active_pm_id.add(self.cur_pm_id)

    def evaluate_ele_cost(self):
        return OnlineSolver.evaluate_cost(self.active_pm_id, self.pm_set, self.ele_price)

    def evaluate_pms_num(self):
        return OnlineSolver.evaluate_pm_num(self.active_pm_id)
