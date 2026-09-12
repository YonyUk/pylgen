from lexer import PythonLexer
from grammar import PythonParser
from semantic.walkers import evaluator,checker,Context,collector

from editor import PythonEditor

PythonEditor(PythonLexer,PythonParser,Context,collector,checker,evaluator)