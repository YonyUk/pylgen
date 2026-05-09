# cython: language_level=3, boundscheck=False, wraparound=False

from typing import Tuple,List,Dict

cdef class Table:

    def __init__(self):
        self._table = {}
    
    @property
    def entries(self) -> List[Tuple[str,str]]:
        cdef list result = list(self._table.keys())
        return result
    
    @property
    def values(self) -> List[str]:
        cdef list result = list(self._table.values())
        return result
    
    @property
    def items(self) -> List[Tuple[str,str,str]]:
        cdef list result = []
        cdef tuple k
        cdef str v,a,b
        for k,v in self._table.items():
            a = <str>k[0]
            b = <str>k[1]
            result.append((a,b,v))
        return result
    
    cpdef dict to_dict(self):
        cdef dict result = {}
        cdef tuple k
        cdef str v,a,b
        for k, v in self._table.items():
            a = <str>k[0]
            b = <str>k[1]
            result[(a,b)] = v
        return result
    
    cpdef void from_dict(self, dict data):
        cdef tuple k
        cdef str v
        # Se usa .items() explícito (el original omite la llamada)
        for k, v in data.items():
            self._table[k] = v

    def __getitem__(self, coord: Tuple[str, str]) -> str:
        return self._table[coord]

    def __setitem__(self, coord: Tuple[str, str], value: str) -> None:
        if len(coord) != 2:
            raise ValueError()
        # Uso de isinstance en lugar de type() por claridad y velocidad
        if not isinstance(coord[0], str) or not isinstance(coord[1], str) or not isinstance(value, str):
            raise ValueError('All values must be strings')
        self._table[coord] = value

    def __delitem__(self, coord: Tuple[str, str]) -> None:
        if len(coord) != 2:
            raise ValueError()
        if not isinstance(coord[0], str) or not isinstance(coord[1], str):
            raise ValueError('All values must be strings')
        del self._table[coord]