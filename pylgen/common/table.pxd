cdef class Table:
    cdef dict _table

    cpdef dict to_dict(self)
    cpdef void from_dict(self, dict data)
