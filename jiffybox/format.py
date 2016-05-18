from visitor import Visitor


class PlainFormatVisitor(Visitor):
    def __init__(self):
        self.indent = 0

    def visit_Box(self, node):
        buf = "{}({}):".format(node.name, node.id)
        buf += self.visit_object(node)
        return buf

    def visit_dict(self, node):
        if not node:
            return ''
        buf = '\n'
        self.indent += 2
        parts = []
        for k, v in sorted(node.items()):
            parts.append(' ' * self.indent + '{}: {}'.format(k, self.visit(v)))
        self.indent -= 2

        return buf + '\n'.join(parts)

    def visit_list(self, node):
        return ', '.join(self.visit(child) for child in node)

    def visit_object(self, node):
        if hasattr(node, '_attributes'):
            obj_dict = {
                attr: getattr(node, attr)
                for attr in node._attributes.keys()
            }
            return self.visit(obj_dict)
        return str(node)
