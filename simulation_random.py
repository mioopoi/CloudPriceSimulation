from container import PriorityQueue

from generate_input import *
from ilp_solver import ILPSolver
from online_solver import OnlineSolver, OnlineDemandFirst
from offline_solver import OfflineSolver

import copy

random.seed(0)

num_points = 7
num_algorithms = 5  # if there is no offline algorithms, set it to be 3
step = 100

results_cost = [[0.0 for col in range(num_algorithms)] for row in range(num_points)]
results_num = [[0.0 for c in range(num_algorithms)] for r in range(num_points)]

for point_id in range(0, num_points):
    num_jobs = (point_id+1) * step
    num_slots = 300
    rounds = 10

    total_cost_df_online, total_cost_alg_online, total_cost_opt = 0.0, 0.0, 0.0
    total_num_df_online, total_num_alg_online, total_num_opt = 0.0, 0.0, 0.0
    #total_cost_df_online, total_cost_alg_online = 0.0, 0.0
    #total_num_df_online, total_num_alg_online = 0.0, 0.0

    total_cost_df_offline, total_cost_alg_offline = 0.0, 0.0
    total_num_df_offline, total_num_alg_offline = 0.0, 0.0

    for round_id in range(0, rounds):

        # Generate the input
        [job_set, pm_set, ele_price] = gen_data(num_jobs, num_slots)    # random input

        # Put all the jobs into a priority queue with start time of the job as the priority
        pq = PriorityQueue()
        for i in job_set:
            job = job_set[i]
            pq.put(job, job.start_time)

        # Init the online algorithms
        num_pms = len(job_set)
        online_alg = OnlineSolver(num_pms, num_slots, ele_price)
        online_df = OnlineDemandFirst(num_pms, num_slots, ele_price)
        opt_lb = ILPSolver(job_set, pm_set, ele_price)

        # Init the offline algorithms and run
        solver = OfflineSolver()
        solver.solve_offline_demand_first(copy.deepcopy(job_set), pm_set, ele_price)
        cost_df_offline = solver.evaluate(pm_set, ele_price)
        num_df_offline = solver.evaluate_pm_number()
        solver.reset(pm_set)

        solver.solve_offline_alg(copy.deepcopy(job_set), pm_set, ele_price)
        cost_alg_offline = solver.evaluate(pm_set, ele_price)
        num_alg_offline = solver.evaluate_pm_number()
        solver.reset(pm_set)

        # Simulate the running of time
        for t in range(0, num_slots):
            # Catch all the jobs arrive at time t
            cur_job_set = {}
            while not pq.empty():
                job = pq.get()
                if job.start_time == t:
                    cur_job_set[job.id] = job
                else:
                    pq.put(job, job.start_time)
                    break

            if len(cur_job_set) == 0:
                continue

            # Push the cur_job_set to the online algorithm engine
            online_alg.job_set = copy.deepcopy(cur_job_set)
            online_df.job_set = copy.deepcopy(cur_job_set)  # 2017.09.17 using deepcopy?

            # Run the online algorithms to schedule the cur_job_set
            online_df.demand_first()
            online_alg.partition_round()

        # Evaluate cost and number of active PMs
        cost_alg = online_alg.evaluate_ele_cost()
        cost_df = online_df.evaluate_ele_cost()
        #cost_opt = opt_lb.solve_offline_ILP()
        cost_opt = 0
        num_alg = online_alg.evaluate_pms_num()
        num_df = online_df.evaluate_pms_num()
        num_opt = opt_lb.evaluate_pms_num()

        # Add to total value
        total_cost_df_online += cost_df
        total_cost_alg_online += cost_alg
        total_cost_opt += cost_opt
        total_num_df_online += num_df
        total_num_alg_online += num_alg
        total_num_opt += num_opt

        total_cost_df_offline += cost_df_offline
        total_cost_alg_offline += cost_alg_offline
        total_num_df_offline += num_df_offline
        total_num_alg_offline += num_alg_offline

    ave_cost_df = total_cost_df_online / rounds
    ave_cost_alg = total_cost_alg_online / rounds
    ave_cost_opt = total_cost_opt / rounds
    ave_num_df = total_num_df_online / rounds
    ave_num_alg = total_num_alg_online / rounds
    ave_num_opt = total_num_opt / rounds

    ave_cost_df_offline = total_cost_df_offline / rounds
    ave_cost_alg_offline = total_cost_alg_offline / rounds
    ave_num_df_offline = total_num_df_offline / rounds
    ave_num_alg_offline = total_num_alg_offline / rounds

    results_cost[point_id][0] = ave_cost_df
    results_cost[point_id][1] = ave_cost_alg
    results_cost[point_id][2] = ave_cost_opt
    results_cost[point_id][3] = ave_cost_df_offline
    results_cost[point_id][4] = ave_cost_alg_offline

    results_num[point_id][0] = ave_num_df
    results_num[point_id][1] = ave_num_alg
    results_num[point_id][2] = ave_num_opt
    results_num[point_id][3] = ave_num_df_offline
    results_num[point_id][4] = ave_num_alg_offline

    print ave_cost_df, ave_cost_alg, ave_cost_opt
    print ave_num_df, ave_num_alg, ave_num_opt
    #print ave_cost_df, ave_cost_alg
    #print ave_num_df, ave_num_alg


# Print the result matrix
print
for i in range(num_points):
    for j in range(num_algorithms):
        print results_cost[i][j],
    print
print
for i in range(num_points):
    for j in range(num_algorithms):
        print results_num[i][j],
    print
