
from generate_input import *
from solver import *
from ilp_solver import *


num_points = 7
#num_points = 14
num_algorithms = 3
step = 100

results_cost = [[0.0 for col in range(num_algorithms)] for row in range(num_points)]
results_num = [[0.0 for c in range(num_algorithms)] for r in range(num_points)]

for point_id in range(0, num_points):
    num_jobs = (point_id+1) * step
    num_slots = 300
    rounds = 50
    '''total_cost_df, total_cost_lf, total_cost_pf, total_cost_alg, total_cost_opt, total_cost_opt_lb = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0'''
    total_cost_df, total_cost_alg, total_cost_opt_lb = 0.0, 0.0, 0.0
    total_num_df, total_num_alg, total_num_opt_lb = 0, 0, 0

    for round_id in range(0, rounds):
        [job_set, pm_set, ele_price] = gen_data(num_jobs, num_slots)

        solver = OfflineSolver()

        solver.solve_offline_demand_first(job_set, pm_set, ele_price)
        cost_df = solver.evaluate(pm_set, ele_price)
        num_df = solver.evaluate_pm_number()
        solver.reset(pm_set)

        '''cost_lf = solver.solve_offline_length_first(job_set, pm_set, ele_price)
        solver.reset(pm_set)

        cost_pf = solver.solve_offline_price_first(job_set, pm_set, ele_price)
        solver.reset(pm_set)'''

        solver.solve_offline_alg(job_set, pm_set, ele_price)
        cost_alg = solver.evaluate(pm_set, ele_price)
        num_alg = solver.evaluate_pm_number()
        solver.reset(pm_set)

        ilp_solver = ILPSolver(job_set, pm_set, ele_price)
        num_opt_lb = ilp_solver.evaluate_pms_num()
        cost_opt_lb = ilp_solver.solve_offline_ILP()

        '''cost_opt_lb = solver.solve_offline_opt_lb(job_set, pm_set, ele_price)
        solver.reset(pm_set)'''

        total_cost_df += cost_df
        total_cost_alg += cost_alg
        total_cost_opt_lb += cost_opt_lb
        '''total_cost_lf += cost_lf
        total_cost_pf += cost_pf
        total_cost_opt += cost_opt'''

        total_num_df += num_df
        total_num_alg += num_alg
        total_num_opt_lb += num_opt_lb

    ave_cost_df = total_cost_df / rounds
    '''ave_cost_lf = total_cost_lf / rounds
    ave_cost_pf = total_cost_pf / rounds'''
    ave_cost_alg = total_cost_alg / rounds
    '''ave_cost_opt = total_cost_opt / rounds'''
    ave_cost_opt_lb = total_cost_opt_lb / rounds

    ave_num_df = total_num_df / rounds
    ave_num_alg = total_num_alg / rounds
    ave_num_opt_lb = total_num_opt_lb / rounds

    results_cost[point_id][0] = ave_cost_df
    results_cost[point_id][1] = ave_cost_alg
    results_cost[point_id][2] = ave_cost_opt_lb

    results_num[point_id][0] = ave_num_df
    results_num[point_id][1] = ave_num_alg
    results_num[point_id][2] = ave_num_opt_lb

    '''print ave_cost_df, ave_cost_lf, ave_cost_alg, ave_cost_opt, ave_cost_opt_lb'''
    print ave_cost_df, ave_cost_alg, ave_cost_opt_lb
    print ave_num_df, ave_num_alg, ave_num_opt_lb

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