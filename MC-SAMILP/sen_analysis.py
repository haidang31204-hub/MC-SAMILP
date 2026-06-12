import pandas as pd
import matplotlib.pyplot as plt
import copy
import pulp as lp
import numpy as np
import Model 
from parameters import *

def run_sensitivity_analysis():
    # (0.5 = 50%, 1.0 = original, 2.0 = 200%)
    scaling_factors = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
    
    periods = range(1, T + 1)
    
    orig_h = copy.deepcopy(h)
    orig_b = copy.deepcopy(b)
    orig_s = copy.deepcopy(s)
    orig_u = copy.deepcopy(u)
    
    results = []

    print("STARTING SENSITIVITY ANALYSIS")
    print(f"Config: T={T}, N={len(N)}, Scenarios={num_scenarios}")

    def run_scenario(param_name, factor):
        try:
            model, Z, Y, O, H, B = Model.model_solver()
            
            if model.status == lp.LpStatusOptimal:
                total_obj_cost = lp.value(model.objective)
                
                total_avg_inv = 0
                total_avg_back = 0
                
                for i in N:
                    for t in periods:
                        avg_h_it = sum(H[i][t][gamma].varValue for gamma in range(1, num_scenarios+1)) / num_scenarios
                        avg_b_it = sum(B[i][t][gamma].varValue for gamma in range(1, num_scenarios+1)) / num_scenarios
                        
                        total_avg_inv += avg_h_it
                        total_avg_back += avg_b_it
                
                # 2. Sum Y over t
                total_setups = sum(Y[t].varValue for t in periods)
                
                # 3. Sum O over t
                total_overtime = sum(O[t].varValue for t in periods)

                return {
                    "Parameter": param_name,
                    "Factor": factor,
                    "Total Cost": total_obj_cost,
                    "Avg Inventory (Qty)": total_avg_inv,
                    "Avg Backlog (Qty)": total_avg_back,
                    "Total Setups (Count)": total_setups,
                    "Total Overtime (Qty)": total_overtime
                }
            else:
                print(f"  -> Model Infeasible for {param_name} x {factor}")
                return None
        except Exception as e:
            print(f"  -> Error running {param_name} x {factor}: {e}")
            return None

    # TEST 1: HOLDING COST (h)
    print("\n[1/4] Testing Holding Cost (h)...")
    for f in scaling_factors:
        Model.b = orig_b; Model.s = orig_s; Model.u = orig_u

        Model.h = {i: orig_h[i] * f for i in N}
        
        res = run_scenario("Holding Cost (h)", f)
        if res: results.append(res)

    # TEST 2: BACKLOG COST (b)
    print("\n[2/4] Testing Backlog Cost (b)...")
    for f in scaling_factors:
        Model.h = orig_h; Model.s = orig_s; Model.u = orig_u
        Model.b = {i: orig_b[i] * f for i in N}
        
        res = run_scenario("Backlog Cost (b)", f)
        if res: results.append(res)

    # TEST 3: SETUP COST (s)
    print("\n[3/4] Testing Setup Cost (s)...")
    for f in scaling_factors:
        Model.h = orig_h; Model.b = orig_b; Model.u = orig_u
        Model.s = {t: orig_s[t] * f for t in periods}
        
        res = run_scenario("Setup Cost (s)", f)
        if res: results.append(res)
    # TEST 4: OVERTIME COST (u)
    print("\n[4/4] Testing Overtime Cost (u)...")
    for f in scaling_factors:
        Model.h = orig_h; Model.b = orig_b; Model.s = orig_s
        Model.u = {t: orig_u[t] * f for t in periods}
        res = run_scenario("Overtime Cost (u)", f)
        if res: results.append(res)

    Model.h = orig_h; Model.b = orig_b; Model.s = orig_s; Model.u = orig_u

    # Save results to Excel and draw plots
    df = pd.DataFrame(results)
    filename_excel = "Sensitivity_Analysis_Results.xlsx"
    df.to_excel(filename_excel, index=False)
    print(f"\nData saved to {filename_excel}")
    
    plot_full_sensitivity(df)

def plot_full_sensitivity(df):

    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    axes = axes.flatten()
    
    params_list = ["Holding Cost (h)", "Backlog Cost (b)", "Setup Cost (s)", "Overtime Cost (u)"]
    
    for idx, param in enumerate(params_list):
        ax = axes[idx]
        subset = df[df["Parameter"] == param]
        
        if subset.empty: 
            continue
        
        # LEFT Y-AXIS
        if "Holding" in param or "Backlog" in param:
            l1 = ax.plot(subset["Factor"], subset["Avg Inventory (Qty)"], 'b-o', label="Avg Inventory")
            l2 = ax.plot(subset["Factor"], subset["Avg Backlog (Qty)"], 'r-s', label="Avg Backlog")
            ax.set_ylabel("Quantity (Inv/Back)")
        
        elif "Setup" in param:
            l1 = ax.plot(subset["Factor"], subset["Total Setups (Count)"], 'm-D', label="Total Setups")
            ax.set_ylabel("Frequency")
            l2 = [] 

        elif "Overtime" in param:
            l1 = ax.plot(subset["Factor"], subset["Total Overtime (Qty)"], 'c-^', label="Total Overtime")
            ax.set_ylabel("Quantity (Overtime)")
            l2 = []

        ax.set_title(f"Sensitivity to {param}", fontsize=12, fontweight='bold')
        ax.set_xlabel("Scaling Factor (1.0 = Original)")
        ax.grid(True, linestyle='--', alpha=0.6)

        # RIGHT Y-AXIS
        ax2 = ax.twinx()
        l3 = ax2.plot(subset["Factor"], subset["Total Cost"], 'g--', label="Total Objective Cost")
        ax2.set_ylabel("Total Cost ($)", color='green')
        ax2.tick_params(axis='y', labelcolor='green')
    
        lines = l1 + l2 + l3 if isinstance(l2, list) else l1 + [l2] + l3
        labels = [l.get_label() for l in lines]
        ax.legend(lines, labels, loc='best')

    plt.tight_layout()
    plt.savefig("Sensitivity_Analysis_Chart.png", dpi=300)
    print("Chart saved to Sensitivity_Analysis_Chart.png")
    plt.show()

if __name__ == "__main__":
    run_sensitivity_analysis()