import math

from machine import Job, PhysicalMachine


class OfflineSolver:

    def __init__(self):
        self.active_pm_id = set()

    def solve_offline_alg(self, job_set, pm_set, ele_price):
        """
        Offline algorithm Electric-Partition.
        :param job_set: VMs
        :param pm_set: PMs
        :param ele_price: electricity price
        :return: cost
        :type job_set: dict[int, Job]
        :type pm_set: dict[int, PhysicalMachine]
        :type ele_price: list[float]
        :rtype: float
        """

        # Partition the jobs(VMs) into two sets
        large_set = set()
        small_set = set()
        gamma = 0.25  # constant for partitioning
        for job_id in job_set:
            job = job_set[job_id]
            if job.demand > gamma:
                large_set.add(job)
            else:
                small_set.add(job)

        #print "Number of jobs in the large set: %d." % len(large_set)
        #print "Number of jobs in the small set: %d." % len(small_set)

        # For each VM in the large set, select from the activated physical machines
        # to allocate the VM to the first physical machine of which the active time
        # does not conflict with the interval of this VM. If there exists no such an
        # activated physical machine, activate one new physical machine to allocate the VM.
        #sorted_large_set = sorted(large_set, key=lambda x: x.demand, reverse=True)
        for job in large_set:
            self.schedule_job(job, pm_set)

        # Compute the electricity cost for each VM in the small set.
        for job in small_set:
            self.compute_electricity_cost(job, ele_price)

        # Sort these VMs so that their electricity cost decreases as the index increases.
        sorted_small_set = sorted(small_set, key=lambda x: x.e_price, reverse=True)

        # For each VM in the small set in the order of increasing index, select from the
        # activated physical machines to allocate the VM to the first physical machine of
        # which the resource capacity on each time in the interval of the VM is not exceeded
        for job in sorted_small_set:
            self.schedule_job(job, pm_set)

        # Evaluate
        ret = self.evaluate(pm_set, ele_price)  # the average total cost
        #ret = self.evaluate_pm_number(pm_set)   # the average number of active PMs

        return ret

    def solve_offline_demand_first(self, job_set, pm_set, ele_price):
        """
        Offline algorithm Demand-First.
        :param job_set: VMs
        :param pm_set: PMs
        :param ele_price: electricity price
        :return: cost
        :type job_set: dict[int, Job]
        :type pm_set: dict[int, PhysicalMachine]
        :type ele_price: list[float]
        :rtype: float
        """
        sorted_job_set = sorted(job_set.values(), key=lambda x: x.demand, reverse=True)

        for job in sorted_job_set:
            self.schedule_job(job, pm_set)

    def solve_offline_length_first(self, job_set, pm_set, ele_price):
        """
        Offline algorithm Length-First.
        :param job_set: VMs
        :param pm_set: PMs
        :param ele_price: electricity price
        :return: cost
        :type job_set: dict[int, Job]
        :type pm_set: dict[int, PhysicalMachine]
        :type ele_price: list[float]
        :rtype: float
        """
        sorted_job_set = sorted(job_set.values(), key=lambda x: x.end_time-x.start_time+1, reverse=True)

        for job in sorted_job_set:
            self.schedule_job(job, pm_set)

    def solve_offline_first_fit(self, job_set, pm_set, ele_price):

        for job_id in job_set:
            self.schedule_job(job_set[job_id], pm_set)

    def solve_offline_price_first(self, job_set, pm_set, ele_price):

        for job_id in job_set:
            self.compute_electricity_cost(job_set[job_id], ele_price)

        sorted_job_set = sorted(job_set.values(), key=lambda x: x.e_price, reverse=True)

        for job in sorted_job_set:
            self.schedule_job(job, pm_set)

    def solve_offline_opt_lb(self, job_set, pm_set, ele_price):
        """
        Offline algorithm lower bound opt.
        :param job_set: VMs
        :param pm_set: PMs
        :param ele_price: electricity price
        :return: cost
        :type job_set: dict[int, Job]
        :type pm_set: dict[int, PhysicalMachine]
        :type ele_price: list[float]
        :rtype: float
        """
        pm = pm_set[1]
        pm.status = True
        for job_id in job_set:
            job = job_set[job_id]
            for t in range(job.start_time, job.end_time+1):
                pm.utilization[t] += job.demand

    def reset(self, pm_set):
        """
        Reset all the PMs
        :param pm_set: PMs
        :return: None
        :type pm_set: dict[int, PhysicalMachine]
        """
        for pm_id in pm_set:
            pm = pm_set[pm_id]
            pm.status = False
            for i in range(0, len(pm.utilization)):
                pm.utilization[i] = 0.0
            pm.running_jobs = set()
        self.active_pm_id = set()

    def schedule_large_job(self, job, pm_set):
        """
        Schedule a job belongs to the large set.
        :param job: VM
        :param pm_set: PMs
        :return: None
        :type job: Job
        :type pm_set: dict[int, PhysicalMachine]
        """
        n = len(pm_set)
        for pm_id in range(1, n+1):
            pm = pm_set[pm_id]
            if not self.__intersected(job, pm):
                pm.running_jobs.add(job)
                pm.status = True
                self.__update_utilization(job, pm)
                pm.power_off_time = max(pm.power_off_time, job.end_time)
                return

    def __intersected(self, job, pm):
        """
        Determine if the interval of a VM conflicts with the active time of a PM.
        :param job: VM
        :param pm: PM
        :return: whether the interval of a VM conflicts with the active time of a PM
        :type job: Job
        :type pm: PhysicalMachine
        :rtype: bool
        """
        for t in range(job.start_time, job.end_time+1):
            if pm.utilization[t] > 0.0:
                return True
        return False

    def schedule_job(self, job, pm_set):
        """
        Schedule a job on a PM.
        :param job: VM
        :param pm_set: PMs
        :return: None
        :type job: Job
        :type pm_set: dict[int, PhysicalMachine]
        """
        n = len(pm_set)
        for pm_id in range(1, n+1):
            pm = pm_set[pm_id]
            if self.__can_schedule(job, pm):
                pm.running_jobs.add(job)
                pm.status = True
                self.__update_utilization(job, pm)
                pm.power_on_time = min(pm.power_on_time, job.start_time)
                pm.power_off_time = max(pm.power_off_time, job.end_time)
                self.active_pm_id.add(pm.id)
                return

    def __update_utilization(self, job, pm):
        """
        Update the utilization of a physical machine incurred by the new coming job.
        :param job: VM
        :param pm: PM
        :return: None
        :type job: Job
        :type pm: PhysicalMachine
        """
        for t in range(job.start_time, job.end_time+1):
            pm.utilization[t] += job.demand

    def __can_schedule(self, job, pm):
        """
        Check the capacity constraint of a pm, if a job is scheduled on it.
        :param job: VM
        :param pm: PM
        :return: whether we can schedule the job on the pm or not
        :type job: Job
        :type pm: PhysicalMachine
        :rtype: bool
        """
        for t in range(job.start_time, job.end_time+1):
            if pm.utilization[t] + job.demand > pm.capacity:
                return False
        return True

    def compute_electricity_cost(self, job, ele_price):
        """
        Compute the electricity cost C(J_i) = \sum_{t in [s_i, e_i)} c(t)
        :param job: VM
        :param ele_price: electricity price
        :return: None
        :type job: Job
        :type ele_price: list[float]
        """
        price = 0.0
        for t in range(job.start_time, job.end_time + 1):
            price += ele_price[t]
        job.e_price = price

    def evaluate(self, pm_set, ele_price):
        """
        Evaluate the cost of the solution.
        :param pm_set: PMs
        :param ele_price: electricity price
        :return: electricity cost
        :type pm_set: dict[int, PhysicalMachine]
        :type ele_price: list[float]
        :rtype: float
        """
        e_i = 0.1  # idle power incurred by keeping the physical machine active, unit: KW
        e_p = 0.2  # peak power of the physical machine with full utilization, unit: KW

        cost = 0.0

        for pm_id in pm_set:
            pm = pm_set[pm_id]
            if pm.status is False:
                continue
            # compute the electricity price of a PM
            for t in range(0, pm.power_off_time+1):
                if pm.utilization[t] > 0.0:
                    power_consumption = e_i + (e_p - e_i) * pm.utilization[t]
                    cost += (power_consumption * ele_price[t])

        return cost

    def evaluate_pm_number(self):

        return len(self.active_pm_id)

