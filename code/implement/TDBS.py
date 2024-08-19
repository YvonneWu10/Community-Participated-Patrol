import numpy as np
import time


# Algorithm 1
def judge(n, t, pt, vt, Ra, Pa, rp, rv, ep, ev):
    ct = min(1, ep * pt + ev * vt)
    Uat = Ra[t] * (1 - ct) + Pa[t] * ct
    neededCoverage = [(0, 0)] * n
    v = np.zeros(n)
    v[t] = vt

    # allocate as many villagers as possible
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

    # allocate villagers, trying to minimize the wasted coverage
    for k in range(int(rv)):
        nc, i = neededCoverage[k]
        if nc == 0:
            break
        neededCoverage[k] = (0, i)
        v[i] += 1

    # judge whether there are enough rangers    
    totalNeeded = 0
    for i in range(n):
        totalNeeded += neededCoverage[i][0]
    
    if totalNeeded > rp * ep:
        return False, None, None
    
    # return the generated strategy
    p = [0] * n
    for k in range(n):
        nc, i = neededCoverage[k]
        p[i] = nc / ep
    p[t] = pt

    return True, p, v.tolist()


# Algorithm 2
def maxDefUnility(n, rp, rv, ep, ev, Rd, Pd, Ra, Pa, error, time_limit):
    time0 = time.time()
    max_utility = float("-inf")
    opt_t = None
    opt_p = None
    opt_v = None

    # enumerate every target as the target to be attacked
    for t in range(n):
        vleft = 0
        vright = rv
        vt = None

        # binary search on villagers allocated to t
        while vleft <= vright:
            curvt = (vleft + vright) // 2
            result, _, _ = judge(n, t, 0, curvt, Ra, Pa, rp, rv - curvt, ep, ev)
            if result:
                vleft = curvt + 1
                vt = curvt
            else:
                vright = curvt - 1
        # vt == None represents that t cannot be the attacker's best response even if no rangers and villagers are allocated to t
        if vt == None:
            continue

        pleft = 0
        pright = ev / ep
        if vt == rv:
            pright = rp
        p = None
        v = None

        # binary search on rangers allocated to t
        while True:
            pt = (pleft + pright) / 2
            result, curp, curv = judge(n, t, pt, vt, Ra, Pa, rp - pt, rv - vt, ep, ev)
            if result:
                pleft = pt
                p = curp
                v = curv
            else:
                pright = pt
            if pright - pleft <= error:
                if p == None or v == None:
                    result, curp, curv = judge(n, t, pleft, vt, Ra, Pa, rp - pleft, rv - vt, ep, ev)
                    if result:
                        p = curp
                        v = curv
                break
        
        # update the optimal defender's utility
        assert(p != None and v != None)
        ct = min(1, ep * p[t] + ev * vt)
        Udt = Rd[t] * ct + Pd[t] * (1 - ct)
        if Udt > max_utility:
            max_utility = Udt
            opt_t = t
            opt_p = p
            opt_v = v
    
    return max_utility, opt_t, np.array(opt_p), np.array(opt_v), time.time() - time0