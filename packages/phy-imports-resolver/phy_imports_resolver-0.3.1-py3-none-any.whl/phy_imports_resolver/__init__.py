""" Resolve imports of a python file or module, exclude site packages & builtin modules. """
__version__ = "0.3.1"
__all__ = [
    'resolve',
    'FileModuleImportsNode',
    'PackageModuleImportsNode',
]

# imports
from pathlib import Path

# local imports
from phy_imports_resolver.resolver import ImportResolver
from phy_imports_resolver.types import FileModuleImportsNode, PackageModuleImportsNode


def resolve(entry_file: Path, project_dir: Path = None) -> FileModuleImportsNode | None:
    """ Resolve imports from entry code file, within given search directory. If no search directory is 
    given, current work directory is used.
    """
    resolver = ImportResolver(project_dir=project_dir)

    entry_file_path = Path(entry_file).resolve()
    return resolver.start(entry_file_path)
