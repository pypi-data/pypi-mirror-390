from enum import Enum


def extend_enum(inherited_enum):
    def wrapper(added_enum):
        joined = {}
        for item in inherited_enum:
            joined[item.name] = item.value
        for item in added_enum:
            joined[item.name] = item.value
        return Enum(added_enum.__name__, joined)

    return wrapper


if __name__ == '__main__':
    class Cats(Enum):
        SIBERIAN = 'siberian'
        SPHINX = 'sphinx'


    @extend_enum(Cats)
    class Animals(Enum):
        LABRADOR = 'labrador'
        CORGI = 'corgi'


    print(list(Animals))
