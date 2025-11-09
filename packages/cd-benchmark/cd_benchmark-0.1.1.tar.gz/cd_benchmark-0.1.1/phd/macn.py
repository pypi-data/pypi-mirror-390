import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import networkx as nx

# 1) preberi in očisti
df = pd.read_csv("data/citation_edges.csv")  # ne uporabljaj skiprows
df = df.dropna(subset=["source", "target"])
df["source"] = df["source"].astype(str).str.strip()
df["target"] = df["target"].astype(str).str.strip()

# opcijsko: odstrani očitno pokvarjene/odrezane vnose
df = df[(df["source"].str.len() > 10) & (df["target"].str.len() > 10)]

# 2) NetworkX graf
G = nx.from_pandas_edgelist(df, "source", "target", create_using=nx.DiGraph)

# 3A) Če tvoja CommunityAnalysis sprejme NetworkX, uporabi G neposredno:
# ca = CommunityAnalysis(graph=G)

# 3B) Če CommunityAnalysis pod pokrovom pretvarja v igraph (in zato pada):
#    relabel na cela števila, DOI ohrani v 'name'
H = nx.convert_node_labels_to_integers(G, label_attribute="name")

# naprej uporabljaj H
from cd_benchmark.analysis import CommunityAnalysis
from cd_benchmark.visualization import GraphVisualizer

gv = GraphVisualizer(H)
ca = CommunityAnalysis(graph=H)  # H ima int ID-je, DOI je v node attr 'name'

algorithms = ["Louvain", "Girvan Newman", "Fast Label Propagation", "Walktrap", "Infomap", "Greedy Modularity", "Leiden"]
df_res = ca.run(algorithms=algorithms)

for alg in algorithms:
    ca.visualize_by_method(method=alg, how="max", metric="Modularity")