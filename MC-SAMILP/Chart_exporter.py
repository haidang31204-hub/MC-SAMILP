import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from Model import model_solver
import math
from parameters import T, N, num_scenarios, h, b

# Run the Model
model, Z, Y, O, H, B = model_solver()
periods = np.arange(1, T + 1)

# Extract first-stage variables

Z_values = [Z[t].value() for t in periods]
Y_values = [Y[t].value() for t in periods]
O_values = [O[t].value() for t in periods]

# Chart 1: Decision Variables

fig, ax1 = plt.subplots(figsize=(12, 6))

ax1.bar(periods, O_values, label="Overtime (O)", color='orange', alpha=0.5)
ax1.plot(periods, Z_values, marker='o', color='red', label="Disassembly (Z)", linewidth=2)
ax1.set_ylabel("Quantity (Z, O)")
ax1.set_ylim(0, max(Z_values)*1.1)

ax2 = ax1.twinx() 
ax2.step(periods, Y_values, where='mid', label="Setup (Y)", color='blue', linestyle='--')
ax2.set_ylabel("Binary Decision (Y)")
ax2.set_ylim(-0.1, 1.5)
ax2.set_yticks([0, 1])
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines + lines2, labels + labels2, loc='upper right')
plt.savefig("decision_variables_chart.png", dpi=300, bbox_inches="tight")
plt.show()
print("Saved: decision_variables_chart.png")

# Bar chart 2: Inventory + Backorder (summed across all items and scenarios)

inventory_sum = []
backorder_sum = []
inventory_avg = []
backorder_avg = []
divisor = len(N) * num_scenarios
for t in periods:
    inv_total_t = sum(H[i][t][gamma].value() for i in N for gamma in range(1, num_scenarios+1))
    back_total_t = sum(B[i][t][gamma].value() for i in N for gamma in range(1, num_scenarios+1))
    inventory_sum.append(inv_total_t)
    backorder_sum.append(back_total_t)
    inventory_avg.append(inv_total_t / divisor)
    backorder_avg.append(back_total_t / divisor)
# 2. Setup Bar Chart Positioning
x_indexes = np.arange(len(periods))  # The label locations
bar_width = 0.35                     # The width of the bars
plt.figure(figsize=(12, 7))
plt.bar(x_indexes - bar_width/2, inventory_avg, width=bar_width, label="Inventory", color='tab:blue', alpha=0.8)
plt.bar(x_indexes + bar_width/2, backorder_avg, width=bar_width, label="Backorder", color='tab:red', alpha=0.8)
plt.xlabel("Period")
plt.ylabel("Quantity (Average per Item & Scenario)")
plt.title("Average Inventory vs Backorder per items & scenarios Over Periods")
plt.xticks(ticks=x_indexes, labels=periods) 
plt.grid(axis='y', linestyle='--', alpha=0.7) # Grid on Y-axis only looks cleaner for bars
plt.legend()
plt.savefig("inventory_backorder_barchart.png", dpi=300, bbox_inches="tight")
plt.show()
print("Saved: inventory_backorder_barchart.png")

# Chart 3: Expected Cost per Period

expected_cost_per_t = []

for t in periods:
    cost_t = 0
    for i in N:
        for gamma in range(1, num_scenarios+1):
            prob = 1 / num_scenarios
            inv = H[i][t][gamma].value()
            back = B[i][t][gamma].value()
            cost_t += prob * (h[i] * inv + b[i] * back)
    # add setup + overtime
    cost_t += (Y[t].value() * (h[i]*0 + 0) + O[t].value())   # You may adjust if needed
    expected_cost_per_t.append(cost_t)
plt.figure(figsize=(12, 7))
plt.plot(periods, expected_cost_per_t, marker='s', label="Expected Cost[t]")
plt.xlabel("Period")
plt.ylabel("Expected Cost")
plt.title("Expected Cost Per Period")
plt.xticks(periods)
plt.grid(True)
plt.legend()
plt.savefig("expected_cost_chart.png", dpi=300, bbox_inches="tight")
plt.show()
print("Saved: expected_cost_chart.png")

# Chart 4: Stochastic Inventory Levels (Boxplot across scenarios for each period)
num_products = len(N)
cols = 2  
rows = math.ceil(num_products / cols)
fig, axes = plt.subplots(rows, cols, figsize=(14, 5 * rows))

if num_products == 1:
    axes = [axes]
else:
    axes = axes.flatten()
for idx, i in enumerate(N):
    ax = axes[idx]  
    
    data_plot = []
    for t in periods:
        inventory_at_t = []
        for gamma in range(1, num_scenarios + 1):
            h_val = H[i][t][gamma].varValue
            b_val = B[i][t][gamma].varValue
            net_val = h_val - b_val
            inventory_at_t.append(net_val)
        data_plot.append(inventory_at_t)
    # Draw boxplot
    ax.boxplot(data_plot, positions=periods, patch_artist=True,
               boxprops=dict(facecolor="lightblue", color="blue", alpha=0.6),
               medianprops=dict(color="red", linewidth=1.5),
               flierprops=dict(marker='o', markerfacecolor='gray', markersize=3, alpha=0.5))
    
    # Customize plot
    ax.axhline(0, color='red', linestyle='--', linewidth=1, label='Zero Level')
    ax.set_title(f"Product {i}: Inventory Variance (across {num_scenarios} scenarios)", fontsize=11, fontweight='bold')
    ax.set_xlabel("Period")
    ax.set_ylabel("Net Inventory (+Inv / -Backlog)")
    ax.grid(True, linestyle='--', alpha=0.5)
for j in range(idx + 1, len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout() 
plt.savefig("inventory_boxplot_all_products.png", dpi=300)
plt.show()