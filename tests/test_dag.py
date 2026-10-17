from atlas_runtime import dag

def test_dag_basic():
    d = dag.DAGScheduler()
    d.add_node("a", tokens=10)
    d.add_node("b", tokens=20, deps=["a"])
    d.add_edge("a", "b")
    ready = d.ready_nodes()
    assert "a" in ready
