""" resolve import relationship among modules """
# imports
import os
import ast as builtin_ast
from pathlib import Path
from typing import List, Set

# local imports
from phy_imports_resolver.types import (
    SEARCH_FOR_SUFFIXES, 
    Module, 
    ModuleFile, 
    ModulePackage, 
    ModuleImportsNode, 
    FileModuleImportsNode, 
    PackageModuleImportsNode
)


class ImportResolver:
    """ resolve importing chain from given entry code file, searching within given project path """

    # instance attributes
    project_dir: Path
    resolved_mod: Set[Module]  # avoid circular imports

    def __init__(self, project_dir: Path = None):
        """ Init resolver with project directory. 
        
        Project is the directory that look for python modules, it is usually the current work directory. 
        """
        if project_dir is None:
            project_dir = Path.cwd()

        # validate
        project_dir = project_dir.resolve()
        if not (project_dir.exists() and project_dir.is_dir()):
            raise FileNotFoundError(str(project_dir))

        self.project_dir = project_dir
        self.resolved_mod = set()

    def start(self, entry_file: Path) -> FileModuleImportsNode | None:
        """ entry file to start resolving """
        # clear resolved
        self.resolved_mod = set()

        # name of entry module
        entry_file = entry_file.resolve()

        if entry_file.stem != '__init__':  # file module
            mod_file = ModuleFile.create_or_err(name=entry_file.stem, path=entry_file)
            return self._resolve_mod_file(mod_file)  # type: ignore[arg-type]
        
        else:  # package module
            pkg_dir = entry_file.parent.resolve()
            mod_pkg = ModulePackage.create_or_err(name=pkg_dir.stem, path=pkg_dir)
            return self._resolve_mod_pkg(mod_pkg)  # type: ignore[arg-type, return-value]

    def _resolve_mod_file(self, mod_file: ModuleFile, **kwargs) -> FileModuleImportsNode | None:
        """ resolve imports of specified module of file """
        if mod_file in self.resolved_mod:
            return None
        
        # create node with imports un-resolved
        mod_file_imports_node = FileModuleImportsNode(
            mod=mod_file, 
            project_dir=self.project_dir, 
            code=kwargs.get('code')
        )
        self.resolved_mod.add(mod_file)

        for _import_union_ast in mod_file.extract_import_ast():
            if isinstance(_import_union_ast, builtin_ast.Import):
                mod_file_imports_node.imports += self._resolve_import_ast(_import_union_ast, mod_file)

            elif isinstance(_import_union_ast, builtin_ast.ImportFrom):
                mod_file_imports_node.imports += self._resolve_import_from_ast(_import_union_ast, mod_file)

            else:
                raise TypeError  # never occurs
        
        return mod_file_imports_node
    
    def _resolve_mod_pkg(self, mod_pkg: ModulePackage, **kwargs) -> PackageModuleImportsNode | None:
        """ Resolve imports of specified module of package. 
        
        The imports of package module is considered as those of its dunder init file. If the package is native namespace 
        package, it is the submodule that should not be resolved instead of the super package.
        """
        if mod_pkg in self.resolved_mod:
            return None

        if init_mod_file := mod_pkg.dunder_init_mod_file:
            # use package name as its dunder init file module name
            if init_mod_file in self.resolved_mod:
                return None

            mod_pkg_imports_node = PackageModuleImportsNode(
                mod=mod_pkg,
                project_dir=self.project_dir,
                code=kwargs.get('code')
            )
            self.resolved_mod.add(mod_pkg_imports_node)  # type: ignore[arg-type]

            init_mod_file_imports_node = self._resolve_mod_file(init_mod_file, code=kwargs.get('code'))
            mod_pkg_imports_node.imports = init_mod_file_imports_node.imports
            return mod_pkg_imports_node
            
        raise FileNotFoundError(str(mod_pkg.path / '__init__.*'))
    
    def _resolve_import_ast(
        self, 
        import_ast: builtin_ast.Import, 
        mod_file: ModuleFile,
        **kwargs
    ) -> List[ModuleImportsNode]:
        """ 'import' ','.dotted_as_name+ """
        _ = kwargs
        _code = builtin_ast.unparse(builtin_ast.fix_missing_locations(import_ast))
        print(f'Start resolve import statemenet: "{_code}" of "{mod_file.path}".')

        mod_imports_node_list: List[ModuleImportsNode] = []

        # "import . <as ...>" & "import .<submod> <as...>" are illegal syntax, so in this case no need to care about
        # resolving dot operator.
        for import_name_ast in import_ast.names:
            # dotted_name: dotted_name '.' NAME | NAME
            import_name = import_name_ast.name

            if mod_imports_node := self._resolve_import_name(import_name, code=_code):
                mod_imports_node_list.append(mod_imports_node)

        return mod_imports_node_list
    
    def _resolve_import_from_ast(
        self, 
        import_from_ast: builtin_ast.ImportFrom, 
        mod_file: ModuleFile,
        **kwargs
    ) -> List[ModuleImportsNode]:
        """ import_from:
            | 'from' ('.' | '...')* dotted_name 'import' import_from_targets 
            | 'from' ('.' | '...')+ 'import' import_from_targets 
        """
        _ = kwargs
        _code = builtin_ast.unparse(builtin_ast.fix_missing_locations(import_from_ast))
        print(f'Start resolve import statemenet: "{_code}" of "{mod_file.path}".')

        mod_imports_node_list: List[ModuleImportsNode] = []
        from_level = import_from_ast.level

        # level > 0 : relative imports; need to get absolute mod path by resolving level
        if from_level:
            mod_path = mod_file.path
            while from_level:
                mod_path = mod_path.parent
                from_level -= 1
                
        # level = 0: 'from' dotted_name 'import' import_from_targets
        else:
            mod_path = self.project_dir

        # "<ast.ImportForm>.module is None" means "from .|.. import", not "from .|..<submod> import"
        if import_from_ast.module:
            import_path = import_from_ast.module.replace('.', os.sep)
            mod_path = mod_path / import_path

        # from module is package
        abs_import_path = mod_path.resolve()
        import_name = abs_import_path.stem

        if mod_pkg := ModulePackage.create_or_null(name=import_name, path=abs_import_path):
            # if `__init__.*` exists, firstly resolve the `__init__.*` file
            if mod_pkg.dunder_init_mod_file:
                if mod_imports_node := self._resolve_mod_pkg(mod_pkg, code=_code):
                    mod_imports_node_list.append(mod_imports_node)

            # resolve submodules
            for import_sub_name_ast in import_from_ast.names:
                import_sub_name = import_sub_name_ast.name

                # in case of format "from ... import *"
                if import_sub_name == '*':
                    continue

                # submodule 
                if submod_file := mod_pkg.get_submod_file(import_sub_name):
                    if mod_imports_node := self._resolve_mod_file(submod_file, code=_code):  # type: ignore[assignment]
                        mod_imports_node_list.append(mod_imports_node)

                if submod_pkg := mod_pkg.get_submod_pkg(import_sub_name):
                    if mod_imports_node := self._resolve_mod_pkg(submod_pkg, code=_code):
                        mod_imports_node_list.append(mod_imports_node)
        
        # from module is file
        for _suffix in SEARCH_FOR_SUFFIXES:
            abs_import_path = abs_import_path.with_suffix(_suffix).resolve()
            if mod_file := ModuleFile.create_or_null(name=import_name, path=abs_import_path):  # type: ignore[assignment]
                if mod_imports_node := self._resolve_mod_file(mod_file, code=_code):  # type: ignore[assignment]
                    mod_imports_node_list.append(mod_imports_node)
            
        return mod_imports_node_list
    
    def _resolve_import_name(self, import_name: str, **kwargs) -> ModuleImportsNode | None:
        """ Resolve import name for path of file module or package. 

        Import name should be absolute, no relative symbol '.' or '..' is allowed.
        """
        # assert relative import name has been resolved
        assert not import_name.startswith('.')

        # dotted_name '.' NAME | NAME
        import_path = import_name.replace('.', os.sep)

        # imported is package
        abs_import_path = (self.project_dir / import_path).resolve()
        import_name = abs_import_path.stem

        if mod_pkg := ModulePackage.create_or_null(name=import_name, path=abs_import_path):
            return self._resolve_mod_pkg(mod_pkg, code=kwargs.get('code'))
        
        # imported is file
        for _suffix in SEARCH_FOR_SUFFIXES:
            abs_import_path = abs_import_path.with_suffix(_suffix).resolve()
            if mod_file := ModuleFile.create_or_null(name=import_name, path=abs_import_path):
                return self._resolve_mod_file(mod_file, code=kwargs.get('code'))

        # builtin module or site-packages
        return None
