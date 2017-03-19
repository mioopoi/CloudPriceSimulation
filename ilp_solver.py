from gurobipy import *

from machine import Job, PhysicalMachine


class ILPSolver:

    def __init__(self, job_set, pm_set, ele_price):
        self.job_set = job_set
        self.pm_set = pm_set
        self.ele_price = ele_price
        self.x = {}  # Plant job decision variables: x[i,j] == 1 if VM(i) is scheduled on PM(j)
        self.u = {}
        self.y = {}
        self.ei = 0.1
        self.ep = 0.2

    def solve_offline_ILP(self):
        """
        Solve offline problem using ILP.
        :return: total electricity cost
        :rtype: float
        """

        n = len(self.job_set)
        m = len(self.pm_set)
        T = len(self.ele_price)

        # Model
        model = Model("cloudPowerPriceILP")

        # Add variables
        for i in range(n):
            for j in range(m):
                self.x[(i,j)] = model.addVar(vtype=GRB.CONTINUOUS, name="x%d,%d" % (i,j))  # linear relaxation
        model.update()

        for j in range(m):
            for t in range(T):
                self.u[(t,j)] = model.addVar(lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS)
                self.y[(t,j)] = model.addVar(vtype=GRB.CONTINUOUS)  # linear relaxation
        model.update()

        # Add constraints
        for j in range(m):
            for t in range(T):
                model.addConstr(self.u[t,j] == self.compute_u(t,j))
                model.addConstr(self.u[t,j] <= self.y[t,j])
                #model.addConstr(self.y[t,j] == self.compute_y(t,j))  # Wrong expression!!!

        for i in range(n):
            model.addConstr(quicksum(self.x[i,j] for j in range(m)) == 1)

        # Set objective
        model.setObjective(
            quicksum(
                quicksum(
                    (self.ei * self.y[t,j] + (self.ep - self.ei) * self.u[t,j]) * self.ele_price[t]
                    for t in range(T)
                )
                for j in range(m)
            ),
            GRB.MINIMIZE
        )

        model.optimize()

        #for i in range(n):
        #    for j in range(m):
        #        print("x(%d,%d): %s" % (i, j, self.x[i,j]))
        #for j in range(m):
        #    for t in range(T):
        #        print("u(%d, %d): %s  y(%d,%d): %s" % (t,j,self.u[t,j], t, j, self.y[t,j]))

        return model.objVal

    def compute_u(self, t, j):
        """
        :param t: slot id
        :param j: VM id
        :return: u[t,j]
        """
        ret = 0.0
        for i in self.job_set:
            if t >= self.job_set[i].start_time and t <= self.job_set[i].end_time:
                ret += self.job_set[i].demand * self.x[i-1,j]
        #print "u[%d,%d]: %s" % (t, j, ret)
        return ret

    def compute_y(self, t, j):
        if self.u[t,j] > 0:
            return 1
        else:
            return 0

    def evaluate_pms_num(self):
        """
        :rtype: float
        """
        num = 0.0
        for i in self.job_set:
            num += self.job_set[i].demand
        return num
