""" types to describe import relationship among modules """
# imports
from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET
from typing import List, Tuple, Optional

# local imports
from phy_imports_resolver._extractor import extract_import_ast_nodes, ImportUnionAst


# constants

# Search for python code file with these file suffixes by module name. 
# TODO: replace to ('.phy', ) when release
SEARCH_FOR_SUFFIXES: Tuple[str, ...] = ('.py', '.pyi')


@dataclass
class Module:
    """ Like builtin `module` object but in parsing time instead of runtime. """
    name: str
    path: Path

    # define `__eq__` & `__hash__` to use `set` collection of this class
    def __eq__(self, other: 'Module') -> bool:  # type: ignore[override]
        if not isinstance(other, Module):  # include subclasses
            return False
        return self.path.resolve() == other.path.resolve()
    
    def __hash__(self):
        return hash(str(self.path.resolve()))


@dataclass
class ModuleFile(Module):
    """ module as single file, with file name the same as module name """

    def extract_import_ast(self) -> List[ImportUnionAst]:
        """ extract import ast node from module file """
        return extract_import_ast_nodes(self.path)
    
    @classmethod
    def create_or_null(cls, name: str, path: Path) -> Optional['ModuleFile']:
        """ validate before create instance; if failed, return None """
        if path.exists() and path.is_file():
            return cls(name=name, path=path)
        return None
    
    @classmethod
    def create_or_err(cls, name: str, path: Path) -> Optional['ModuleFile']:
        """ validate before create instance; if failed, raise error """
        if path.exists() and path.is_file():
            return cls(name=name, path=path)
        raise FileNotFoundError(str(path))
    
    # define `__eq__` & `__hash__` to use `set` collection of this class
    def __eq__(self, other: 'ModuleFile') -> bool:  # type: ignore[override]
        if not isinstance(other, ModuleFile):  # include subclasses
            return False
        return self.path.resolve() == other.path.resolve()
    
    def __hash__(self):
        return hash((
            self.__class__.__name__, 
            str(self.path.resolve())
        ))


@dataclass
class ModulePackage(Module):
    """ Module as packages, with folder name the same as module name and a `__init__` file.
    
    Notice that builtin `module.__path__` is a list instead of single file, intended to be designed 
    for `native namespace package`, which is not unnessary to take into account here for different native 
    namesapce packages cannot coexists in same project folder.
    """
    def get_submod(self, submod_name: str) -> Optional[Module]:
        """ find submodule of the package """
        if submod_file := self.get_submod_file(submod_name):
            return submod_file
        if submod_pkg := self.get_submod_pkg(submod_name):
            return submod_pkg
        return None

    def get_submod_file(self, submod_name: str) -> Optional[ModuleFile]:
        """ find file submodule of the package """
        for _suffix in SEARCH_FOR_SUFFIXES:
            submod_path = self.path / (submod_name + _suffix)
            if submod_file := ModuleFile.create_or_null(name=submod_name, path=submod_path):
                return submod_file
        return None

    def get_submod_pkg(self, submod_name: str) -> Optional['ModulePackage']:
        """ find package submodule of the package """
        submod_path = self.path / submod_name
        return ModulePackage.create_or_null(name=submod_name, path=submod_path)

    @property
    def dunder_init_mod_file(self) -> Optional[ModuleFile]:
        """ `__init__.*` file of the package """
        for _suffix in SEARCH_FOR_SUFFIXES:
            dunder_init_path = self.path / ('__init__' + _suffix)
            # use package name as mod file name
            if dunder_init_file := ModuleFile.create_or_null(name=self.name, path=dunder_init_path):
                return  dunder_init_file
        
        # dunder init file may not exists in cases of `native namespace package`
        return None
    
    @property
    def is_native_namespace(self) -> bool:
        """ dunder init file may not exists when self is `native namespace package` """
        return self.dunder_init_mod_file is None
    
    @classmethod
    def create_or_null(cls, name: str, path: Path) -> Optional['ModulePackage']:
        """ validate before create instance; if failed, return None """
        if path.exists() and path.is_dir():
            return cls(name=name, path=path)
        return None
    
    @classmethod
    def create_or_err(cls, name: str, path: Path) -> Optional['ModulePackage']:
        """ validate before create instance; if failed, raise error """
        if path.exists() and path.is_dir():
            return cls(name=name, path=path)
        raise FileNotFoundError(str(path))
    
    # define `__eq__` & `__hash__` to use `set` collection of this class
    def __eq__(self, other: 'ModulePackage') -> bool:  # type: ignore[override]
        if not isinstance(other, ModulePackage):  # include subclasses
            return False
        return self.path.resolve() == other.path.resolve()
    
    def __hash__(self):
        return hash((
            self.__class__.__name__, 
            str(self.path.resolve())
        ))


class ModuleImportsNode:
    """ module with dependent imports info """

    # instance attributes
    mod: Module
    project_dir: Path
    imports: List['ModuleImportsNode']  # DO NOT use `Self` for it is introduced until 3.11

    code: Optional[str]  # import statement code

    def __init__(
        self, 
        mod: Module, 
        project_dir: Path, 
        imports: List['ModuleImportsNode'] = None, 
        **kwargs
    ):
        """ constructor """
        self.mod = mod
        self.imports = imports if imports is not None else []

        # Project is the directory that look for python modules, it is usually the current work directory.
        # It is essential for resolving imports; if imported module is outside of the project directory, it 
        # will not be resolved and be regarded as site-packages.
        self.project_dir = project_dir.resolve()

        # extra attributes
        self.code = kwargs.get('code')

    @property
    def name(self) -> str:
        """ getter of `name` """
        return self.mod.name
    
    @property
    def path(self) -> Path:
        """ getter of `path` """
        return self.mod.path

    def repr_element(self) -> ET.Element:
        """ represent the ast node as xml-like node """
        # use relative path to project directory to simplify the output
        simplified_path = self.path.relative_to(self.project_dir)
        root = ET.Element('module', name=self.name, path=str(simplified_path))

        if self.code:
            root.set('code', self.code)
        
        if self.imports:
            imports_et = ET.Element('imports')
            for import_node in self.imports:
                imports_et.append(import_node.repr_element())
            root.append(imports_et)

        return root
    
    def __repr__(self) -> str:
        """ print element tree with indent xml-like format """
        root = self.repr_element()
        ET.indent(root, space=' ' * 2, level=0)
        return ET.tostring(root, encoding='unicode', method='xml')
    
    def __str__(self) -> str:
        return self.__repr__()


class FileModuleImportsNode(ModuleImportsNode):
    """ module of single file with dependent imports info """
    mod: ModuleFile

    def repr_element(self) -> ET.Element:
        root = super().repr_element()
        root.tag = 'file'
        return root


class PackageModuleImportsNode(ModuleImportsNode):
    """ module of package with dependent imports info """
    mod: ModulePackage

    def repr_element(self) -> ET.Element:
        root = super().repr_element()
        root.tag = 'package'
        return root
