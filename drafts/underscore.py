from utils import type_utils


class Underscore(object):
    def __init__(self):
        self._f = []

    def __getattr__(self, method):
        print(method)
        def wrapper(*args, **kwargs):
            self._f.append(lambda x: x.__getattribute__(method)(*args, **kwargs))
            return self
        return wrapper

    def __call__(self, *args, **kwargs):
        result = args
        for f in self._f:
            try:
                result = f(*result)
            except TypeError:
                result = f(result)
        print(result)

    # def __getitem__(self, item):
    #     return lambda x: x[item]


_ = Underscore()


class Elem(type_utils.Printable):
    def __init__(self, name):
        self._name = name

    def name(self, msg):
        return msg + ':' + self._name


class Container(type_utils.Printable):
    def __init__(self, elems):
        self._elems = elems

    def get(self, index):
        return self._elems[index]


class List(type_utils.Printable):
    def __init__(self, l):
        self._l = l

    def get(self, index):
        return self._l[index]

    def map(self, f):
        return list(map(f, self._l))


if __name__ == '__main__':
    elems1 = List([Elem('11'), Elem('12'), Elem('13')])
    elems2 = List([Elem('21'), Elem('22')])
    containers = List([elems1, elems2])
    f = _.get(0).map(_.get(0))   # .name('hi'))

    print(f(containers))
