"""Dependency graph with provenance labels for sourced links vs assumptions."""
import networkx as nx

def build_graph(commodity: str, partner_shares: list[dict]) -> dict:
    labels = {
        "crude_oil": ("Crude oil", ["Refining", "Transport", "Petrochemicals", "Fertilizers"]),
        "copper": ("Refined copper", ["Electrical equipment", "Construction", "Electronics", "Renewable energy"]),
        "fertilizers": ("Fertilizers", ["Agriculture", "Food processing"]),
    }
    commodity_label, industries = labels.get(commodity, (commodity, []))
    g = nx.DiGraph()
    g.add_node(commodity, label=commodity_label, kind="commodity")
    for p in partner_shares[:6]:
        pid = "country_" + p["partner"].lower().replace(" ", "_")
        g.add_node(pid, label=p["partner"], kind="country")
        g.add_edge(pid, commodity, weight=p["share_pct"], relation="supplies (demo share)", provenance="synthetic_demo_data")
    for i, industry in enumerate(industries):
        iid = "industry_" + str(i)
        g.add_node(iid, label=industry, kind="industry")
        g.add_edge(commodity, iid, weight=None, relation="may be an input to", provenance="assumption_to_validate")
    return {
        "nodes": [{"id": n, **attrs} for n, attrs in g.nodes(data=True)],
        "edges": [{"source": u, "target": v, **attrs} for u, v, attrs in g.edges(data=True)],
        "note": "Partner edges use synthetic demo shares. Industry dependency edges are explicitly labelled assumptions, not verified causal claims."
    }

def dependency_path(commodity: str, industry: str, graph: dict) -> dict:
    nodes = {n["id"]: n for n in graph["nodes"]}
    target = next((n["id"] for n in graph["nodes"] if n["kind"] == "industry" and n["label"] == industry), None)
    if not target or commodity not in nodes:
        return {"found": False, "path": [], "message": "No documented path found."}
    return {"found": True, "path": [nodes[commodity]["label"], industry], "message": "Illustrative dependency path; industry link is an assumption requiring validation."}
