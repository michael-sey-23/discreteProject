class ExpressionNode:
    def __init__(self, node_type, value=None, left=None, right=None):
        self.type = node_type    # 'GATE' or 'VAR'
        self.value = value        # Gate type (AND/OR/NOT) or variable name
        self.left = left          # Left child node
        self.right = right        # Right child node