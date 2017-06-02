from math import sin, cos, atan, pi
import math
import time


class calculator():
    def __init__(self, step_size=3):
        self.sin_d = {}
        self.cos_d = {}
        self.atan_d = {}
        self.len_step = step_size
        step = 10**-self.len_step
        for i in range(int(-2*pi/step), int((2*pi+step)/step), 1):
            i = i * step
            self.sin_d[i] = sin(i)
            self.cos_d[i] = cos(i)
        for i in range(int(-20/step), int(20/step), 1):
            self.atan_d[i*step] = atan(i)

        keys_s = self.sin_d.keys()
        keys_c = self.cos_d.keys()
        keys_a = self.atan_d.keys()

        self.sin_bounds = (min(keys_s), max(keys_s))
        self.cos_bounds = (min(keys_c), max(keys_c))
        self.atan_bounds = (min(keys_a), max(keys_a))

    def sin(self, num):
        num = num % (2*pi)
        num = round(self.len_step, num)
        return self.sin_d[num]

    def cos(self, num):
        num = num % (2*pi)
        num = round(self.len_step, num)
        return self.cos_d[num]

    def atan(self, num):
        if num > 0:
            if num > self.atan_bounds[1]:
                return self.atan_d[self.atan_bounds[1]]
        else:
            if num < self.atan_bounds[0]:
                return self.atan_d[self.atan_bounds[0]]

        num = round(self.len_step, num)
        return self.atan_d[num]


def round(number_of_zeros, num):
    if type(num) is list:
        to_return = []
        for i in num:
            to_return.append(round(number_of_zeros, i))
        return to_return
    else:
        factor = 10**number_of_zeros
        return int(num * factor) / factor


if __name__ == "__main__":
    calc = calculator()
    calc.sin(-1.23456789)
    calc.sin(-1.23456789-2*pi)
    time_tot = 0
    inc = 0
    for i in range(10000):
        old = time.clock()
        math.atan(1.23456)
        new = time.clock()
        time_tot += new - old
        inc += 1

    built_in = time_tot / inc
    # print('built-in', time_tot / inc)

    time_tot = 0
    inc = 0
    for i in range(10000):
        old = time.clock()
        calc.atan(1.23456)
        new = time.clock()
        time_tot += new - old
        inc += 1

    updated = time_tot / inc
    print(updated - built_in)
