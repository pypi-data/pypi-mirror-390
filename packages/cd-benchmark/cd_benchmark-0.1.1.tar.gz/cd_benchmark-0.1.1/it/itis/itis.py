from cd_benchmark.analysis import CommunityAnalysis
from cd_benchmark.benchmark import CommunityBenchmark
from cd_benchmark.generator import GraphGenerator
from cd_benchmark.visualization import GraphVisualizer
from networkx.generators.community import LFR_benchmark_graph
import math, networkx as nx


n = 150
tau1 = 2.5
tau2 = 1.5
mu = 0.1

# 1) omeji max stopnjo, da ne sili skupnosti v velikane
min_degree = 10
max_degree = 30  # znižaj, če želiš manjše skupnosti

# 2) izračunaj varno spodnjo mejo za velikost skupnosti
min_comm_safe = math.ceil((1 - mu) * max_degree) + 1   # npr. (0.9*30)+1 = 28
min_community = 20
max_community = 40  # dovolj široko

print(min_community)

G = nx.LFR_benchmark_graph(
    n=n,
    tau1=tau1, tau2=tau2, mu=mu,
    min_degree=min_degree, max_degree=max_degree,
    min_community=min_community, max_community=max_community,
    max_iters=100000, seed=11
)

viz = GraphVisualizer(G)
viz.draw_graph("Graph G", node_color="lightblue", with_labels=False, node_size=40)

ca = CommunityAnalysis(graph=G)

algorithms = ["Louvain", "Leiden", "Infomap", "Girvan Newman", "Label Propagation", "Fast Label Propagation", "Walktrap", "Greedy Modularity"]
df = ca.run(algorithms=algorithms)

for alg in algorithms:
    ca.visualize_by_method(method=alg, how="max", metric="Modularity")

cb = CommunityBenchmark(graph=G, iterations=100)
dfb = cb.run(algorithms=algorithms)
cb.plot_all()