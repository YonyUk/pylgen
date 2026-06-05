from typing import Dict, List, Tuple

from common.types import AST, Token,Symbol
from common.enums import TokenType
from grammar.grammar import Grammar, Production
from parser.parser import BottomUpParser
from parser.bottom_up_parser_actions import BottomUpParserAction
from parser.lalr_parser import LALRState
from parser.parser_builder import ParserBuilder

class TokenTypeEnum(TokenType):
    NUMBER = 'NUMBER'
    SYMBOL = 'SYMBOL'

class TestIntegrationBottomUpParser:

    def plain_goto_table(self,goto:Dict[Tuple[LALRState,Symbol],LALRState]) -> Dict[Tuple[str,Symbol],str]:
        result = {}
        for (state,symbol),to_state in goto.items():
            result[(f'I{state.index}',symbol)] = f'I{to_state.index}'
        return result

    def plain_action_table(self,action:Dict[Tuple[LALRState,Symbol],Tuple[str,LALRState|Production]]) -> Dict[Tuple[str,Symbol],Tuple[str, str | Production]]:
        result = {}
        for (state,symbol),(act,to_state_or_production) in action.items():
            if act == BottomUpParserAction.SHIFT:
                result[(f'I{state.index}',symbol)] = (act,f'I{to_state_or_production.index}') # type:ignore
            else:
                result[(f'I{state.index}',symbol)] = (act,to_state_or_production)
        return result

    def test_parsing_1(self):
        
        def reductor(asts:List[AST]) -> AST:
            return AST(E,1,1)

        E = Symbol('E')
        n = Symbol('n',True)
        end = Symbol('$',True)

        token = Token('12',TokenTypeEnum.NUMBER,n,1,1)
        end_token = Token('$',TokenTypeEnum.SYMBOL,end,1,3)

        goto:Dict[Tuple[str,Symbol],str] = {}
        action:Dict[Tuple[str,Symbol],Tuple[str, str | Production]] = {}

        goto[('I0',n)] = 'I1'
        goto[('I0',E)] = 'I2'

        action[('I0',n)] = (BottomUpParserAction.SHIFT,'I1')
        action[('I0',E)] = (BottomUpParserAction.SHIFT,'I2')
        action[('I1',end)] = (BottomUpParserAction.REDUCE,Production(E,[n]))
        action[('I2',end)] = (BottomUpParserAction.ACCEPT,'')

        parser = BottomUpParser('I0',goto,action)
        parser[Production(E,[n])] = reductor

        tokens = [token,end_token]

        ast = parser.parse(tokens)
        assert ast.symbol == E
    
    def test_parsing_2(self):

        E = Symbol('E')
        T = Symbol('T')
        plus = Symbol('+',True)
        n = Symbol('n',True)
        end = Symbol('$',True)

        def reductor_E_plus_T(asts:List[AST]) -> AST:
            return AST(E,asts[1].line,asts[1].column)
        
        def reductor_E_T(asts:List[AST]) -> AST:
            return AST(E,asts[0].line,asts[0].column)
        
        def reductor_T_n(asts:List[AST]) -> AST:
            return AST(T,asts[0].line,asts[0].column)

        t1 = Token('12',TokenTypeEnum.NUMBER,n,1,1)
        t2 = Token('+',TokenTypeEnum.SYMBOL,plus,1,4)
        t3 = Token('13',TokenTypeEnum.NUMBER,n,1,6)
        end_token = Token('$',TokenTypeEnum.SYMBOL,end,1,7)

        goto:Dict[Tuple[str,Symbol],str] = {}
        action:Dict[Tuple[str,Symbol],Tuple[str, str | Production]] = {}

        goto[('I0',E)] = 'I3'
        goto[('I0',T)] = 'I1'
        goto[('I0',n)] = 'I2'
        goto[('I3',plus)] = 'I4'
        goto[('I4',n)] = 'I2'
        goto[('I4',T)] = 'I5'

        action[('I3',end)] = (BottomUpParserAction.ACCEPT,'')
        action[('I3',plus)] = (BottomUpParserAction.SHIFT,'I4')
        action[('I2',end)] = (BottomUpParserAction.REDUCE,Production(T,[n]))
        action[('I2',plus)] = (BottomUpParserAction.REDUCE,Production(T,[n]))
        action[('I0',E)] = (BottomUpParserAction.SHIFT,'I3')
        action[('I0',T)] = (BottomUpParserAction.SHIFT,'I1')
        action[('I0',n)] = (BottomUpParserAction.SHIFT,'I2')
        action[('I1',end)] = (BottomUpParserAction.REDUCE,Production(E,[T]))
        action[('I1',plus)] = (BottomUpParserAction.REDUCE,Production(E,[T]))
        action[('I4',n)] = (BottomUpParserAction.SHIFT,'I2')
        action[('I4',T)] = (BottomUpParserAction.SHIFT,'I5')
        action[('I5',end)] = (BottomUpParserAction.REDUCE,Production(E,[E,plus,T]))
        action[('I5',plus)] = (BottomUpParserAction.REDUCE,Production(E,[E,plus,T]))

        parser = BottomUpParser('I0',goto,action)
        
        parser[Production(T,[n])] = reductor_T_n
        parser[Production(E,[T])] = reductor_E_T
        parser[Production(E,[E,plus,T])] = reductor_E_plus_T

        tokens = [t1,t2,t3,end_token]

        ast = parser.parse(tokens)
        assert ast.symbol == E
        assert ast.line == t2.line and ast.column == t2.column
    
    def test_parsing_3(self):
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

        def reductor_E_plus_T(asts:List[AST]) -> AST:
            return AST(E,asts[1].line,asts[1].column)
        
        def reductor_E_T(asts:List[AST]) -> AST:
            return AST(E,asts[0].line,asts[0].column)
        
        def reductor_T_mul_F(asts:List[AST]) -> AST:
            return AST(T,asts[1].line,asts[1].column)
        
        def reductor_T_F(asts:List[AST]) -> AST:
            return AST(T,asts[0].line,asts[0].column)
        
        def reductor_F_lp_E_rp(asts:List[AST]) -> AST:
            return AST(F,asts[1].line,asts[1].column)
        
        def reductor_F_n(asts:List[AST]) -> AST:
            return AST(F,asts[0].line,asts[0].column)

        goto,action = ParserBuilder.get_goto_action_tables_lalr(G)

        plain_goto = self.plain_goto_table(goto)
        plain_action = self.plain_action_table(action)

        parser = BottomUpParser('I0',plain_goto,plain_action)
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
        assert ast.line == mul_token.line and ast.column == mul_token.column