

class Job:
    """
    This class is the abstraction of the Virtual Machine.
    """
    def __init__(self, identifier, start_time, end_time, demand, e_price=0.0):
        """
        Initialize a job (virtual machine).

        :param identifier: id of a job
        :param start_time:  starting time
        :param end_time:  ending time
        :param demand: resource demand
        :param e_price: electricity price
        :return: None
        :type identifier: int
        :type start_time: int
        :type end_time: int
        :type demand: float
        :type e_price: float
        """
        self.id = identifier
        self.start_time = start_time
        self.end_time = end_time
        self.demand = demand
        self.e_price = e_price

    def __str__(self):
        return "Job:\n- id: {}\n- start time: {}\n- end time: {}\n- demand: {}"\
            .format(self.id, self.start_time, self.end_time, self.demand)


class PhysicalMachine:
    """
    This class is the abstraction of the Physical Machine.
    """
    def __init__(self, identifier, capacity=1.0, status=False, utilization=None, running_jobs=None,
                 power_on_time=0, power_off_time=0, num_slots=1000):
        """
        Initialize a physical machine.

        :param identifier: id of a PM
        :param capacity: resource capacity of a PM
        :param status: whether a PM is active or not
        :param utilization: the resource utilization of a PM
        :param running_jobs: running jobs on a PM
        :return: None
        :type identifier: int
        :type capacity: float
        :type status: bool
        :type utilization: list[float]
        :type running_jobs: set[Job]
        :type power_on_time: int
        :type power_off_time: int
        :type num_slots: int
        """
        self.id = identifier
        self.capacity = capacity
        self.status = status
        if utilization is None:
            self.utilization = [0.0]*num_slots
        else:
            self.utilization = utilization
        if running_jobs is None:
            self.running_jobs = set()
        else:
            self.running_jobs = running_jobs
        self.power_on_time = power_on_time
        self.power_off_time = power_off_time

    def __str__(self):
        return "PM:\n- id: {}\n- capacity: {}\n- status: {}\n- utilization: {}"\
            .format(self.id, self.capacity, self.status, self.utilization)
