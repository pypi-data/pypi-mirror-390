import sys
from brick_tq_shacl import infer, validate
from ontoenv import OntoEnv
from rdflib import Graph
env = OntoEnv(
    offline=False,
    no_search=True,
)
data = Graph()
data.parse(sys.argv[1], format="ttl")

shapes = Graph()
shapes.parse("Brick.ttl")
imported = env.import_dependencies(shapes, fetch_missing=True)
print(f"Imported shapes: {imported}")
shapes.serialize("shapes.ttl")

data = infer(data, shapes, min_iterations=1, max_iterations=100, early_isomorphic_exit=True)
data.serialize("post-infer.ttl")

valid, rgr, rstr = validate(data, shapes, min_iterations=1, max_iterations=100, early_isomorphic_exit=True)
print(f"Result string: {rstr}")
print(f"Valid: {valid}")
#print(f"Result graph: {rgr.serialize(format='turtle')}")

