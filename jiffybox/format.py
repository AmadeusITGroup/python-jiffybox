from visitor import Visitor


class PlainFormatVisitor(Visitor):
    def __init__(self):
        self.indent = 0

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
            buf = ''
            if hasattr(node, 'name'):
                buf += node.name
            if hasattr(node, 'id'):
                buf += '({})'.format(node.id)
            obj_dict = dict(
                (attr, getattr(node, attr))
                for attr in node._attributes.keys()
            )
            buf += self.visit(obj_dict)
            return buf
        return str(node)
