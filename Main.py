from logicGateSimulator import *
from node import *

# Create simulator instance
simulator = LogicCircuitSimulator()

# Your logic expression
expression = "A AND B OR NOT (C AND E)"

# Process the expression
parsed = simulator.parse_expression(expression)
rpn = simulator.change_to_rpn(parsed)
expression_tree = simulator.build_expression_tree(rpn)

# Generate truth table
simulator.generate_truth_table(expression_tree)

# Visualize the circuit
simulator.visualize_circuit(expression_tree)