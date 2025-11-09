import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# --------------------------
# Dodani podatki z LFR benchmarka (iz Table 3)
# --------------------------
data = {
    "Algorithm": [
        "Louvain", "Label Propagation", "Fast Label Propagation", "Leiden",
        "Infomap", "Walktrap", "Greedy Modularity", "Girvan–Newman"
    ],
    "LFR Benchmark":         [0.668, 0.668, 0.668, 0.668, 0.668, 0.668, 0.659, 0.476],
    "Zachary’s karate club": [0.58457, 0.56520, 0.55826, 0.58460, 0.58300, 0.58080, 0.58280, 0.57640],
    "Neuroscience Network":  [0.44077, 0.30949, 0.37273, 0.44490, 0.43210, 0.32316, 0.41096, 0.35806],
    "Synthetic Network":     [0.76294, 0.70496, 0.74724, 0.76383, 0.75960, 0.75609, 0.74609, 0.64646],
    "Social Network":        [0.90862, 0.81517, 0.80918, 0.91144, 0.84092, 0.85014, 0.90700, np.nan],
    "LFR Benchmark 10k":     [0.67586, 0.67455, 0.67586, 0.67586, 0.67586, 0.67586, np.nan, np.nan],
    "E-mail Network":        [0.79091, 0.69716, 0.69585, 0.80838, 0.80796, np.nan, np.nan, np.nan],
    "Citation Network":      [0.81151, 0.57483, 0.61951, 0.83249, np.nan, np.nan, np.nan, np.nan],
}

df = pd.DataFrame(data).set_index("Algorithm")

# --------------------------
# Risanje heatmape
# --------------------------
plt.figure(figsize=(10, 5))
sns.heatmap(
    df, annot=True, fmt=".3f", cmap="YlGnBu",
    cbar_kws={'label': 'Modularity (Q)'}, linewidths=0.5
)

plt.title("Variation in Community Detection Benchmark Across Networks", fontsize=13, pad=12)
plt.xlabel("Network")
plt.ylabel("Algorithm")
plt.xticks(rotation=30, ha='right')
plt.tight_layout()
plt.show()