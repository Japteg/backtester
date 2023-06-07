class A:
    def __init__(self):
        self.a = ''
        self.b = 2
        self.c = [1, 2, 3]
        self.d = {}

        # self.hse = B(self.a, self.b, self.c, self.d)
        self.hse = {}
        c = C(self.hse)
        c.modify_instance()

    def print_items(self):
        # print(self.a)
        # print(self.b)
        # print(self.c)
        # print(self.d)
        # print(self.hse.a)
        # print(self.hse.b)
        # print(self.hse.c)
        # print(self.hse.d)
        print(self.hse)


class B:
    def __init__(self, a, b, c, d):
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def modify(self):
        self.a = 'modeified in B'
        self.b += 1
        self.c = [3, 2,  1]
        self.d = {
            'class_name': 'B'
        }


class C:
    def __init__(self, instance):
        self.instance = instance

    def modify_instance(self):
        # self.instance.update(
        #     new='new_val'
        # )
        self.instance = {
            'hel': 'lo'
        }


aa = A()
aa.print_items()
