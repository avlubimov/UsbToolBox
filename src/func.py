from functools import reduce


def merge(*args):
    r = {}
    for d in args:
        for k, v in d.items():
            r[k] = v
    return r


def _reduce_(wrapper=lambda x: x):
    """
    Декоратор с параметром запускает функцию в цикле reduce
    :param wrapper: враппер для оборачивания вывода. dict, list по умолчанию ничего
    :return: декоратор без параметра
    """
    def decorator(func):
        """
        Деократор для запускает функцию в цикле reduce
        :param func: sункция
        :return: фцгкцию
        """
        def inner(sequence, initial=None):
            """
            Контейнер для запуска reduce
            :param sequence:  Последовательность по которой запускать функцию
            :param initial:  Начальное значение, по умолчанию нет
            :return: результат Reduce
            """
            r = reduce(func, sequence) if initial is None else reduce(func, sequence, initial)
            return wrapper(r)
        return inner
    return decorator


def _map_(wrapper=lambda x: x):
    def decorator(func):
        def inner(sequence):
            return wrapper(map(func, sequence))
        return inner
    return decorator


def _filter_(wrapper=lambda x: x):
    def decorator(func):
        def inner(sequence):
            """

            :param sequence: Последовательность для фильтрации
            :return:
            """
            return wrapper(filter(func, sequence))
        return inner
    return decorator


@_reduce_(wrapper=dict)
def merge_dict(r: list, d: dict):
    return r + list(d.items())


@_map_(wrapper=list)
def map_dict(x):
    return x[1]


@_filter_(wrapper=dict)
def filter_dict(el):
    # print (el)
    k, v = el
    # print (k,v)
    if k != 2:
        return True
    else:
        return False


A = {0: "A", 1: 1, 2: 2}
B = {0: "B", 3: 3, 4: 4}
C = {0: "C", 5: 5, 6: 6}

R0 = {**A, **B, **C}
R1 = merge(A, B, C)
R2 = merge_dict((A, B, C), initial=[])
R3 = filter_dict(A.items())

for t in R0, R1, R2, R3:
    print(t)

# print(map_dict(A.items()))
# print(help(map_dict))
