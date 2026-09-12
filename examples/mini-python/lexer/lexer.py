from pylgen.lexer import IdentedLexer
from pylgen.common.types import Symbol
from pylgen.analysis import LexicalRule

from grammar.symbols import *

from .tokens import PythonTokenType

class IntegerLexicalRule(LexicalRule):

    def __init__(self) -> None:
        super().__init__('non-zero integers cannot start with 0 digit')

    def _check(self, text: str):
        return len(text) == 1 or text[0] != '0'

class FloatingLexicalRule(LexicalRule):

    def __init__(self) -> None:
        super().__init__('non-zero numbers must have at most one 0 digit at the start')

    def _check(self,text:str):
        if len(text) <= 3:
            return True
        if text[0] == '0':
            if text[1] not in ['.','e']:
                return False
            return True
        return True

class VariableLexicalRule(LexicalRule):

    def __init__(self) -> None:
        super().__init__('variables names must starts with a non-digit character')

    def _check(self, text: str):
        return not text[0].isdigit()

whitespace = Symbol('whitespace',True)
invalid_token = Symbol('INVALID_TOKEN',True)

operators = {
    '+':plus,
    '-':minus,
    '*':mul,
    '/':div,
    '//':int_div,
    '%':mod,
    '**':power,
    '==':eq,
    '=':assign,
    'or':or_op,
    'and':and_op,
    'not':not_op,
    '|':bit_or,
    '&':bit_and,
    '!=':neq,
    '<':le,
    '>':ge,
    '<=':leq,
    '>=':geq,
    '+=':plus_eq,
    '-=':minus_eq,
    '*=':mul_eq,
    '/=':div_eq,
    '//=':int_div_eq,
    '**=':power_eq,
    '|=':bit_or_eq,
    '&=':bit_and_eq,
    '%=':mod_eq
}

symbols = {
    '(':lparen,
    ')':rparen,
    ',':comma,
    ':':colon
}

keywords = {
    'print':print_keyword,
    'clear':clear_keyword,
    'exit':exit_keyword,
    'if':if_keyword,
    'elif':elif_keyword,
    'else':else_keyword,
    'while':while_keyword,
    'input':input_keyword,
    'def':def_keyword,
    'return':return_keyword,
    'break':break_keyword,
    'continue':continue_keyword
}

def get_symbol_function(t:PythonTokenType,tx:str) -> Symbol:
    if t == PythonTokenType.INTEGER:
        return int_number
    if t == PythonTokenType.FLOATING:
        return float_number
    if t == PythonTokenType.STRING:
        return string
    if t == PythonTokenType.SYMBOL:
        return symbols[tx]
    if t == PythonTokenType.OPERATOR:
        return operators[tx]
    if t == PythonTokenType.IDENTATION:
        return indent
    if t == PythonTokenType.KEYWORD:
        return keywords[tx]
    if t == PythonTokenType.WHITESPACE or t == PythonTokenType.WHITESPACEMARKER:
        return whitespace
    if t == PythonTokenType.JUMPLINE:
        return jumpline
    if t == PythonTokenType.BOOLEAN:
        return boolean
    if t == PythonTokenType.IDENTIFIER:
        return identifier
    return invalid_token

def sanitaze_function(t:str) -> str:
    new_lines = []
    for line in t.splitlines():
        if line.strip() == '':
            new_lines.append('#ignore#')
        else:
            new_lines.append(line)
    return '\n'.join(new_lines) + '\n'

PythonLexer = IdentedLexer(get_symbol_function,'#ignore#\n?')
PythonLexer.set_eof_token('\x00',PythonTokenType.EOF)
PythonLexer.set_ident(PythonTokenType.IDENTATION)
PythonLexer.set_indent_symbol(indent)
PythonLexer.set_dedent_symbol(dedent)
PythonLexer.set_text_sanitize_function(sanitaze_function)

PythonLexer[0,PythonTokenType.INTEGER] = r'\d+'
PythonLexer[1,PythonTokenType.FLOATING] = r'(\d+)?\.\d+|\d+e(\+|\-)?\d+'
PythonLexer[2,PythonTokenType.BOOLEAN] = 'True|False'
PythonLexer[3,PythonTokenType.KEYWORD] = 'print|clear|exit|if|elif|else|while|input|def|return|break|continue'
PythonLexer[4,PythonTokenType.OPERATOR] = r'\+=?|\-=?|\*\*?=?|//?=?|%=?|==?|or|and|not|\|=?|&=?|!=|<=?|>=?'
PythonLexer[5,PythonTokenType.IDENTIFIER] = r'\w+'
PythonLexer[6,PythonTokenType.SYMBOL] = r'\(|\)|\,|:'
PythonLexer[7,PythonTokenType.IDENTATION] = '    |\t'
PythonLexer[8,PythonTokenType.WHITESPACE] = ' '
PythonLexer[9,PythonTokenType.WHITESPACEMARKER] = '#ignore#\n?'
PythonLexer[10,PythonTokenType.JUMPLINE] = '\n'
PythonLexer[11,PythonTokenType.STRING] = '"[^"]*"|\'[^\']*\''

PythonLexer.add_rule(PythonTokenType.INTEGER,IntegerLexicalRule())
PythonLexer.add_rule(PythonTokenType.FLOATING,FloatingLexicalRule())
PythonLexer.add_rule(PythonTokenType.IDENTIFIER,VariableLexicalRule())

print('initializing lexer...')
PythonLexer.initialize()
print('done')