""" cli app by `click` """
# imports
from pathlib import Path

# import optional dependencies
try:
    import click
    from graphviz import Digraph

except ImportError as err:
    raise SystemExit(
        'The CLI requires extra dependencies. ' +
        'Please install with `pip install phy-imports-resolver[cli]`.'
    ) from err

# local imports
from phy_imports_resolver.types import ModuleImportsNode
from phy_imports_resolver import ImportResolver


def _add_children_to_diagram(
        diagram: Digraph, 
        node: ModuleImportsNode, 
        parent_node: ModuleImportsNode = None
    ) -> None:
    """ recursively add imported modules to diagram """
    diagram.node(str(id(node)), node.name, shape='box')
    if parent_node is not None:
        diagram.edge(str(id(parent_node)), str(id(node)))
    for _child in node.imports:
        _add_children_to_diagram(diagram, _child, node)


def _mod_imports_node_to_diagram(mod_imports_node: ModuleImportsNode, output_path: Path, fmt: str = 'png') -> Digraph:
    """ generate `graphviz` diagram by module imports tree """
    diagram = Digraph(comment=mod_imports_node.name, format=fmt)
    diagram.attr('node', shape='box')
    diagram.attr(rankdir='TB')  # layout: from top to bottom

    _add_children_to_diagram(diagram, mod_imports_node)
    diagram.render(output_path.with_suffix(''), view=True)  # graphviz will add `fmt` as suffix
    print(f'Diagram image saved to {output_path}.')


@click.command(name='resolve-imports')
@click.argument(
    'file', 
    type=click.Path(exists=True)
)
@click.option(
    '--format',
    '-f',
    'output_format',
    type=click.Choice(['xml', 'png', 'svg'], case_sensitive=False),
    default='xml',
    show_default=True,
    help='Specify the output format',
)
@click.option(
    '--output',
    '-o',
    default=None,
    type=click.Path(),
    help='Optional output file path.',
)
def cli_app(file: str, output_format: str, output: str):
    """ Resolve the imports of a python file or module, recursively.
    
    FILE: path to the entry code file.
    """
    project_dir = Path.cwd().resolve()
    resolver = ImportResolver(project_dir=project_dir)

    entry_file_path = Path(file).resolve()
    resolved_node = resolver.start(entry_file_path)

    # if no output specified, print xml to stdout
    resolved_tree_repr = str(resolved_node)
    if output is None:
        click.echo(resolved_tree_repr)

    # if output specified, output to file
    else:
        output_path = Path(output).resolve()
        # output to xml
        if output_format == 'xml':
            with open(output_path, 'w', encoding='utf8') as _f:
                _f.write(resolved_tree_repr)

        # output to diagram with `graphviz`
        elif output_format in ('png', 'svg'):
            _mod_imports_node_to_diagram(resolved_node, output_path, fmt=output_format)

        else:
            raise NotImplementedError


def main():
    """ expose method entry to `pyproject.toml` script spec """
    # this is click command; pylint: disable=no-value-for-parameter
    cli_app()
