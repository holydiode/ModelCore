from sympy import symbols, Symbol, Function, integrate, exp, Piecewise
from sympy.parsing.sympy_parser import parse_expr
import matplotlib.pyplot as mp


delta = 0.1
raund_value = 1
time = symbols('t')


class Thread():
    def __init__(self, out_node, in_node, type):
        self._in_node = in_node
        self._out_node = out_node
        self.type = type

    def value(self, t):
        return self._out_node.get_out_value(t, self.type)

class Node():
    def __init__(self):
        self._input_thread = {}
        self._output_thread = {}

    def _plug(self, thread, name=None):
        if name is None:
            name = self._get_free_name()
        name = symbols(name)
        self._input_thread[name] = thread
        return name

    def _get_free_name(self):
        index = 0
        while ('in_' + str(index) in self._input_thread):
            index += 1
        return 'in_' + str(index)

    def conect_with(self, other_node, thread, name=None):
        new_thread = Thread(self, other_node, thread)
        letter = other_node._plug(new_thread, name)
        self._output_thread[letter] = new_thread

    def get_out_value(self, t, type=None):
        return None

class Halt(Node):

    def __init__(self, operation):
        super().__init__()
        self._operation = lambda t: parse_expr(operation).subs({time: t})

    def get_out_value(self, t, type=None):
        answer = self._operation(t)
        for symb in self._input_thread:
            if symb in answer.free_symbols:
                answer = answer.subs({symb: self._input_thread[symb].value(t)})
                a = 1

        return answer

class Chouse(Halt):
    def __init__(self, operation):
        super().__init__(operation)

class Constant(Node):
    def __init__(self, constant_value):
        super().__init__()
        self._value = parse_expr(constant_value)

    def get_out_value(self, t, type=None):
        return self._value

class Source(Node):
    def __init__(self, output):
        super().__init__()
        self._output = lambda t: parse_expr(output).subs({time: t})

    def get_out_value(self, t, type=None):
        answer = self._output(t)
        answer = answer.subs({symb: self._input_thread[symb].value((t) * delta) for symb in self._input_thread if symb in answer.free_symbols})
        return answer

class Targer(Node):
    def __init__(self, input):
        super().__init__()
        self._input_rate = lambda t: parse_expr(input).subs({time: t})

    def get_result(self, t):
        answer = self._input_rate(t)
        for symb in self._input_thread:
            if symb in answer.free_symbols:
                answer = answer.subs({symb: self._input_thread[symb].value(t)})

        return answer

class Level(Node):
    def __init__(self, strt_level, input_rate, output_rate):
        super().__init__()
        self._strt_level = strt_level
        self._value_letter = time
        self._input_rate = lambda t: parse_expr(input_rate).subs({time: t})
        self._output_rate = lambda t: parse_expr(output_rate).subs({time: t})
        self._data_table = {0: self._strt_level}

    def lelvel_equasion(self, t):
        t = int(round(t / delta, 0))

        if t not in self._data_table:

            answer = self._strt_level
            for cur_t_index in range( list(self._data_table.keys())[-1] + 1, t + 1):


                answer += delta * (self._input_rate((cur_t_index - 1) * delta) - self._output_rate((cur_t_index - 1) * delta))
                answer = answer.subs({symb: self._input_thread[symb].value((cur_t_index - 1) * delta) for symb in self._input_thread if symb in answer.free_symbols })


                self._data_table[cur_t_index] = answer

        return repr(self._data_table[t])

    def get_out_value(self, t, type=None):
        if type == 'info':
            return self.lelvel_equasion(t)

        answer = self._output_rate(t)
        for symb in self._input_thread:
            if symb in answer.free_symbols:
                answer = answer.subs({symb: self._input_thread[symb].value(t)})

        return answer

class Exp_Delay(Level):
    def __init__(self, strt_level, input_rate, average_time):
        super().__init__(strt_level, input_rate, None)
        self._average_time = average_time
        self._output_rate = self.exp_delay()

    def lelvel_equasion(self, t):
        teil_exp = self._strt_level + integrate(self._input_rate, (self._value_letter, 0, self._value_letter))
        sub_letter = symbols('x')
        return teil_exp - 1 / self._average_time * integrate(
            exp(-1 / self._average_time * (self._value_letter - sub_letter)) * teil_exp.subs(
                {self._value_letter: sub_letter}), (sub_letter, 0, self._value_letter))

    '''
    def lelvel_equasion_(self):
        teil_exp = self._strt_level + integrate(self._input_rate, (self._value_letter, 0, self._value_letter))
        x = symbols('x')
        s = symbols('s')
        r_exp = self._average_time * exp(
            integrate(self._average_time.subs({self._value_letter: s}), (s, x, self._value_letter)))

        return teil_exp - 1 * integrate(r_exp * teil_exp.subs({self._value_letter: x}), (x, 0, self._value_letter))
    '''

    def exp_delay(self, t):
        return self.lelvel_equasion(t) / self._average_time


RRR = Source('2')
SRR = Source('1')


UOR = Level(0, 'RRR', 'SSR')
IAR = Level(0, 'SRR', 'SSR')
RSR = Level(0, 'RRR / DRR', 'RSR / DRR')

SSR = Chouse('Min(STR,NIR)')

STR = Halt('UOR / DFR')
NIR = Halt('IAR / DT')
DFR = Halt('DHR + DUR * IDR / IAR')
IDR = Halt('AIR * RSR')

DHR = Constant('1')
DUR = Constant('1')
DRR = Constant('1')
DT  = Constant('1')
AIR = Constant('1')


File = Targer('UOR')
ToCosumers = Targer('IAR')

RRR.conect_with(UOR,  'order',  "RRR")
RRR.conect_with(RSR,  'info',   "RRR")
UOR.conect_with(File, 'order',  "UOR")
UOR.conect_with(STR,  'info',   "UOR")
STR.conect_with(SSR,  'info',   "STR")
SSR.conect_with(UOR, 'info', 'SSR')
SSR.conect_with(IAR, 'info', 'SSR')
NIR.conect_with(SSR, 'info', 'NIR')
DT.conect_with(NIR, 'info', 'DT')
IAR.conect_with(ToCosumers, 'goods', 'IAR')
IAR.conect_with(NIR, 'info', 'IAR')
IAR.conect_with(DFR, 'info', 'IAR')
DFR.conect_with(STR, 'info', 'DFR')
DHR.conect_with(DFR, 'info', 'DHR')
DUR.conect_with(DFR, 'info', 'DUR')
IDR.conect_with(DFR, 'info', 'IDR')
AIR.conect_with(IDR, 'info', 'AIR')
DRR.conect_with(RSR, 'info', 'DRR')
RSR.conect_with(IDR, 'info', 'RSR')
RSR.conect_with(RSR, 'info', 'RSR')
SRR.conect_with(IAR, 'good', 'SRR')


mp.plot([IAR.get_out_value(step * delta) for step in range(100)])
mp.plot([UOR.get_out_value(step * delta) for step in range(100)])


mp.plot([ToCosumers.get_result(step * delta) for step in range(100)])
mp.plot([File.get_result(step * delta) for step in range(100)])


mp.show()