from typing import Dict, List, Tuple

from common.types import AST, Token,Symbol
from common.enums import TokenType
from grammar.grammar import Production
from parser.parser import BottomUpParser
from parser.bottom_up_parser_actions import BottomUpParserAction

class TokenTypeEnum(TokenType):
    NUMBER = 'NUMBER'
    SYMBOL = 'SYMBOL'

class TestIntegrationBottomUpParser:

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