import numpy as np
import pandas as pd

# Problem size parameters
seed = 3
T = 8  # Number of time periods
N = list(range(3))  # Set of product types
num_scenarios = 200  # Number of scenarios
Fixed = False # Fixed Cost parameters used or not

# Fixed Cost parameters
F = 0.0 #disassembly operation time
K = 100000
Max_capacity = 300
Max_inventory = 500

if Fixed:
     if seed is not None:
        np.random.seed(seed)
        C = {t: 300 for t in range(1, T + 1)} #Available disassembly capacity in period t
        s = {t: 500 for t in range(1, T + 1)} #Setup cost
        u = {t: 20 for t in range(1, T + 1)}  #cost of adding a unit of extra capacity in period t 
        #Set u to 15 to test
        R = {i: np.random.randint(1, 4) for i in N} #Disassembly yield rate
        h = {i: 20 for i in N} #Holding cost per unit of component i 
        #Set h to 10 to test 
        b = {i: 40 for i in N} #Backlog cost per unit of component i 
        #Set b to 800 to test
        I_0 = {i: 500 for i in N}  # initial inventory of component i
        D = {(i, t): 300 for i in N for t in range(1, T + 1)} # External demand for component i in period t
        print("Fixed cost parameters loaded.")
else: 
# Cost parameters
    if seed is not None:
        np.random.seed(seed)
        C = {t: 300 for t in range(1, T + 1)} #Available disassembly capacity in period t
        s = {t: 500 for t in range(1, T + 1)} #Setup cost
        u = {t: 30 for t in range(1, T + 1)}  #cost of adding a unit of extra capacity in period t
        R = {i: np.random.randint(1, 4) for i in N} #Disassembly yield rate
        h = {i: 10 for i in N} #Holding cost per unit of component i
        b = {i: 100 for i in N} #Backlog cost per unit of component i
        I_0 = {i: np.random.randint(100, 200) for i in N}  # initial inventory of component i
        D = {(i, t): np.random.randint(150, 500) for i in N for t in range(1, T + 1)} # External demand for component i in period t
        print("Cost parameters generated randomly.")
#Lead time parameters
if seed is not None:
    np.random.seed(seed)  
    L_min = {i: np.random.randint(1, 3) for i in N}
    L_max = {i: int(L_min[i] + np.random.randint(2, 3)) for i in N}
    L_it = {(i, t): int(np.random.randint(L_min[i], L_max[i])) for i in N for t in range(1, T + 1)}