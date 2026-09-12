from pylgen.analysis import ASTWalker

from grammar.asts import *

from .context import PythonContext
from .traversals import PostOrder,EvalPostOrder,CheckerPostOrder
from .selectors import *
from .evaluator_visitors import *
from .semantic_visitors import *
from .collector_visitors import *

Context = PythonContext()

CheckerTraversal = CheckerPostOrder()
FuncDefCollectTraversal = PostOrder()
EvalTraversal = EvalPostOrder()

CheckerTraversal.set_default_selector(DefaultSelector())
CheckerTraversal.add_selector(AssignAST,AssignASTSelector())

FuncDefCollectTraversal.set_default_selector(DefaultSelector())

EvalTraversal.set_default_selector(DefaultSelector())
EvalTraversal.add_selector(AssignAST,AssignASTSelector())
EvalTraversal.add_selector(FuncDefAST,EvalFuncDefASTSelector())

collector = ASTWalker(Context,FuncDefCollectTraversal)

collector.add_visitor(FuncDefAST,FuncDefCollectorASTVisitor())

checker = ASTWalker(Context,CheckerTraversal)

checker.add_visitor(VariableAST,VariableASTSemanticCheckingVisitor())
checker.add_visitor(FuncCallAST,FuncCallASTSemanticCheckingVisitor())
checker.add_visitor(AssignAST,AssignASTSemanticCheckingVisitor())
checker.add_visitor(ReturnAST,ReturnASTSemanticCheckingVisitor())
checker.add_visitor(VoidReturnAST,ReturnASTSemanticCheckingVisitor())
checker.add_visitor(BreakAST,BreakASTSemanticVisitor())
checker.add_visitor(ContinueAST,ContinueASTSemanticVisitor())

evaluator = ASTWalker(Context,EvalTraversal)

evaluator.add_visitor(NumberAST,NumberASTEvaluatorVisitor())
evaluator.add_visitor(PlusAST,PlusASTEvaluatorVisitor())
evaluator.add_visitor(MinusAST,MinusASTEvaluatorVisitor())
evaluator.add_visitor(MulAST,MulASTEvaluatorVisitor())
evaluator.add_visitor(DivAST,DivASTEvaluatorVisitor())
evaluator.add_visitor(IntDivAST,IntDivASTEvaluatorVisitor())
evaluator.add_visitor(ModAST,ModASTEvaluatorVisitor())
evaluator.add_visitor(PowAST,PowASTEvaluatorVisitor())
evaluator.add_visitor(FuncCallAST,FuncCallASTEvaluatorVisitor())
evaluator.add_visitor(MinusMathExprAST,MinusMathExprASTEvaluatorVisitor())
evaluator.add_visitor(BooleanAST,BooleanASTEvaluatorVisitor())
evaluator.add_visitor(OrAST,OrASTEvaluatorVisitor())
evaluator.add_visitor(BitOrAST,BitOrASTEvaluatorVisitor())
evaluator.add_visitor(AndAST,AndASTEvaluatorVisitor())
evaluator.add_visitor(BitAndAST,BitAndASTEvaluatorVisitor())
evaluator.add_visitor(NotBoolExprAST,NotBoolExprASTEvaluatorVisitor())
evaluator.add_visitor(VariableAST,VariableASTEvaluatorVisitor())
evaluator.add_visitor(AssignAST,AssignASTEvaluatorVisitor())
evaluator.add_visitor(EqAST,EqASTEvaluatorVisitor())
evaluator.add_visitor(NeqAST,NeqASTEvaluatorVisitor())
evaluator.add_visitor(LeAST,LeASTEvaluatorVisitor())
evaluator.add_visitor(LeqAST,LeqASTEvaluatorVisitor())
evaluator.add_visitor(GeAST,GeASTEvaluatorVisitor())
evaluator.add_visitor(GeqAST,GeqASTEvaluatorVisitor())
evaluator.add_visitor(StringAST,StringASTEvaluatorVisitor())
evaluator.add_visitor(PlusEqAST,PlusEqASTEvaluatorVisitor())
evaluator.add_visitor(MinusEqAST,MinusEqASTEvaluatorVisitor())
evaluator.add_visitor(MulEqAST,MulEqASTEvaluatorVisitor())
evaluator.add_visitor(DivEqAST,DivEqASTEvaluatorVisitor())
evaluator.add_visitor(IntDivEqAST,IntDivEqASTEvaluatorVisitor())
evaluator.add_visitor(PowEqAST,PowEqASTEvaluatorVisitor())
evaluator.add_visitor(ModEqAST,ModEqASTEvaluatorVisitor())
evaluator.add_visitor(BitAndEqAST,BitAndEqASTEvaluatorVisitor())
evaluator.add_visitor(BitOrEqAST,BitOrEqASTEvaluatorVisitor())
evaluator.add_visitor(VoidReturnAST,VoidReturnASTEvaluatorVisitor())
evaluator.add_visitor(ReturnAST,ReturnASTEvaluatorVisitor())
evaluator.add_visitor(BreakAST,BreakASTEvaluatorVisitor())
evaluator.add_visitor(ContinueAST,ContinueASTEvaluatorVisitor())