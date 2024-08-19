import json
import numpy as np
import time

import implement.MILP as base
import implement.TDBS as binary
import implement.HW as exact


def save(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)


n_set = [5, 10, 30, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]

# test for n in n_set
for n in n_set:
    print("scale:", n, flush=True)

    # runtime for a single run is recorded as 7200 seconds if it exceeds 7200 seconds
    time_limit = 7200  #2h

    # input is generated and stored
    with open('input/input n={}.json'.format(n), 'r') as f:  
        data = json.load(f)
    
    result = []

    err = 0.001
    eps = 1e-4
    rp = n // 2
    rv = n // 2
    # run 30 settings for a single n
    for i in range(30):
        input = data[i]
        
        ep = input["ep"]
        ev = input["ev"]
        Rd = np.array(input["Rd"])
        Pd = np.array(input["Pd"])
        Ra = np.array(input["Ra"])
        Pa = np.array(input["Pa"])

        cur = {"id": input["id"]}

        # run the 3 solutions and record the runtime
        time1 = time.time()
        u_base, t_opt, _, _, time_base = base.maxDefUnility(n, rp, rv, ep, ev, Rd, Pd, Ra, Pa, time_limit)
        time2 = time.time()
        u_binary, _, _, _, time_binary = binary.maxDefUnility(n, rp, rv, ep, ev, Rd, Pd, Ra, Pa, err, time_limit)
        time3 = time.time()
        u_exact, _, _, _, time_exact = exact.maxDefUnility(n, rp, rv, ep, ev, Rd, Pd, Ra, Pa, time_limit)
        time4 = time.time()

        print(cur["id"], "done", flush=True)

        # store the optimal utility and runtime
        cur["base"] = {"utility": u_base, "time": time2 - time1}
        cur["binary"] = {"utility": u_binary, "time": time3 - time2}
        cur["exact"] = {"utility": u_exact, "time": time4 - time3}

        if time_base >= time_limit:
            cur["base"]["comment"] = "timeout"
            print(cur["id"], "base timeout", flush=True)
        if time_binary >= time_limit:
            cur["binary"]["comment"] = "timeout"
            print(cur["id"], "binary timeout", flush=True)
        if time_exact >= time_limit:
            cur["exact"]["comment"] = "timeout"
            print(cur["id"], "exact timeout")

        result.append(cur)

    save(result, "store_n/result n={}.json".format(n))
    print(flush=True)