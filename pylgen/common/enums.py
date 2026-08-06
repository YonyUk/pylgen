from enum import StrEnum,EnumMeta

class TokenTypeMeta(EnumMeta):

    def __new__(metacls, cls, bases, classdict, **kwds):
        if cls != 'TokenType' and 'INVALID_TOKEN' not in classdict:
            classdict['INVALID_TOKEN'] = 'INVALID_TOKEN'
        return super().__new__(metacls,cls,bases,classdict,**kwds)

class TokenType(StrEnum,metaclass=TokenTypeMeta):
    pass