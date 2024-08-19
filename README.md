# Improving Community-Participated Patrol for Anti-Poaching

## Table of Contents

- [Improving Community-Participated Patrol for Anti-Poaching](#improving-community-participated-patrol-for-anti-poaching)
  - [Table of Contents](#table-of-contents)
  - [General Information](#general-information)
  - [File Structure](#file-structure)
  - [Reproducing the Experiments](#reproducing-the-experiments)

## General Information

This repository contains the source code for the experiments in a paper submitted to AAAI 2025: Improving Community-Participated Patrol for Anti-Poaching.

## File Structure
```
└── code
    ├── figures # Figure 2
    ├── implement # the implementation of MILP, TDBS, and HW
    ├── input # the input of the experiments
    ├── store_n # the stored runtime with increasing n
    ├── store_pv # the stored runtime with increasing rp, rv
    ├── draw_runtime_n.py # the script to draw Figure 2(a)
    ├── draw_runtime_rp_rv.py # the script to draw Figure 2(b)
    ├── runtime - n.py 
        # the script to evaluate runtime with increasing n
    └── runtime - rp rv.py 
        # the script to evaluate runtime with increasing rp, rv
```

## Reproducing the Experiments

+ To re-evaluate runtime with increasing $n$, enter
  ```
  python3 runtime_n.py
  ```
+ To re-evaluate runtime with increasing $r^{\mathrm{p}}$, $r^{\mathrm{v}}$, enter
  ```
  python3 runtime_rp_rv.py
  ```
+ To generate Figure 2 in the paper, enter
  ```
  python3 draw_runtime_n.py
  python3 draw_runtime_rp_rv.py
  ```
