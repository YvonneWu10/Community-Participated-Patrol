import matplotlib.pyplot as plt
import json
import numpy as np

n_set = [5, 10, 30, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
base, binary, exact = [], [], []
base_std, binary_std, exact_std = [], [], []


for n in n_set:
    with open('store_n/result n={}.json'.format(n), 'r') as f:  
        record = json.load(f)

    # for every n, compute the average runtime and the standard variance    
    base_time, binary_time, exact_time = 0, 0, 0
    base_count, binary_count, exact_count = 0, 0, 0
    base_data, binary_data, exact_data = [], [], []
    for res in record:
        if "comment" not in res["base"]:
            base_time += res["base"]["time"]
            base_count += 1
            base_data.append(res["base"]["time"])
        else:
            base_time += 7200
            base_count += 1
            base_data.append(7200)

        if "comment" not in res["binary"]:
            binary_time += res["binary"]["time"]
            binary_count += 1
            binary_data.append(res["binary"]["time"])
        else:
            binary_time += 7200
            binary_count += 1
            binary_data.append(7200)

        if "comment" not in res["exact"]:
            exact_time += res["exact"]["time"]
            exact_count += 1
            exact_data.append(res["exact"]["time"])
        else:
            exact_time += 7200
            exact_count += 1
            exact_data.append(7200)

    base_time /= base_count
    binary_time /= binary_count
    exact_time /= exact_count

    base.append(base_time)
    binary.append(binary_time)
    exact.append(exact_time)
    base_std.append(np.std(base_data))
    binary_std.append(np.std(binary_data))    
    exact_std.append(np.std(exact_data))


plt.figure(figsize=(10, 4))
plt.subplots_adjust(top=0.98, bottom=0.18, left=0.12, right=0.98)

plt.errorbar(n_set, base, yerr=base_std, label="MILP", marker="o", ecolor="#ADD8E6", capsize=3)
plt.errorbar(n_set, binary, yerr=binary_std, label="TDBS", marker="o", ecolor="#FFA500", capsize=3)
plt.errorbar(n_set, exact, yerr=exact_std, label="HW", marker="o", ecolor="#90EE90", capsize=3)

plt.legend(fontsize=20)
plt.yticks(fontsize=20)
plt.xticks(fontsize=20)

plt.xlabel("Number of Targets", fontsize=20)
plt.ylabel("Runtime (s)", fontsize=20)
plt.savefig("figures/number of targets - runtime.pdf", dpi=1200)