import ast
import operator as op

# supported operators
operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
             ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor}


class rewiredBotPlugin():
    def __init__(self, *args):
        self.defines = "!calc"
        self.privs = {'!calc': 1}

    def run(*args):
        print args[1]
        try:
            result = eval_expr(args[1])
        except:
            return 0
        if result != None:
            if not result:
                return '0 '
            return str(result)
        return 0


def eval_expr(expr):
    return eval_(ast.parse(expr).body[0].value)


def eval_(node):
    if isinstance(node, ast.Num):  # <number>
        return node.n
    elif isinstance(node, ast.operator):  # <operator>
        return operators[type(node)]
    elif isinstance(node, ast.BinOp):  # <left> <operator> <right>
        return eval_(node.op)(eval_(node.left), eval_(node.right))
    else:
        return None
