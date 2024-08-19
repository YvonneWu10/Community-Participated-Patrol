import numpy as np
from math import ceil
import json
import time

# Algorithm 1 (refer to function judge in TDBS.py)
def judgeWithNoPt(n, t, pt, vt, Ra, Pa, rp, rv, ep, ev):
    ct = min(1, ep * pt + ev * vt)
    Uat = Ra[t] * (1 - ct) + Pa[t] * ct
    neededCoverage = [(0, 0)] * n
    v = np.zeros(n)
    v[t] = vt

    for i in range(n):
        if i == t:
            continue
        if Uat < Pa[i]:
            return False, None, None
        c = (Ra[i] - Uat) / (Ra[i] - Pa[i])
        c = max(0, c)
        vi = min(rv, c // ev)
        rv -= vi
        v[i] = vi
        neededCoverage[i] = (c - vi * ev, i)
    
    neededCoverage = sorted(neededCoverage, key=lambda x: x[0], reverse=True)

    for k in range(int(rv)):
        nc, i = neededCoverage[k]
        if nc == 0:
            break
        neededCoverage[k] = (0, i)
        v[i] += 1
    
    totalNeeded = 0
    for i in range(n):
        totalNeeded += neededCoverage[i][0]
    
    if totalNeeded > rp * ep:
        return False, None, None
    
    p = [0] * n
    for k in range(n):
        nc, i = neededCoverage[k]
        p[i] = nc / ep
    p[t] = pt

    return True, p, v.tolist()


def findOptimalVt(n, t, Ra, Pa, rp, rv, ep, ev):
    vleft = 0
    vright = rv
    vt = None

    # binary search on villagers allocated to t
    while vleft <= vright:
        curvt = (vleft + vright) // 2
        result, _, _ = judgeWithNoPt(n, t, 0, curvt, Ra, Pa, rp, rv - curvt, ep, ev)
        if result:
            vleft = curvt + 1
            vt = curvt
        else:
            vright = curvt - 1
    
    return vt


# Algorithm 4
def findOptimalPt(n, t, vt, Rd, Pd, Ra, Pa, rp, rv, ep, ev, time0, time_limit):
    eps = 1e-6

    Ua = Ra.copy()
    Ua[t] = float("-inf")
    haveVillager = [False] * n
    vs = np.zeros(n)   # villager strategy
    ps = np.zeros(n)   # patroller strategy
    vs[t] = vt
    reachEnd = set()
    Pa_globalMax = max(Pa)

    # greedily allocate all villagers at first
    while rv > 0:
        # cannot allocate villagers to target with attacher's utility reaching Pa
        i = np.argmax([float("-inf") if i in reachEnd else Ua[i] for i in range(n)])
        assert(i != t)
        
        Ua[i] -= (Ra[i] - Pa[i]) * ev
        Ua[i] = max(Ua[i], Pa[i])
        haveVillager[i] = True
        rv -= 1
        vs[i] += 1

        if Ua[i] <= Pa[i]:
            reachEnd.add(i)

    ct = min(1, ev * vt)
    Ua[t] = Ra[t] * (1 - ct) + Pa[t] * ct
    Uav = Ua.copy()

    if Ua[t] <= Pa[t]:
        reachEnd.add(t)

    width = [1 / (Ra[i] - Pa[i]) for i in range(n)]
    noPatroller = [True] * n
    cannotExchange = set()

    # distribute ranger efforts with Waterfilling and execute swaps
    while rp > eps and True in noPatroller and len(reachEnd) < n:
        if time.time() - time0 >= time_limit:
            break

        # edge cases
        t_end = False
        if len(reachEnd):
            tmp = max([Pa[i] for i in reachEnd])
            if Ua[t] + eps < tmp:
                return False, None, None
            elif Ua[t] - eps < tmp and tmp < Ua[t] + eps:
                t_end = True

        # Ua1 is the highest utility，set1 contains the targets whose attacker's utlity would be decreased this iteration
        Ua1 = max([Ua[i] for i in range(n) if i not in reachEnd])
        set1 = set([i for i in range(n) if Ua[i] == Ua1]) - reachEnd
        if t_end:
            set1 -= {t}
            if not len(set1):
                break
        # Ua2 is the second highest utility
        Ua2 = None
        tmp = sorted(list(set([Ua[i] for i in set(range(n)) - reachEnd])), reverse=True)   # Ua2 may not exist
        if len(tmp) > 1:
            Ua2 = tmp[1]
        minU = float("inf")   # the decrease of sea level this iteration
        minI = None   # outp
        minJ = None   # outv
        exchange = True

        # find the minimum decrease of sea level during a swap
        for i in set1 - {t}:
            for j in set(range(n)) - set1 - cannotExchange - {t}:
                if width[j] < width[i] and noPatroller[j] and haveVillager[j]:
                    curU = Ua[i] - Uav[i] + (Ra[j] - (Ra[j] - Pa[j]) * ev * (vs[j] - 1) - Uav[i]) * (Ra[i] - Pa[i]) / ((Ra[j] - Pa[j]) - (Ra[i] - Pa[i]))
                    if curU < minU:
                        minU = curU
                        minI = i
                        minJ = j

        # judge whether the decrease of sea level would break the bound of Pa, Ua2, and update minU
        if t in set1:
            tmp = Pa_globalMax
        else:
            tmp = max([Pa[i] for i in set1])
        if Ua1 - minU < tmp:
            minU = Ua1 - tmp
            exchange = False
        
        if Ua2 and Ua1 - minU < Ua2:
            minU = Ua1 - Ua2
            exchange = False

        if exchange and minJ and Ua1 - minU < Pa[minJ]:
            minU = Ua1 - Pa[minJ]
            exchange = False
            cannotExchange.add(minJ)

        # judge whether there are enough rangers
        nc = minU * sum([width[i] for i in set1])
        if nc > rp * ep:
            break

        # for targets in set1, decrease the attack's utility on them
        for i in set1:
            noPatroller[i] = False
            Ua[i] -= minU
            pi = (Uav[i] - Ua[i]) / (ep * (Ra[i] - Pa[i]))
            rp -= (pi - ps[i])
            ps[i] = pi
            if Ua[i] <= Pa[i]:
                reachEnd.add(i)
        
        # execute a swap
        if exchange:
            vs[minJ] -= 1
            ps[minJ] = ps[minI]
            Uav[minJ] = Ra[minJ] - (Ra[minJ] - Pa[minJ]) * min(1, vs[minJ] * ev)
            Ua[minJ] = Ua[minI]
            noPatroller[minJ] = False
            if Uav[minJ] == Ra[minJ]:
                haveVillager[minJ] = False
            if Ua[minJ] > Pa[minJ]:
                reachEnd.discard(minJ)
            
            vs[minI] += 1
            ps[minI] = 0
            Uav[minI] = Ra[minI] - (Ra[minI] - Pa[minI]) * min(1, vs[minI] * ev)
            Ua[minI] = Uav[minI]
            noPatroller[minI] = True
            haveVillager[minI] = True
            if Ua[minI] <= Pa[minI]:
                reachEnd.add(minI)

    
    # allocate the remaining rangers, similar to the iteration above (omit some procedures since no swaps can be executed any more)
    t_end = False
    while rp > eps and len(reachEnd) < n:
        if time.time() - time0 >= time_limit:
            break

        if len(reachEnd):
            tmp = max([Pa[i] for i in reachEnd])
            if Ua[t] + eps < tmp:
                return False, None, None
            elif Ua[t] - eps < tmp and tmp < Ua[t] + eps:
                t_end = True

        Ua1 = max([Ua[i] for i in range(n) if i not in reachEnd])
        set1 = set([i for i in range(n) if Ua[i] == Ua1]) - reachEnd
        if t_end:
            set1 -= {t}
            if not len(set1):
                break
        Ua2 = None
        tmp = sorted(list(set([Ua[i] for i in set(range(n)) - reachEnd])), reverse=True)
        if len(tmp) > 1:
            Ua2 = tmp[1]

        if t in set1:
            tmp = Pa_globalMax
        else:
            tmp = max([Pa[i] for i in set1])
        minU = Ua1 - tmp
        if Ua2 and Ua2 > tmp:
            minU = Ua1 - Ua2
        
        widthSum = sum([width[i] for i in set1])
        p = min(rp, minU * widthSum / ep)
        utilityDrop = p * ep / widthSum

        for i in set1:
            Ua[i] -= utilityDrop
            pi = (Uav[i] - Ua[i]) / (ep * (Ra[i] - Pa[i]))
            rp -= (pi - ps[i])
            ps[i] = pi
            if Ua[i] <= Pa[i]:
                reachEnd.add(i)
    
    # judge whether the best response is ensured
    for i in range(n):
        if Ua[i] > Ua[t] + eps:
            return False, None, None

    return True, ps, vs


# Algorithm 5
def maxDefUnility(n, rp, rv, ep, ev, Rd, Pd, Ra, Pa, time_limit):
    time0 = time.time()
    max_utility = float("-inf")
    opt_t = None
    opt_p = None
    opt_v = None

    # enumerate every target as the target to be attacked
    for t in range(n):
        # find the optimal number of villagers to be allocated to t
        vt = findOptimalVt(n, t, Ra, Pa, rp, rv, ep, ev)

        # vt == None represents that t cannot be the attacker's best response even if no rangers and villagers are allocated to t
        if vt == None:
            continue

        # limit the time
        time1 = time.time()
        if time1 - time0 >= time_limit:
            return max_utility, opt_t, opt_p, opt_v, time1 - time0
        
        # find the optimal number of ranger efforts to be allocated to t
        result, p, v = findOptimalPt(n, t, vt, Rd, Pd, Ra, Pa, rp, rv - vt, ep, ev, time0, time_limit)

        # update the optimal defender's utility
        if result:
            ct = min(1, ep * p[t] + ev * vt)
            Udt = Rd[t] * ct + Pd[t] * (1 - ct)
            if Udt > max_utility:
                max_utility = Udt
                opt_t = t
                opt_p = p
                opt_v = v
    
    return max_utility, opt_t, opt_p, opt_v, time.time() - time0