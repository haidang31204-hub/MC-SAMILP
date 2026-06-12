import pulp as lp
from pulp import *
import numpy as np
import pandas as pd
from parameters import *
from MC_sampling import mc_sampling

# Input MC_sampling. for MCMILP
alpha_samples = mc_sampling(auto_load=True)

def model_solver():
    model = lp.LpProblem("MC-SAMILP_CDLS", lp.LpMinimize)  

    # Define first-stage decision variables
    Z=lp.LpVariable.dicts("Z", range(1,T+1), lowBound=0, cat=lp.LpInteger) #Disassembly quantity
    Y=lp.LpVariable.dicts("Y", range(1,T+1), cat=lp.LpBinary) #Disassembly decision
    O=lp.LpVariable.dicts("O", range(1,T+1), lowBound=0, cat=lp.LpInteger) #Disassembly overtime
   
    # Define second-stage decision variables
    H=lp.LpVariable.dicts("Inventory level", (N, range(1,T+1), range(1, num_scenarios+1)), lowBound=0,) #Inventory level
    B=lp.LpVariable.dicts("Backorder level", (N, range(1,T+1), range(1, num_scenarios+1)), lowBound=0,) #Backorder level
    

    # Define objective function
    obj=[]
    for t in range(1, T+1):
        expected_cost_t = []
        for i in N:
            for gamma in range(1, num_scenarios+1):
                prob_scenario = 1/num_scenarios
                expected_cost_t.append(prob_scenario*(h[i]*H[i][t][gamma] + b[i]*B[i][t][gamma]))
        
        fixed_cost_t = (s[t]*Y[t] + u[t]*O[t])
        obj.append(lp.lpSum(expected_cost_t + fixed_cost_t))
    model += lp.lpSum(obj), "Expected total cost"
    # Define constraints
    # Inventory balance constraints
    for i in N:
        for t in range(1, T+1):
            D_tau = lp.lpSum(D[(i, tau)] for tau in range(1, t+1))
            for gamma in range(1, num_scenarios+1):
                arrival_certain = lp.lpSum(R[i] * Z[tau] 
                                        for tau in range(1, t - L_max[i]+1) 
                                        if tau >= 1) 
                arrival_stochastic = lp.lpSum(R[i] * Z[tau] * alpha_samples[i][tau][t][gamma] 
                                        for tau in range(1,t+1) if t-L_max[i] < tau <= t-L_min[i]
                                        if tau >= 1)  
                model += H[i][t][gamma] - B[i][t][gamma] == I_0[i] + arrival_certain + arrival_stochastic - D_tau, f"Inventory_Balance_{i}_{t}_{gamma}"
    # Others Constraints
    for t in range(1, T+1):
        model += Z[t] <= K * Y[t], f"Setup_Constraint_{t}"
        model += F*Z[t] <= C[t] + O[t], f"Overtime_Capacity_Constraint_{t}"
        model += Z[t] <= Max_capacity, f"Nonnegativity_Z_{t}"
        print(f"Added constraints for period {t}")
    
    # Solve the problem
    print("Solving the model...")
    model.solve()
    
# Output results
    print("INPUT PARAMETERS PER PERIOD")
    
    param_data = []
    for t in range(1, T + 1):
        row = {
            "Period": t,
            "Capacity (C)": C[t],
            "Setup Cost (s)": s[t],
            "Overtime Cost (u)": u[t]
        }
        # Demand per product
        for i in N:
            row[f"Demand_Prod_{i}"] = D[(i, t)]
        param_data.append(row)
    
    df_params = pd.DataFrame(param_data)
    df_params.set_index("Period", inplace=True)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(df_params)
    
    # 2. Static Parameters
    print("\n--- Item Parameters ---")
    item_data = []
    for i in N:
        item_data.append({
            "Product": i,
            "Initial Inv (I0)": I_0[i],
            "Yield (R)": R[i],
            "Hold Cost (h)": h[i],
            "Back Cost (b)": b[i],
            "L_min": L_min[i],
            "L_max": L_max[i]
        })
    print(pd.DataFrame(item_data).set_index("Product"))

    # 3. Display Optimization Results and Input Summary
    print("\n" + "="*50)
    print("OPTIMIZATION RESULTS PER PERIOD")
    print("="*50)
    if model.status == lp.LpStatusOptimal:
        results_data = []
        for t in range(1, T + 1):
            # Display first-stage decision variables
            z_val = Z[t].varValue
            y_val = Y[t].varValue
            o_val = O[t].varValue
            row = {
                "Period": t,
                "Z (Disassembly)": z_val,
                "Y (Setup)": y_val,
                "O (Overtime)": o_val
            }
            # Calculate and display expected inventory and backlog levels
            for i in N:
                avg_inv = sum(H[i][t][gamma].varValue for gamma in range(1, num_scenarios+1)) / num_scenarios
                avg_back = sum(B[i][t][gamma].varValue for gamma in range(1, num_scenarios+1)) / num_scenarios
                
                row[f"Exp_Inv_Prod_{i}"] = round(avg_inv, 2)
                row[f"Exp_Back_Prod_{i}"] = round(avg_back, 2)
            
            results_data.append(row)
        
        df_results = pd.DataFrame(results_data)
        df_results.set_index("Period", inplace=True)
        print(df_results)
        
        print(f"\nTotal Objective Cost: {lp.value(model.objective):,.2f}")
    else:
        print("Model did not solve successfully.")

    return model, Z, Y, O, H, B
if __name__ == "__main__":
    model_solver()
