from typing import List

import pytest

from pylgen.analysis.context import Context
from pylgen.analysis.visitor import ASTChildrenSelector,ASTVisitor,ASTWalker,TraversalStrategy
from pylgen.common.types import Symbol,AST

class CounterContext(Context):

    def __init__(self) -> None:
        super().__init__()
        self._asts = []

    @property
    def asts(self) -> List[AST]:
        return self._asts.copy()

    def add_ast(self,ast:AST):
        self._asts.append(ast)

class BinaryAST(AST):

    def __init__(self, left:AST, right:AST):
        super().__init__(Symbol('binary'), 0, 0)
        self._left = left
        self._right = right
    
    @property
    def left(self) -> AST:
        return self._left

    @property
    def right(self) -> AST:
        return self._right

    def children(self) -> List[AST]:
        return [self._left,self._right]
    
class AtomicAST(AST):

    def __init__(self):
        super().__init__(Symbol('atomic'), 0, 0)
    
    def children(self) -> List[AST]:
        return []

class CounterASTVisitor(ASTVisitor):

    def __init__(self) -> None:
        super().__init__(CounterContext)
    
    def visit(self, ast: AST, context: CounterContext) -> None: # type: ignore
        context.add_ast(ast)

class CounterChildrenSelector(ASTChildrenSelector):

    def __init__(self) -> None:
        super().__init__(CounterContext)
    
    def select_children(self, ast: AST, context: CounterContext) -> List[AST]: # type: ignore
        return ast.children()

class PostOrderTraversalStrategy(TraversalStrategy):

    def __init__(self) -> None:
        super().__init__(CounterContext)
        self._stack = []
        self._seen = []
    
    def init(self, root: AST) -> None:
        super().init(root)
        self._stack = [root]
    
    def has_next(self) -> bool:
        return len(self._stack) > 0
    
    def current(self, context: Context) -> AST:
        self._check_context_type(context)
        selector = self._get_selector(self._stack[-1])
        children = selector.select_children(self._stack[-1],context)
        seen = self._stack[-1] in self._seen
        while children and not seen:
            self._seen.append(self._stack[-1])
            children.reverse()
            for child in children:
                self._stack.append(child)
            selector = self._get_selector(self._stack[-1])
            children = selector.select_children(self._stack[-1],context)
            seen = self._stack[-1] in self._seen
        return self._stack.pop()
    
    def reset(self) -> None:
        self._seen.clear()
        self._stack.clear()

class PreOrderTraversalStrategy(TraversalStrategy):

    def __init__(self) -> None:
        super().__init__(CounterContext)
        self._stack = []
    
    def init(self, root: AST) -> None:
        self._stack.append(root)
    
    def has_next(self) -> bool:
        return len(self._stack) > 0
    
    def current(self, context: CounterContext) -> AST: # type: ignore
        self._check_context_type(context)
        ast = self._stack.pop(0)
        selector = self._get_selector(ast)
        self._stack += selector.select_children(ast,context)
        return ast
    
    def reset(self) -> None:
        self._stack.clear()

class TestIntegrationSemantic:

    @pytest.fixture
    def ast1(self) -> AST:
        left = AtomicAST()
        right = AtomicAST()
        return BinaryAST(left,right)

    def build_walker1(self,context:CounterContext) -> ASTWalker:
        
        strategy = PostOrderTraversalStrategy()
        selector = CounterChildrenSelector()
        strategy.add_selector(AtomicAST,selector)
        strategy.add_selector(BinaryAST,selector)
        walker = ASTWalker(context,strategy)
        visitor = CounterASTVisitor()
        walker.add_visitor(AtomicAST,visitor)
        walker.add_visitor(BinaryAST,visitor)
        return walker
    
    def build_walker2(self,context:CounterContext) -> ASTWalker:
        
        strategy = PreOrderTraversalStrategy()
        selector = CounterChildrenSelector()
        strategy.add_selector(AtomicAST,selector)
        strategy.add_selector(BinaryAST,selector)
        walker = ASTWalker(context,strategy)
        visitor = CounterASTVisitor()
        walker.add_visitor(AtomicAST,visitor)
        walker.add_visitor(BinaryAST,visitor)
        return walker

    def build_walker3(self,context:CounterContext) -> ASTWalker:
        
        strategy = PostOrderTraversalStrategy()
        selector = CounterChildrenSelector()
        strategy.set_default_selector(selector)
        walker = ASTWalker(context,strategy)
        visitor = CounterASTVisitor()
        walker.set_default_visitor(visitor)
        return walker

    def build_walker4(self,context:CounterContext) -> ASTWalker:
        
        strategy = PreOrderTraversalStrategy()
        selector = CounterChildrenSelector()
        strategy.set_default_selector(selector)
        walker = ASTWalker(context,strategy)
        visitor = CounterASTVisitor()
        walker.set_default_visitor(visitor)
        return walker

    def test_1(self,ast1:AST):

        context = CounterContext()
        walker = self.build_walker1(context)
        walker.walk(ast1)

        assert context.asts == [ast1.left,ast1.right,ast1] # type: ignore
    
    def test_2(self,ast1:AST):

        context = CounterContext()
        walker = self.build_walker2(context)
        walker.walk(ast1)

        assert context.asts == [ast1,ast1.left,ast1.right] # type: ignore

    def test_3(self,ast1:AST):

        context = CounterContext()
        walker = self.build_walker3(context)
        walker.walk(ast1)

        assert context.asts == [ast1.left,ast1.right,ast1] # type: ignore
    
    def test_4(self,ast1:AST):

        context = CounterContext()
        walker = self.build_walker4(context)
        walker.walk(ast1)

        assert context.asts == [ast1,ast1.left,ast1.right] # type: ignore