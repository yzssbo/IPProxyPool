class A(object):

    def __init__(self, a=None, b='-1', c=2, d=None):
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __getattr__(self, item):
        return item

    def insert(self):
        print('insert')
        pass

    def __str__(self):
        return ('a:{}, b:{}, c:{}, d:{}'.format(self.a, self.b, self.c, self.d))


if __name__ == '__main__':
    test = A()

    test.insert()
