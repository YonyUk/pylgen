from pylgen.lexer.lexer cimport Lexer
from pylgen.common.types cimport Symbol
from .tokens_enum import TokenTypeEnum

cdef Symbol new_line = Symbol('new_line',True) # type:ignore
cdef Symbol int_number = Symbol('integer',True) # type:ignore
cdef Symbol float_number = Symbol('float',True) # type:ignore
cdef Symbol variable = Symbol('variable',True) # type:ignore
cdef Symbol plus = Symbol('+',True) # type:ignore
cdef Symbol minus = Symbol('-',True) # type:ignore
cdef Symbol mod = Symbol('%',True) # type:ignore
cdef Symbol div = Symbol('/',True) # type:ignore
cdef Symbol mul = Symbol('*',True) # type:ignore
cdef Symbol exp = Symbol('**',True) # type:ignore
cdef Symbol eq = Symbol('=',True) # type:ignore
cdef Symbol lp = Symbol('(',True) # type:ignore
cdef Symbol rp = Symbol(')',True) # type:ignore
cdef Symbol lc = Symbol('[',True) # type:ignore
cdef Symbol rc = Symbol(']',True) # type:ignore
cdef Symbol com = Symbol(',',True) # type:ignore
cdef Symbol double_dot = Symbol(':',True) # type:ignore
cdef Symbol sum_keyword = Symbol('sum_keyword',True) # type:ignore
cdef Symbol mean_keyword = Symbol('mean_keyword',True) # type:ignore
cdef Symbol dot_keyword = Symbol('dot_keyword',True) # type:ignore
cdef Symbol print_keyword = Symbol('print_keyword',True) # type:ignore
cdef Symbol type_int = Symbol('int_keyword',True) # type:ignore
cdef Symbol type_float = Symbol('float_keyword',True) # type:ignore
cdef Symbol type_complex = Symbol('complex_keyword',True) # type:ignore
cdef Symbol type_vector = Symbol('vector_keyword',True) # type:ignore

cdef Symbol comment = Symbol('COMMENT',True) # type:ignore

cdef dict[str,Symbol] _symbols = {
    '[':lc,
    ']':rc,
    '(':lp,
    ')':rp,
    ',':com,
    ':':double_dot
}

cdef dict[str,Symbol] _operators = {
    '+':plus,
    '-':minus,
    '*':mul,
    '**':exp,
    '/':div,
    '%':mod,
    '=':eq
}

cdef dict[str,Symbol] _keywords = {
    'sum':sum_keyword,
    'mean':mean_keyword,
    'dot':dot_keyword,
    'print':print_keyword,
    'int':type_int,
    'float':type_float,
    'complex':type_complex,
    'vector':type_vector
}

cdef Symbol get_symbol_function(object t,str tx):
    if t == TokenTypeEnum.INTEGER:
        return int_number
    if t == TokenTypeEnum.FLOAT:
        return float_number
    if t == TokenTypeEnum.JUMPLINE:
        return new_line
    if t == TokenTypeEnum.VARIABLE:
        return variable
    if t == TokenTypeEnum.OPERATOR:
        return _operators[tx]
    if t == TokenTypeEnum.SYMBOL:
        return _symbols[tx]
    if t == TokenTypeEnum.KEYWORD:
        return _keywords[tx]
    if t == TokenTypeEnum.COMMENT:
        return comment
    raise NotImplementedError()

cpdef Lexer build_lexer():
    lexer = Lexer(get_symbol_function,'\t| |//.*\n',False) # type:ignore
    lexer._enum_type = TokenTypeEnum
    lexer.set_eof_token('\x00',TokenTypeEnum.EOF)
    lexer.add_token_regex(0,TokenTypeEnum.INTEGER,'\\d+')
    lexer.add_token_regex(1,TokenTypeEnum.FLOAT,'\\d*\\.\\d+|\\d+e(\\+|\\-)\\d+')
    lexer.add_token_regex(2,TokenTypeEnum.JUMPLINE,'\n')
    lexer.add_token_regex(3,TokenTypeEnum.KEYWORD,'sum|mean|dot|print|int|float|complex|vector')
    lexer.add_token_regex(4,TokenTypeEnum.VARIABLE,'[a-zA-Z_]\\w*')
    lexer.add_token_regex(5,TokenTypeEnum.OPERATOR,'\\+|\\-|/|\\*\\*?|%|=')
    lexer.add_token_regex(6,TokenTypeEnum.SYMBOL,'\\[|\\]|:|\\(|\\)|\\,')
    lexer.add_token_regex(7,TokenTypeEnum.COMMENT,'//.*\n')
    return lexer