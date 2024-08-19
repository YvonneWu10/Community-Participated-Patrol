import gurobipy as grb
import numpy as np
import json
import time
import os


def maxDefUnility(t_num, rp, rv, ep, ev, Rd, Pd, Ra, Pa, time_limit):
    time0 = time.time()

    # need to replace it with your own license
    # os.environ["GRB_LICENSE_FILE"] = "/home/yfwu/gurobi.lic"

    utility = np.array([-100.0 for i in range(t_num)])
    strategy = np.zeros((t_num, 2 * t_num))
    coverage = np.zeros((t_num, t_num))
    M = 1000

    # enumerate every target as the target to be attacked
    for t in range(t_num):
        model = grb.Model()

        # claim the variables
        p = model.addVars(t_num, vtype=grb.GRB.CONTINUOUS, name="p", lb=0, ub=rp)
        v = model.addVars(t_num, vtype=grb.GRB.INTEGER, name="v", lb=0, ub=rv)
        c = model.addVars(t_num, vtype=grb.GRB.CONTINUOUS, name="c", lb=0, ub=1)

        delta = model.addVars(t_num, vtype=grb.GRB.CONTINUOUS, name="delta", lb=0, ub=float("inf"))
        w = model.addVars(t_num, vtype=grb.GRB.BINARY, name="w", lb=0, ub=1)

        Ua = model.addVars(t_num, vtype=grb.GRB.CONTINUOUS, name="Ua", lb=-float("inf"), ub=float("inf"))
        Ud = model.addVars(t_num, vtype=grb.GRB.CONTINUOUS, name="Ud", lb=-float("inf"), ub=float("inf"))

        # add constraints
        model.addConstrs((Ua[i] == (1 - c[i]) * Ra[i] + c[i] * Pa[i] for i in range(t_num)), name="definition of Ua")
        model.addConstrs((Ud[i] == c[i] * Rd[i] + (1 - c[i]) * Pd[i] for i in range(t_num)), name="definition of Ud")

        model.addConstrs((Ua[t] >= Ua[i] for i in range(t_num)), name=f"attacker make best response")

        model.addConstr(grb.quicksum(p[i] for i in range(t_num)) <= rp, name="constraint of patrollers' resources")
        model.addConstr(grb.quicksum(v[i] for i in range(t_num)) <= rv, name="constraint of villagers' resources")

        model.addConstrs((ep*p[i] + ev*v[i] == c[i] + delta[i] for i in range(t_num)), name="effectiveness constraint")
        model.addConstrs((w[i] <= c[i] for i in range(t_num)))
        model.addConstrs((delta[i] <= M * w[i]  for i in range(t_num)))

        # maximize defender's utility
        model.setObjective(Ud[t], sense=grb.GRB.MAXIMIZE)

        model.setParam("outPutFlag", 0)
        model.setParam("DualReductions", 0)
        model.setParam("MIPGap", 1e-6)

        # limit the time
        time1 = time.time()
        if time1 - time0 >= time_limit:
            break
        model.setParam("TimeLimit", time_limit - (time1 - time0))

        model.optimize()

        # store the optimal strategy for t as the target to be attacked
        if model.status != grb.GRB.Status.OPTIMAL:
            pass
        else:    
            utility[t] = model.ObjVal
            for i in range(2 * t_num):
                strategy[t][i] = model.getVars()[i].x
            for i in range(t_num):
                coverage[t][i] = model.getVars()[2 * t_num + i].x
    
    target = np.argmax(utility)
    
    return utility[target], target, strategy[target], coverage[target], time1 - time0