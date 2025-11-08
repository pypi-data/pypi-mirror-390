from brick_tq_shacl import infer, validate
from ontoenv import OntoEnv
from rdflib import Graph
env = OntoEnv(offline=True)
data = Graph()
data.parse("nist-bdg1-1.ttl", format="ttl")

shapes = Graph()
shapes.parse("223p.ttl")
imported = env.import_dependencies(shapes, fetch_missing=True, recursion_depth=2)
print(f"Imported {len(imported)} shapes dependencies.")
for g in imported:
    print(g)
shapes.serialize("shapes.ttl")

data = infer(data, shapes, min_iterations=5, max_iterations=100, early_isomorphic_exit=True)
data.serialize("post-infer.ttl")

valid, rgr, rstr = validate(data, shapes, min_iterations=5, max_iterations=100, early_isomorphic_exit=True)
print(f"Result string: {rstr}")
print(f"Valid: {valid}")
#print(f"Result graph: {rgr.serialize(format='turtle')}")
