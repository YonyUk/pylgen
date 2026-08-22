from typing import List

from pylgen.common.types import Symbol,AST,Token,ASTListView
from pylgen.common.enums import TokenType
from pylgen.grammar.grammar import Grammar,AttributedGrammar,Production
from pylgen.parser.parser_builder import ParserBuilder
from pylgen.parser.parser_type import ParserType
from pylgen.parser.parser import BottomUpParser,ParsingException

class TokenTypeEnum(TokenType):
    NUMBER = 'NUMBER'
    SYMBOL = 'SYMBOL'

class TestIntegrationParserBuilder:

    def test_build_lalr_parser_1(self):
        E = Symbol('E')
        T = Symbol('T')
        F = Symbol('F')

        plus = Symbol('+',True)
        mul = Symbol('*',True)
        n = Symbol('n',True)
        lp = Symbol('(',True)
        rp = Symbol(')',True)

        G = Grammar(E,'$')

        G[E] += E,plus,T
        G[E] += T,
        G[T] += T,mul,F
        G[T] += F,
        G[F] += lp,E,rp
        G[F] += n,

        def reductor_E_plus_T(asts:ASTListView) -> AST:
            return AST(E,asts[1].line,asts[1].column)
                
        def reductor_E_T(asts:ASTListView) -> AST:
            return AST(E,asts[0].line,asts[0].column)
                
        def reductor_T_mul_F(asts:ASTListView) -> AST:
            return AST(T,asts[1].line,asts[1].column)
                
        def reductor_T_F(asts:ASTListView) -> AST:
            return AST(T,asts[0].line,asts[0].column)
                
        def reductor_F_lp_E_rp(asts:ASTListView) -> AST:
            return AST(F,asts[1].line,asts[1].column)
                
        def reductor_F_n(asts:ASTListView) -> AST:
            return AST(F,asts[0].line,asts[0].column)

        parser:BottomUpParser = ParserBuilder.build_parser(G,ParserType.LALR1) # type:ignore

        parser[Production(E,[E,plus,T])] = reductor_E_plus_T
        parser[Production(E,[T])] = reductor_E_T
        parser[Production(T,[T,mul,F])] = reductor_T_mul_F
        parser[Production(T,[F])] = reductor_T_F
        parser[Production(F,[lp,E,rp])] = reductor_F_lp_E_rp
        parser[Production(F,[n])] = reductor_F_n

        lp_token = Token('(',TokenTypeEnum.SYMBOL,lp,1,1)
        rp_token = Token(')',TokenTypeEnum.SYMBOL,rp,1,11)
        
        number1 = Token('12',TokenTypeEnum.NUMBER,n,1,1)
        plus_token = Token('+',TokenTypeEnum.SYMBOL,plus,1,4)
        number2 = Token('13',TokenTypeEnum.NUMBER,n,1,6)

        mul_token = Token('*',TokenTypeEnum.SYMBOL,mul,1,9)
        number3 = Token('2',TokenTypeEnum.NUMBER,n,1,11)
        end = Token(G.end_symbol.symbol,TokenTypeEnum.SYMBOL,G.end_symbol,1,12)

        tokens = [number1,plus_token,number2,mul_token,number3,end]
        
        ast = parser.parse(tokens)
        assert ast.symbol == E
        assert ast.line == plus_token.line and ast.column == plus_token.column

        parser.reset()
        tokens = [number1,plus_token,number2,number2,mul_token,number3,end]
        try:
            ast = parser.parse(tokens)
        except ParsingException:
            pass

        assert len(parser.errors) == 1
        error = next(iter(parser.errors))
        assert error.line == number2.line
        assert error.column == number2.column
        number1 = Token('12',TokenTypeEnum.NUMBER,n,1,3)
        plus_token = Token('+',TokenTypeEnum.SYMBOL,plus,1,6)
        number2 = Token('13',TokenTypeEnum.NUMBER,n,1,8)
        mul_token = Token('*',TokenTypeEnum.SYMBOL,mul,1,13)
        number3 = Token('2',TokenTypeEnum.NUMBER,n,1,15)
        end = Token(G.end_symbol.symbol,TokenTypeEnum.SYMBOL,G.end_symbol,1,16)

        tokens = [lp_token,number1,plus_token,number2,rp_token,mul_token,number3,end]
        
        parser.reset()
        ast = parser.parse(tokens)
        assert ast.symbol == E
        assert ast.column == mul_token.column

        parser.reset()
        tokens = [lp_token,number1,number1,plus_token,number2,rp_token,mul_token,mul_token,number3,end]
        try:
            ast = parser.parse(tokens)
        except ParsingException:
            pass

        errors = [(1,3),(1,13)]
        assert len(parser.errors) == 2
        for error in parser.errors:
            assert (error.line,error.column) in errors

    def test_build_lalr_parser_2(self):
        E = Symbol('E')
        T = Symbol('T')
        F = Symbol('F')

        plus = Symbol('+',True)
        mul = Symbol('*',True)
        n = Symbol('n',True)
        lp = Symbol('(',True)
        rp = Symbol(')',True)

        def reductor_E_plus_T(asts:ASTListView) -> AST:
            return AST(E,asts[1].line,asts[1].column)
                
        def reductor_E_T(asts:ASTListView) -> AST:
            return AST(E,asts[0].line,asts[0].column)
                
        def reductor_T_mul_F(asts:ASTListView) -> AST:
            return AST(T,asts[1].line,asts[1].column)
                
        def reductor_T_F(asts:ASTListView) -> AST:
            return AST(T,asts[0].line,asts[0].column)
                
        def reductor_F_lp_E_rp(asts:ASTListView) -> AST:
            return AST(F,asts[1].line,asts[1].column)
                
        def reductor_F_n(asts:ASTListView) -> AST:
            return AST(F,asts[0].line,asts[0].column)

        G = AttributedGrammar(E,'$')

        G[E] += (E,plus,T),reductor_E_plus_T
        G[E] += (T,),reductor_E_T
        G[T] += (T,mul,F),reductor_T_mul_F
        G[T] += (F,),reductor_T_F
        G[F] += (lp,E,rp),reductor_F_lp_E_rp
        G[F] += (n,),reductor_F_n

        parser:BottomUpParser = ParserBuilder.build_parser_from_attributed(G,ParserType.LALR1) # type:ignore

        lp_token = Token('(',TokenTypeEnum.SYMBOL,lp,1,1)
        rp_token = Token(')',TokenTypeEnum.SYMBOL,rp,1,11)
        
        number1 = Token('12',TokenTypeEnum.NUMBER,n,1,1)
        plus_token = Token('+',TokenTypeEnum.SYMBOL,plus,1,4)
        number2 = Token('13',TokenTypeEnum.NUMBER,n,1,6)

        mul_token = Token('*',TokenTypeEnum.SYMBOL,mul,1,9)
        number3 = Token('2',TokenTypeEnum.NUMBER,n,1,11)
        end = Token(G.end_symbol.symbol,TokenTypeEnum.SYMBOL,G.end_symbol,1,12)

        tokens = [number1,plus_token,number2,mul_token,number3,end]
        
        ast = parser.parse(tokens)
        assert ast.symbol == E
        assert ast.line == plus_token.line and ast.column == plus_token.column
        
        parser.reset()
        tokens = [number1,plus_token,number2,number2,mul_token,number3,end]
        try:
            ast = parser.parse(tokens)
        except ParsingException:
            pass

        assert len(parser.errors) == 1
        error = next(iter(parser.errors))
        assert error.line == number2.line
        assert error.column == number2.column

        number1 = Token('12',TokenTypeEnum.NUMBER,n,1,3)
        plus_token = Token('+',TokenTypeEnum.SYMBOL,plus,1,6)
        number2 = Token('13',TokenTypeEnum.NUMBER,n,1,8)
        mul_token = Token('*',TokenTypeEnum.SYMBOL,mul,1,13)
        number3 = Token('2',TokenTypeEnum.NUMBER,n,1,15)
        end = Token(G.end_symbol.symbol,TokenTypeEnum.SYMBOL,G.end_symbol,1,16)

        tokens = [lp_token,number1,plus_token,number2,rp_token,mul_token,number3,end]
        
        parser.reset()
        ast = parser.parse(tokens)
        assert ast.symbol == E
        assert ast.column == mul_token.column

        parser.reset()
        tokens = [lp_token,number1,number1,plus_token,number2,rp_token,mul_token,mul_token,number3,end]
        try:
            ast = parser.parse(tokens)
        except ParsingException:
            pass

        errors = [(1,3),(1,13)]
        assert len(parser.errors) == 2
        for error in parser.errors:
            assert (error.line,error.column) in errors

    def test_build_slr_parser_1(self):
        E = Symbol('E')
        T = Symbol('T')
        F = Symbol('F')

        plus = Symbol('+',True)
        mul = Symbol('*',True)
        n = Symbol('n',True)
        lp = Symbol('(',True)
        rp = Symbol(')',True)

        G = Grammar(E,'$')

        G[E] += E,plus,T
        G[E] += T,
        G[T] += T,mul,F
        G[T] += F,
        G[F] += lp,E,rp
        G[F] += n,

        def reductor_E_plus_T(asts:ASTListView) -> AST:
            return AST(E,asts[1].line,asts[1].column)
                
        def reductor_E_T(asts:ASTListView) -> AST:
            return AST(E,asts[0].line,asts[0].column)
                
        def reductor_T_mul_F(asts:ASTListView) -> AST:
            return AST(T,asts[1].line,asts[1].column)
                
        def reductor_T_F(asts:ASTListView) -> AST:
            return AST(T,asts[0].line,asts[0].column)
                
        def reductor_F_lp_E_rp(asts:ASTListView) -> AST:
            return AST(F,asts[1].line,asts[1].column)
                
        def reductor_F_n(asts:ASTListView) -> AST:
            return AST(F,asts[0].line,asts[0].column)

        parser:BottomUpParser = ParserBuilder.build_parser(G,ParserType.SLR) # type:ignore

        parser[Production(E,[E,plus,T])] = reductor_E_plus_T
        parser[Production(E,[T])] = reductor_E_T
        parser[Production(T,[T,mul,F])] = reductor_T_mul_F
        parser[Production(T,[F])] = reductor_T_F
        parser[Production(F,[lp,E,rp])] = reductor_F_lp_E_rp
        parser[Production(F,[n])] = reductor_F_n

        lp_token = Token('(',TokenTypeEnum.SYMBOL,lp,1,1)
        rp_token = Token(')',TokenTypeEnum.SYMBOL,rp,1,11)
        
        number1 = Token('12',TokenTypeEnum.NUMBER,n,1,1)
        plus_token = Token('+',TokenTypeEnum.SYMBOL,plus,1,4)
        number2 = Token('13',TokenTypeEnum.NUMBER,n,1,6)

        mul_token = Token('*',TokenTypeEnum.SYMBOL,mul,1,9)
        number3 = Token('2',TokenTypeEnum.NUMBER,n,1,11)
        end = Token(G.end_symbol.symbol,TokenTypeEnum.SYMBOL,G.end_symbol,1,12)

        tokens = [number1,plus_token,number2,mul_token,number3,end]
        
        ast = parser.parse(tokens)
        breakpoint()
        assert ast.symbol == E
        assert ast.line == plus_token.line and ast.column == plus_token.column

        parser.reset()
        tokens = [number1,plus_token,number2,number2,mul_token,number3,end]
        try:
            ast = parser.parse(tokens)
        except ParsingException:
            pass

        assert len(parser.errors) == 1
        error = next(iter(parser.errors))
        assert error.line == number2.line
        assert error.column == number2.column
        number1 = Token('12',TokenTypeEnum.NUMBER,n,1,3)
        plus_token = Token('+',TokenTypeEnum.SYMBOL,plus,1,6)
        number2 = Token('13',TokenTypeEnum.NUMBER,n,1,8)
        mul_token = Token('*',TokenTypeEnum.SYMBOL,mul,1,13)
        number3 = Token('2',TokenTypeEnum.NUMBER,n,1,15)
        end = Token(G.end_symbol.symbol,TokenTypeEnum.SYMBOL,G.end_symbol,1,16)

        tokens = [lp_token,number1,plus_token,number2,rp_token,mul_token,number3,end]
        
        parser.reset()
        ast = parser.parse(tokens)
        assert ast.symbol == E
        assert ast.column == mul_token.column

        parser.reset()
        tokens = [lp_token,number1,number1,plus_token,number2,rp_token,mul_token,mul_token,number3,end]
        try:
            ast = parser.parse(tokens)
        except ParsingException:
            pass

        errors = [(1,3),(1,13)]
        assert len(parser.errors) == 2
        for error in parser.errors:
            assert (error.line,error.column) in errors

    def test_build_slr_parser_2(self):
        E = Symbol('E')
        T = Symbol('T')
        F = Symbol('F')

        plus = Symbol('+',True)
        mul = Symbol('*',True)
        n = Symbol('n',True)
        lp = Symbol('(',True)
        rp = Symbol(')',True)

        def reductor_E_plus_T(asts:ASTListView) -> AST:
            return AST(E,asts[1].line,asts[1].column)
                
        def reductor_E_T(asts:ASTListView) -> AST:
            return AST(E,asts[0].line,asts[0].column)
                
        def reductor_T_mul_F(asts:ASTListView) -> AST:
            return AST(T,asts[1].line,asts[1].column)
                
        def reductor_T_F(asts:ASTListView) -> AST:
            return AST(T,asts[0].line,asts[0].column)
                
        def reductor_F_lp_E_rp(asts:ASTListView) -> AST:
            return AST(F,asts[1].line,asts[1].column)
                
        def reductor_F_n(asts:ASTListView) -> AST:
            return AST(F,asts[0].line,asts[0].column)

        G = AttributedGrammar(E,'$')

        G[E] += (E,plus,T),reductor_E_plus_T
        G[E] += (T,),reductor_E_T
        G[T] += (T,mul,F),reductor_T_mul_F
        G[T] += (F,),reductor_T_F
        G[F] += (lp,E,rp),reductor_F_lp_E_rp
        G[F] += (n,),reductor_F_n

        parser:BottomUpParser = ParserBuilder.build_parser_from_attributed(G,ParserType.SLR) # type:ignore

        lp_token = Token('(',TokenTypeEnum.SYMBOL,lp,1,1)
        rp_token = Token(')',TokenTypeEnum.SYMBOL,rp,1,11)
        
        number1 = Token('12',TokenTypeEnum.NUMBER,n,1,1)
        plus_token = Token('+',TokenTypeEnum.SYMBOL,plus,1,4)
        number2 = Token('13',TokenTypeEnum.NUMBER,n,1,6)

        mul_token = Token('*',TokenTypeEnum.SYMBOL,mul,1,9)
        number3 = Token('2',TokenTypeEnum.NUMBER,n,1,11)
        end = Token(G.end_symbol.symbol,TokenTypeEnum.SYMBOL,G.end_symbol,1,12)

        tokens = [number1,plus_token,number2,mul_token,number3,end]
        
        ast = parser.parse(tokens)
        assert ast.symbol == E
        assert ast.line == plus_token.line and ast.column == plus_token.column
        
        parser.reset()
        tokens = [number1,plus_token,number2,number2,mul_token,number3,end]
        try:
            ast = parser.parse(tokens)
        except ParsingException:
            pass

        assert len(parser.errors) == 1
        error = next(iter(parser.errors))
        assert error.line == number2.line
        assert error.column == number2.column

        number1 = Token('12',TokenTypeEnum.NUMBER,n,1,3)
        plus_token = Token('+',TokenTypeEnum.SYMBOL,plus,1,6)
        number2 = Token('13',TokenTypeEnum.NUMBER,n,1,8)
        mul_token = Token('*',TokenTypeEnum.SYMBOL,mul,1,13)
        number3 = Token('2',TokenTypeEnum.NUMBER,n,1,15)
        end = Token(G.end_symbol.symbol,TokenTypeEnum.SYMBOL,G.end_symbol,1,16)

        tokens = [lp_token,number1,plus_token,number2,rp_token,mul_token,number3,end]
        
        parser.reset()
        ast = parser.parse(tokens)
        assert ast.symbol == E
        assert ast.column == mul_token.column

        parser.reset()
        tokens = [lp_token,number1,number1,plus_token,number2,rp_token,mul_token,mul_token,number3,end]
        try:
            ast = parser.parse(tokens)
        except ParsingException:
            pass

        errors = [(1,3),(1,13)]
        assert len(parser.errors) == 2
        for error in parser.errors:
            assert (error.line,error.column) in errors