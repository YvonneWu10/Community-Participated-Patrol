import json
import numpy as np
import time

import implement.MILP as base
import implement.TDBS as binary
import implement.HW as exact


def save(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)


n = 100
ratios = [1]

err = 0.001
eps = 1e-4
# runtime for a single run is recorded as 7200 seconds if it exceeds 7200 seconds
time_limit = 7200  #2h

# use the inputs with n equal to 100
with open('input/input n=100.json'.format(n), 'r') as f:  
        data = json.load(f)

for ratio in ratios:
    result = []
    
    for rv in range(0, 51):
        rp = rv // ratio
        print("rv:", rv, flush=True)
        
        # run the 30 settings with n equal to 100
        for i in range(30):
            input = data[i]

            ep = input["ep"]
            ev = input["ev"]
            Rd = np.array(input["Rd"])
            Pd = np.array(input["Pd"])
            Ra = np.array(input["Ra"])
            Pa = np.array(input["Pa"])

            cur = {"rv": rv, "rp": rp, "id": input["id"]}

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

    save(result, "store_pv/result ratio={}.json".format(ratio))
    result = []
    print(flush=True)