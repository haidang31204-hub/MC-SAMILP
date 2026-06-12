
import numpy as np
import pandas as pd
import os
from parameters import *
"""Control panel"""
def mc_sampling(save_csv = True, 
                         auto_load = True,
                         filename = "MC_alpha_samples.csv" 
                         ):
  if auto_load and os.path.exists(filename):
   
    print(f"Loading alpha_samples from existed file {filename}")
    df = pd.read_csv(filename)
    data = df.to_numpy()
    alpha = data.reshape(len(N), T + 1, T + 1, num_scenarios)
    alpha_samples = {
        i : {
            tau: {
                t: {gamma + 1: int(alpha[i, tau, t, gamma]) for gamma in range(num_scenarios)}
                for t in range(1, T + 1)
            }
            for tau in range(1, T + 1)
        }
        for i in range(len(N))
    }
    return alpha_samples
  else:
    print("Generating new alpha_samples via Monte Carlo sampling...")
    if seed is not None:
        np.random.seed(seed)
    L = np.zeros((len(N), T+1, num_scenarios), dtype=int)
    for i in range(len(N)):
        L[i, 1:, :] = np.random.randint(L_min[i], L_max[i] + 1, size=(T, num_scenarios))
#Tạo Li
    alpha = np.zeros((len(N), T+1, T+1, num_scenarios), dtype=int)
    for gamma in range(num_scenarios):
        for i in range(len(N)):
            for tau in range(1, T + 1):
                for t in range(1, T + 1):
                    alpha[i, tau, t, gamma] = 1 if (t - tau) >= L[i, tau, gamma] else 0

    alpha_samples = {
        i : {
            tau: {
                t: {gamma + 1: int(alpha[i, tau, t, gamma]) for gamma in range(num_scenarios)}
                for t in range(1, T + 1)
            }
            for tau in range(1, T + 1)
        }
        for i in range(len(N))
    }

    # Save as CSV file
    if save_csv:
        data = alpha.reshape(len(N) * (T+1) * (T+1), num_scenarios)
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"Saved alpha_samples into {filename}")

    return alpha_samples


# Testing
if __name__ == "__main__":
    alpha_samples = mc_sampling(save_csv = True, 
                         auto_load = True,
                         filename = "MC_alpha_samples.csv" 
                         )
    print("Generated alpha_samples dictionary form.")
    print("Check: alpha_samples =", alpha_samples[0][1][1][10])
