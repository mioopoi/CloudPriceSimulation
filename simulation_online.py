from container import PriorityQueue

from generate_input import *
from ilp_solver import ILPSolver
from online_solver import OnlineSolver, OnlineDemandFirst

#num_points = 7
num_points = 14
#num_algorithms = 3
num_algorithms = 2
#step = 100
step = 5000

results_cost = [[0.0 for col in range(num_algorithms)] for row in range(num_points)]
results_num = [[0.0 for c in range(num_algorithms)] for r in range(num_points)]

for point_id in range(0, num_points):
    num_jobs = (point_id+1) * step
    #num_slots = 300
    num_slots = 1000
    rounds = 1

    #total_cost_df_online, total_cost_alg_online, total_cost_opt = 0.0, 0.0, 0.0
    #total_num_df_online, total_num_alg_online, total_num_opt = 0.0, 0.0, 0.0
    total_cost_df_online, total_cost_alg_online = 0.0, 0.0
    total_num_df_online, total_num_alg_online = 0.0, 0.0

    for round_id in range(0, rounds):

        # Generate the input
        #[job_set, pm_set, ele_price] = gen_data(num_jobs, num_slots)
        [job_set, pm_set, ele_price] = load_data(num_jobs, num_slots)

        # Put all the jobs into a priority queue with start time of the job as the priority
        pq = PriorityQueue()
        for i in job_set:
            job = job_set[i]
            pq.put(job, job.start_time)

        # Init the online algorithms
        num_pms = len(job_set)
        online_alg = OnlineSolver(num_pms, num_slots, ele_price)
        online_df = OnlineDemandFirst(num_pms, num_slots, ele_price)
        #opt_lb = ILPSolver(job_set, pm_set, ele_price)

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
            online_alg.job_set = cur_job_set
            online_df.job_set = cur_job_set

            # Run the online algorithms to schedule the cur_job_set
            online_df.demand_first()
            online_alg.partition_round()

        # Evaluate cost and number of active PMs
        cost_alg = online_alg.evaluate_ele_cost()
        cost_df = online_df.evaluate_ele_cost()
        #cost_opt = opt_lb.solve_offline_ILP()
        num_alg = online_alg.evaluate_pms_num()
        num_df = online_df.evaluate_pms_num()
        #num_opt = opt_lb.evaluate_pms_num()

        # Add to total value
        total_cost_df_online += cost_df
        total_cost_alg_online += cost_alg
        #total_cost_opt += cost_opt
        total_num_df_online += num_df
        total_num_alg_online += num_alg
        #total_num_opt += num_opt

    ave_cost_df = total_cost_df_online / rounds
    ave_cost_alg = total_cost_alg_online / rounds
    #ave_cost_opt = total_cost_opt / rounds
    ave_num_df = total_num_df_online / rounds
    ave_num_alg = total_num_alg_online / rounds
    #ave_num_opt = total_num_opt / rounds

    results_cost[point_id][0] = ave_cost_df
    results_cost[point_id][1] = ave_cost_alg
    #results_cost[point_id][2] = ave_cost_opt
    results_num[point_id][0] = ave_num_df
    results_num[point_id][1] = ave_num_alg
    #results_num[point_id][2] = ave_num_opt

    #print ave_cost_df, ave_cost_alg, ave_cost_opt
    #print ave_num_df, ave_num_alg, ave_num_opt
    print ave_cost_df, ave_cost_alg
    print ave_num_df, ave_num_alg


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
