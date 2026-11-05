import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

FOLDER = r"C:\Users\Luca\Desktop\optomechanical-laser-alignment-testbench\host\data comparison"
COLUMNS = ["err_x", "err_y"]
N_RUNS = 5
DT = 0.033

def load(prefix, i, col):
    df = pd.read_csv(f"{FOLDER}/{prefix}_run{i}.csv").dropna(subset=[col])
    return (df["time_ms"] / 1000.0).to_numpy(), df[col].to_numpy()

def mean_curve(prefix, col):
    runs = [load(prefix, i, col) for i in range(1, N_RUNS + 1)]
    t_max = max(t[-1] for t, _ in runs)
    grid = np.arange(0, t_max + DT, DT)
    Y = np.array([np.interp(grid, t, y, left=np.nan, right=np.nan) for t, y in runs])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        m = np.nanmean(Y, axis=0)
    return grid, m

fig, axes = plt.subplots(len(COLUMNS), 1, figsize=(10, 4 * len(COLUMNS)),
                         sharex=True, squeeze=False)
axes = axes[:, 0]

for ax, col in zip(axes, COLUMNS):
    for prefix in ["slack0", "slack3"]:
        t, m = mean_curve(prefix, col)
        ax.plot(t, m, linewidth=1.5, label=f"{prefix} (average of {N_RUNS} runs)")
    ax.set_ylabel(col)
    ax.grid(True, alpha=0.3)
    ax.legend()

axes[-1].set_xlabel("Time [s]")
fig.suptitle("Slack 0° vs Slack 3°")
plt.tight_layout()
plt.savefig("docs/slackcomparison.png", dpi=150)
plt.show()