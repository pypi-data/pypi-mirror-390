""" extract import ast node from code """
# imports
from pathlib import Path
import ast as builtin_ast
import token as builtin_token
import tokenize as builtin_tokenize
from typing import List, Union


# TODO: use `phy-core` ast node
_AstNode = builtin_ast.AST

ImportUnionAst = Union[builtin_ast.Import, builtin_ast.ImportFrom]


# TODO: use `phy-core` parser
class _Parser:
    
    def parse(self, file: Path) -> _AstNode:
        """ parse code file as ast root node """
        # get file encoding by builtin tokenizer
        _encoding = 'utf-8'  # default encoding
        with builtin_tokenize.open(file) as _f:
            for _tok in builtin_tokenize.generate_tokens(_f.readline):
                if _tok.type == builtin_token.ENCODING:
                    _encoding = _tok.string
                break  # encoding token is placed first or omitted
        
        # parse code file
        with file.open('r', encoding=_encoding) as _f:
            return builtin_ast.parse(_f.read(), filename=str(file))


# TODO: use `phy-core` visitor
class _ImportAstVisitor(builtin_ast.NodeVisitor):

    # instance attributes
    imported_ast_nodes: List[ImportUnionAst]

    def __init__(self):
        """ constructor """
        super().__init__()
        self.imported_ast_nodes = []

    def visit_Import(self, node):
        """ override `visit_Import` method """
        self.imported_ast_nodes.append(node)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """ override `visit_ImportFrom` method """
        self.imported_ast_nodes.append(node)
        self.generic_visit(node)


def extract_import_ast_nodes(file: Path) -> List[ImportUnionAst]:
    """ extract import ast node from code """
    parser = _Parser()
    ast_root = parser.parse(file)
    
    visitor = _ImportAstVisitor()
    visitor.visit(ast_root)
    return visitor.imported_ast_nodes
