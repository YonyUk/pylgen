from typing import List

from pylgen.common.types import Symbol,ASTListView,AST,Token
from pylgen.common.enums import TokenType
from pylgen.grammar.grammar import AttributedGrammar
from pylgen.lexer.lexer import IdentedLexer
from pylgen.parser import ParserBuilder,Parser
from pylgen.parser.parser_type import ParserType

import pytest

class TokenTypeEnum(TokenType):
    NUMBER = 'NUMBER'
    STRING = 'STRING'
    BOOLEAN = 'BOOLEAN'
    NEWLINE = 'NEWLINE'
    SYMBOL = 'SYMBOL'
    EOF = 'EOF'
    VARIABLE = 'VARIABLE'
    IDENTATION = 'IDENTATION'

Config = Symbol('Config')
ConfigSequence = Symbol('ConfigSequence')
Section = Symbol('Section')
SubSection = Symbol('SubSection')
SectionConfigSequence = Symbol('SectionConfigSequence')
ConfigAtom = Symbol('ConfigAtom')
Newlines = Symbol('Newlines')

lbracket = Symbol('[',True)
rbracket = Symbol(']',True)
variable = Symbol('variable',True)
indent = Symbol('INDENT',True)
dedent = Symbol('DEDENT',True)
minus = Symbol('-',True)
colon = Symbol(':',True)
string = Symbol('string',True)
boolean = Symbol('boolean',True)
number = Symbol('number',True)
newline = Symbol('newline',True)

class ConfigsAST(AST):

    def __init__(self, line: int, column: int):
        super().__init__(Config, line, column)
        self._configs = []

    def children(self) -> List[AST]:
        return self._configs

class ConfigSequenceAST(AST):

    def __init__(self, line: int, column: int):
        super().__init__(ConfigSequence, line, column)
        self._configs = []

    def children(self) -> List[AST]:
        return self._configs

class ConfigSectionAST(AST):

    def __init__(self, section_name:str,line: int, column: int):
        super().__init__(Section, line, column)
        self._name = section_name
        self._configs = []

    @property
    def section_name(self) -> str:
        return self._name
    
    def children(self) -> List[AST]:
        return self._configs

class SectionConfigSequenceAST(AST):

    def __init__(self, line: int, column: int):
        super().__init__(ConfigSequence, line, column)
        self._configs = []

class AtomConfigAST(AST):

    def __init__(self, name:str,value:str | float | bool,line: int, column: int):
        super().__init__(ConfigAtom, line, column)
        self._name = name
        self._value = value

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> str | float | bool:
        return self._value

    def children(self) -> List[AST]:
        return []

def get_symbol_function(t:TokenTypeEnum,tx:str) -> Symbol:
    if t == TokenTypeEnum.NEWLINE:
        return newline
    if t == TokenTypeEnum.NUMBER:
        return number
    if t == TokenTypeEnum.BOOLEAN:
        return boolean
    if t == TokenTypeEnum.STRING:
        return string
    if t == TokenTypeEnum.IDENTATION:
        return indent
    if t == TokenTypeEnum.VARIABLE:
        return variable
    if t == TokenTypeEnum.SYMBOL:
        return Symbol(tx,True)
    return Symbol(tx,True)

def config_configsequence_reductor(asts:ASTListView) -> AST:
    config = ConfigsAST(1,1)
    config_sequence:ConfigSequenceAST = asts[0] # type:ignore
    config._configs = config_sequence._configs
    return config

def configsequence_section_reductor(asts:ASTListView) -> AST:
    config_sequence:ConfigSequenceAST = asts[0] # type:ignore
    config_sequence._configs.append(asts[1])
    return config_sequence

def configsequence_direct_reductor(asts:ASTListView) -> AST:
    config = ConfigSequenceAST(asts[0].line,asts[0].column)
    config._configs.append(asts[0])
    return config

def section_reductor(asts:ASTListView) -> AST:
    configs:SectionConfigSequenceAST = asts[5] # type:ignore
    var:Token = asts[1] # type:ignore
    config = ConfigSectionAST(var.text,asts[0].line,asts[0].column)
    config._configs = configs._configs
    return config

def sectionconfigsequence_configatom_reductor(asts:ASTListView) -> AST:
    config = SectionConfigSequenceAST(asts[0].line,asts[0].column)
    config._configs.append(asts[0])
    return config

def sectionconfigsequence_sectionconfigsequence_newlines_configatom(asts:ASTListView) -> AST:
    config:SectionConfigSequenceAST = asts[0] # type:ignore
    config._configs.append(asts[1])
    return config

def configatom_variable_colon_string_reductor(asts:ASTListView) -> AST:
    var:Token = asts[0] # type:ignore
    val:Token = asts[2] # type:ignore
    config = AtomConfigAST(var.text,val.text[1:-1],var.line,var.column)
    return config

def configatom_variable_colon_boolean_reductor(asts:ASTListView) -> AST:
    var:Token = asts[0] # type:ignore
    val:Token = asts[2] # type:ignore
    config = AtomConfigAST(var.text,val.text == 'true',var.line,var.column)
    return config

def configatom_variable_colon_number_reductor(asts:ASTListView) -> AST:
    var:Token = asts[0] # type:ignore
    val:Token = asts[2] # type:ignore
    config = AtomConfigAST(var.text,float(val.text),var.line,var.column)
    return config

def sanitaze_text(text:str) -> str:
    lines = text.split('\n')
    lines = list(filter(lambda line:not line.strip() == '', lines))
    return '\n'.join(lines)

G = AttributedGrammar(Config,'$')

G[Config] += (ConfigSequence,),config_configsequence_reductor

G[ConfigSequence] += (ConfigSequence,Section),configsequence_section_reductor
G[ConfigSequence] += (Section,),configsequence_direct_reductor

G[Section] += (lbracket,variable,rbracket,newline,indent,SectionConfigSequence,dedent),section_reductor

G[SectionConfigSequence] += (ConfigAtom,),sectionconfigsequence_configatom_reductor
G[SectionConfigSequence] += (SubSection,),sectionconfigsequence_configatom_reductor
G[SectionConfigSequence] += (SectionConfigSequence,ConfigAtom),sectionconfigsequence_sectionconfigsequence_newlines_configatom
G[SectionConfigSequence] += (SectionConfigSequence,SubSection),sectionconfigsequence_sectionconfigsequence_newlines_configatom

G[ConfigAtom] += (variable,colon,string,newline),configatom_variable_colon_string_reductor
G[ConfigAtom] += (variable,colon,boolean,newline),configatom_variable_colon_boolean_reductor
G[ConfigAtom] += (variable,colon,number,newline),configatom_variable_colon_number_reductor
G[ConfigAtom] += (variable,colon,string),configatom_variable_colon_string_reductor
G[ConfigAtom] += (variable,colon,boolean),configatom_variable_colon_boolean_reductor
G[ConfigAtom] += (variable,colon,number),configatom_variable_colon_number_reductor

G[SubSection] += (minus,variable,colon,newline,indent,SectionConfigSequence,dedent),section_reductor

class TestIntegrationIdentedLexerParser:

    @pytest.fixture(scope='class')
    def lexer(self) -> IdentedLexer:
        lexer = IdentedLexer(get_symbol_function,' ')
        lexer.set_text_sanitize_function(sanitaze_text)
        lexer[0,TokenTypeEnum.NUMBER] = r'\d+(\.\d+)?'
        lexer[1,TokenTypeEnum.BOOLEAN] = 'true|false'
        lexer[2,TokenTypeEnum.VARIABLE] = r'[a-zA-Z_]\w*'
        lexer[3,TokenTypeEnum.IDENTATION] = '    |\t'
        lexer[4,TokenTypeEnum.NEWLINE] = '\n'
        lexer[5,TokenTypeEnum.SYMBOL] = r'\-|:|\[|\]'
        lexer[6,TokenTypeEnum.STRING] = '".*"'

        lexer.set_ident(TokenTypeEnum.IDENTATION)
        lexer.set_indent_symbol(indent)
        lexer.set_dedent_symbol(dedent)
        lexer.set_eof_token('$',TokenTypeEnum.SYMBOL)

        return lexer

    @pytest.fixture
    def parser(self) -> Parser:
        return ParserBuilder.build_parser_from_attributed(G,ParserType.LALR1)

    def test_1(self,lexer:IdentedLexer,parser:Parser):
        parser.reset()
        text = '''
[personal_data]
    name:"jhon"

'''
        lexer.load_text(text)
        ast = parser.parse(lexer.tokens)
        assert len(lexer.errors) == 0
        assert len(parser.errors) == 0

    def test_2(self,lexer:IdentedLexer,parser:Parser):
        parser.reset()
        text = '''
[personal_data]
    name:"jhon"
    age:27
    working:false
    - home:
        address:"wall street"
        apt:12
'''
        lexer.load_text(text)
        ast = parser.parse(lexer.tokens)
        assert len(lexer.errors) == 0
        assert len(parser.errors) == 0

    def test_3(self,lexer:IdentedLexer,parser:Parser):
        parser.reset()
        text = '''
[economic_data]
    bank:"NY"
    debit:12000000

    - hipotec:
        remains:100000
        until:"march"

    solded:false
'''
        lexer.load_text(text)
        ast = parser.parse(lexer.tokens)
        assert len(lexer.errors) == 0
        assert len(parser.errors) == 0

    def test_4(self,lexer:IdentedLexer,parser:Parser):
        parser.reset()
        text = '''
[extra_data]
    level1:"proving"

    - level2:
        final:true

        -level3:
            name:"extra"
            value:100

            - level4:
                final:true
'''
        lexer.load_text(text)
        ast = parser.parse(lexer.tokens)
        assert len(lexer.errors) == 0
        assert len(parser.errors) == 0