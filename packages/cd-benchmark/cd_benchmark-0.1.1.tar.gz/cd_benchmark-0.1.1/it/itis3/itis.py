from cd_benchmark.analysis import CommunityAnalysis
from cd_benchmark.benchmark import CommunityBenchmark
from cd_benchmark.generator import GraphGenerator
from cd_benchmark.visualization import GraphVisualizer
from networkx.generators.community import LFR_benchmark_graph
import math, networkx as nx

def make_lfr(
    n: int,
    tau1: float = 2.5,
    tau2: float = 1.5,
    mu: float = 0.1,
    min_degree: int = 10,
    max_degree: int = 30,
    min_community: int = 20,
    max_community: int = 40,
    seed: int = 11,
    max_iters: int = 100000
):
    # varna spodnja meja velikosti skupnosti glede na max_degree in mu
    min_comm_safe = math.ceil((1 - mu) * max_degree) + 1
    if min_community < min_comm_safe:
        # posodobi min_community, da generator ne pade
        min_community = min_comm_safe

    G = nx.LFR_benchmark_graph(
        n=n,
        tau1=tau1, tau2=tau2, mu=mu,
        min_degree=min_degree, max_degree=max_degree,
        min_community=min_community, max_community=max_community,
        max_iters=max_iters, seed=seed
    )
    return G

G = make_lfr(
    n=10000, tau1=2.5, tau2=1.5, mu=0.2,
    min_degree=20, max_degree=80,
    min_community=100, max_community=300, seed=15,
    max_iters=300000
)

#viz = GraphVisualizer(G)
#viz.draw_graph("Graph G", node_color="lightblue", with_labels=False, node_size=5)

ca = CommunityAnalysis(graph=G)

algorithms = ["Louvain", "Leiden", "Infomap", "Label Propagation", "Fast Label Propagation", "Walktrap"]
df = ca.run(algorithms=algorithms)

cb = CommunityBenchmark(graph=G, iterations=100)
dfb = cb.run(algorithms=algorithms)
cb.plot_all()