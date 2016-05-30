import pkg_resources

from docutils.nodes import literal_block
from sphinx.domains import Domain
from sphinx.util.compat import Directive

import click


def generate_help_texts(command, prefix):
    ctx = click.Context(command)
    yield make_block(
        ' '.join(prefix),
        command.get_help_option(ctx).opts[0],
        command.get_help(ctx),
    )

    if isinstance(command, click.core.Group):
        for c in command.list_commands(ctx):
            c = command.resolve_command(ctx, [c])[1]
            prefix.append(c.name)
            for h in generate_help_texts(c, prefix):
                yield h
            prefix.pop()


def find_script_callable(name):
    return list(pkg_resources.iter_entry_points(
        'console_scripts', name))[0].load()


def make_block(command, opt, content):
    h = "$ {} {}\n".format(command, opt) + content
    return literal_block(h, h, language='bash')


class ClickHelpDirective(Directive):
    has_content = True
    required_arguments = 1

    def run(self):
        root_cmd = self.arguments[0]
        group = find_script_callable(root_cmd)
        return list(generate_help_texts(group, [root_cmd]))


class JiffyBoxDomain(Domain):
    name = 'jiffybox'
    label = 'JiffyBox'
    directives = {
        'click-help': ClickHelpDirective,
    }


def setup(app):
    app.add_domain(JiffyBoxDomain)
