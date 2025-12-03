import tkinter as tk
from tkinter import Canvas
from node import *

class LogicCircuitSimulator:
    def __init__(self):
        self.variables = set()

    @staticmethod
    def tokenize(expression):
        # Split expression into tokens
        # Remove extra spaces
        expression = expression.replace('(', ' ( ')
        expression = expression.replace(')', ' ) ')
        tokens = expression.split()
        return tokens

    def parse_expression(self, expression):
        expression = expression.replace(" ", "").upper()

        # Add spaces around operators for tokenization
        expression_modified = expression.replace("AND", " AND ")
        expression_modified = expression_modified.replace("OR", " OR ")
        expression_modified = expression_modified.replace("NOT", " NOT ")

        # Tokenize and find variables
        tokens = self.tokenize(expression_modified)
        for token in tokens:
            # If it's alphabetic and NOT an operator or parenthesis, it's a variable
            if token.isalpha() and token not in ['AND', 'OR', 'NOT']:
                self.variables.add(token)

        return expression_modified

    def change_to_rpn(self, expression):
        precedence = {
            "NOT" : 3,
            "AND" : 2,
            "OR" : 1
        }
        output = []
        operator_stack = []

        tokens = self.tokenize(expression)

        for token in tokens:
            if token not in ['AND', 'OR', 'NOT', '(', ')']: # token is a variable
                output.append(token)
            elif token in ['AND', 'OR', 'NOT']:
                while operator_stack and operator_stack[-1] != '(' and operator_stack[-1] in precedence and precedence[operator_stack[-1]] >= precedence[token]:
                    output.append(operator_stack.pop())
                operator_stack.append(token)
            elif token == '(':
                operator_stack.append(token)
            elif token == ')':
                while operator_stack and operator_stack[-1] != '(':
                    output.append(operator_stack.pop())
                operator_stack.pop()
        while operator_stack:
            output.append(operator_stack.pop())
        return output

    @staticmethod
    def build_expression_tree(rpn_tokens):
        #Build th expression tree from RPN tokens using a stack
        stack = []

        for token in rpn_tokens:
            if token == 'AND' or token == 'OR':
                # Binary operators need 2 inputs
                right = stack.pop()
                left = stack.pop()

                # Create gate node with both children
                node = ExpressionNode('GATE', token, left, right)
                stack.append(node)

            elif token == 'NOT':
                # needs 1 input
                negate = stack.pop()

                # Create NOT gate with only left child
                node = ExpressionNode('GATE', token, negate, None)
                stack.append(node)

            else:
                # variable
                node = ExpressionNode('VAR', token)
                stack.append(node)
        return stack[0]

    def evaluate_tree(self, node, variable_values):
        # Evaluate the expression tree with given variable values
        if node.type == 'VAR':
            return variable_values[node.value]
        elif node.type == 'GATE':
            if node.value == 'NOT':
                return not self.evaluate_tree(node.left, variable_values)
            elif node.value == 'AND':
                return self.evaluate_tree(node.left, variable_values) and self.evaluate_tree(node.right, variable_values)
            elif node.value == 'OR':
                return self.evaluate_tree(node.left, variable_values) or self.evaluate_tree(node.right, variable_values)
        return None

    def generate_truth_table(self, expression_tree):
        n = len(self.variables)
        num_of_rows = 2 ** n
        num_of_columns = n

        # Create empty table
        truth_table = [[0 for _ in range(num_of_columns)] for _ in range(num_of_rows)]

        # Fill each column
        for col in range(num_of_columns):
            alternation_period = (2 ** n) // (2 ** (col + 1))
            current_value = 1

            for row in range(num_of_rows):
                if row > 0 and row % alternation_period == 0:
                    current_value = 1 - current_value  # change between 0 and 1
                truth_table[row][col] = current_value

        # Print headings
        variables_list = sorted(list(self.variables))
        print(" | ".join(variables_list) + " | Output")

        # Print each row of the truth table with output
        for row in truth_table:
            # Create dictionary mapping variable names to their values
            variable_values = {var: row[i] for i, var in enumerate(variables_list)}

            # Evaluate the expression
            output = int(self.evaluate_tree(expression_tree, variable_values))

            print(" | ".join(str(val) for val in row) + " | " + str(output))

    @staticmethod
    def visualize_circuit(expression_tree):
        # Simple circuit visualization with proper gate shapes
        root = tk.Tk()
        root.title("Logic Circuit Visualization")
        canvas = Canvas(root, width=1000, height=700, bg='white')
        canvas.pack()

        # Title
        canvas.create_text(500, 30, text="Logic Circuit Diagram", font=('Arial', 18, 'bold'), fill='darkblue')

        # Draw proper gate shapes
        def draw_and_gate(x, y):
            # Rectangle part
            canvas.create_rectangle(x, y, x + 40, y + 40, fill='lightblue', outline='black', width=2)
            # Curved part
            canvas.create_arc(x + 20, y, x + 60, y + 40, start=270, extent=180, fill='lightblue', outline='black', width=2)
            # text
            canvas.create_text(x + 20, y + 20, text="AND", font=('Arial', 10, 'bold'))
            return x + 60, y + 20

        def draw_or_gate(x, y):
            # OR gate
            points = [x, y, x + 20, y, x + 50, y + 20, x + 20, y + 40, x, y + 40, x + 15, y + 20]
            canvas.create_polygon(points, fill='lightgreen', outline='black', smooth=True, width=2)
            canvas.create_text(x + 25, y + 20, text="OR", font=('Arial', 10, 'bold'))
            return x + 50, y + 20

        def draw_not_gate(x, y):
            # NOT gate
            # Triangle part
            points = [x, y, x, y + 30, x + 30, y + 15]
            canvas.create_polygon(points, fill='lightyellow', outline='black', width=2)

            # Small circle at the tip
            canvas.create_oval(x + 30, y + 10, x + 40, y + 20, fill='white', outline='black', width=2)
            canvas.create_text(x + 15, y + 15, text="NOT", font=('Arial', 8, 'bold'))
            return x + 40, y + 15

        def draw_input(x, y, name):
            # Draw input variable as a circle
            canvas.create_oval(x, y, x + 40, y + 40, fill='lightcoral', outline='black', width=2)
            canvas.create_text(x + 20, y + 20, text=name, font=('Arial', 12, 'bold'))
            return x + 40, y + 20

        def draw_circuit(node, x, y):
            # Recursively draw the circuit
            if node is None:
                return None, None

            # Base case: input
            if node.type == 'VAR':
                return draw_input(x, y, node.value)

            # Recursive case: gate
            input_x = x - 150

            if node.value == 'NOT':
                child_out_x, child_out_y = draw_circuit(node.left, input_x, y)
                gate_out_x, gate_out_y = draw_not_gate(x, y - 15)
                if child_out_x:
                    canvas.create_line(child_out_x, child_out_y, x, gate_out_y, width=2)
                return gate_out_x, gate_out_y

            elif node.value == 'AND':
                left_out_x, left_out_y = draw_circuit(node.left, input_x, y - 60)
                right_out_x, right_out_y = draw_circuit(node.right, input_x, y + 20)
                gate_out_x, gate_out_y = draw_and_gate(x, y - 20)
                if left_out_x:
                    canvas.create_line(left_out_x, left_out_y, x, y - 10, width=2)
                if right_out_x:
                    canvas.create_line(right_out_x, right_out_y, x, y + 10, width=2)
                return gate_out_x, gate_out_y

            elif node.value == 'OR':
                left_out_x, left_out_y = draw_circuit(node.left, input_x, y - 60)
                right_out_x, right_out_y = draw_circuit(node.right, input_x, y + 20)
                gate_out_x, gate_out_y = draw_or_gate(x, y - 20)
                if left_out_x:
                    canvas.create_line(left_out_x, left_out_y, x, y - 10, width=2)
                if right_out_x:
                    canvas.create_line(right_out_x, right_out_y, x, y + 10, width=2)
                return gate_out_x, gate_out_y

        # Start drawing from center
        out_x, out_y = draw_circuit(expression_tree, 700, 350)

        if out_x:
            # Draw output label
            canvas.create_line(out_x, out_y, out_x + 100, out_y, width=2, fill='blue')
            canvas.create_text(out_x + 150, out_y, text="OUTPUT", font=('Arial', 14, 'bold'), fill='blue')

        root.mainloop()

    def run(self):
        # Main interface
        expression = input("Enter logic expression: ")

        try:
            parsed = self.parse_expression(expression)
            rpn = self.change_to_rpn(parsed)
            expression_tree = self.build_expression_tree(rpn)
            if expression_tree is None:
                raise ValueError("Invalid expression")
        except:
            print("\n❌ Invalid expression! Please check your syntax.")
            expression = input("Enter logic expression: ")

        parsed = self.parse_expression(expression)
        rpn = self.change_to_rpn(parsed)
        expression_tree = self.build_expression_tree(rpn)

        while True:
            print("\n1. Show truth table")
            print("2. Visualize circuit")
            print("3. Exit")

            choice = input("\nChoice: ")

            if choice == '1':
                self.generate_truth_table(expression_tree)
            elif choice == '2':
                self.visualize_circuit(expression_tree)
            elif choice == '3':
                return