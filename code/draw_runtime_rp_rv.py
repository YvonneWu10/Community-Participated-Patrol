import matplotlib.pyplot as plt
import json
import numpy as np


with open('store_pv/result ratio={}.json'.format(1), 'r') as f:  
    raw = json.load(f)


rv_set = range(0, 51)
base, binary, exact = [], [], []
base_low, binary_low, exact_low = [], [], []
base_high, binary_high, exact_high = [], [], []

# for every (rp, rv), store the average runtime, the minimum runtime and the 97th percentile  
for rv in range(0, 51):
    data = raw[30 * rv: 30 * rv + 30]
    base_time, binary_time, exact_time = 0, 0, 0
    base_count, binary_count, exact_count = 0, 0, 0
    base_data, binary_data, exact_data = [], [], []
    for i in range(30):
        assert(data[i]["rv"] == rv)
        if "comment" not in data[i]["base"]:
            base_time += data[i]["base"]["time"]
            base_count += 1
            base_data.append(data[i]["base"]["time"])
        else:
            base_time += 7200
            base_count += 1
            base_data.append(7200)

        if "comment" not in data[i]["binary"]:
            binary_time += data[i]["binary"]["time"]
            binary_count += 1
            binary_data.append(data[i]["binary"]["time"])
        else:
            binary_time += 7200
            binary_count += 1
            binary_data.append(7200)

        if "comment" not in data[i]["exact"]:
            exact_time += data[i]["exact"]["time"]
            exact_count += 1
            exact_data.append(data[i]["exact"]["time"])
        else:
            exact_time += 7200
            exact_count += 1
            exact_data.append(7200)
        base_data.append(data[i]["base"]["time"])
        binary_data.append(data[i]["binary"]["time"])
        exact_data.append(data[i]["exact"]["time"])
    
    base.append(base_time / base_count)
    binary.append(binary_time / binary_count)
    exact.append(exact_time / exact_count)

    base_low.append(np.min(base_data))
    base_high.append(np.percentile(base_data, 97))
    binary_low.append(np.min(binary_data))
    binary_high.append(np.percentile(binary_data, 97))
    exact_low.append(np.min(exact_data))
    exact_high.append(np.percentile(exact_data, 97))


plt.figure(figsize=(10, 4))
plt.subplots_adjust(top=0.98, bottom=0.18, left=0.15, right=0.98)

plt.plot(rv_set, base, label="MILP", marker="o", markersize=3)
plt.plot(rv_set, binary, label="TDBS", marker="o", markersize=3)
plt.plot(rv_set, exact, label="HW", marker="o", markersize=3)

plt.fill_between(rv_set, base_low, base_high, label="MILP", alpha=0.3)
plt.fill_between(rv_set, binary_low, binary_high, label="TDBS", alpha=0.3)
plt.fill_between(rv_set, exact_low, exact_high, label="HW", alpha=0.3)

plt.legend(fontsize=20)
plt.yticks(fontsize=20)
plt.xticks(fontsize=20)

plt.xlabel("Villager Resources (rv)", fontsize=20)
plt.ylabel("Runtime (s)", fontsize=20)
plt.savefig("figures/villager resources - runtime.pdf", dpi=1200)