from common.types cimport Symbol
from parser.lr0_parser cimport LR0State

cdef class LALRState(LR0State):
    cdef set[Symbol] _lookaheads