from sympy import symbols, Symbol, Function, integrate, exp, Piecewise, simplify
from sympy.parsing.sympy_parser import parse_expr
import matplotlib.pyplot as mp


delta = 0.9
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

    def plug(self, thread, name=None):
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
        letter = other_node.plug(new_thread, name)
        self._output_thread[letter] = new_thread

    def get_out_value(self, t, type=None):
        return None

    def render_answer(self, answer, t):
        try:
            answer.free_symbols
        except:
            return answer
        for symb in self._input_thread:
            if symb in answer.free_symbols:
                answer = answer.subs({symb: self._input_thread[symb].value(t)})
        return answer

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

            answer = list(self._data_table.values())[-1]
            for cur_t_index in range( list(self._data_table)[-1] + 1, t + 1):

                temp = self._input_rate((cur_t_index - 1) * delta) - self._output_rate((cur_t_index - 1) * delta)
                temp = self.render_answer(temp, (cur_t_index - 1) * delta)
                #temp = temp if temp > 0 else 0

                answer += delta * temp
                self._data_table[cur_t_index] = answer

        return self._data_table[t]

    def get_out_value(self, t, type=None):
        if type == 'info':
            return self.lelvel_equasion(t)

        return self.render_answer(self._output_rate(t), t)

class Exp_Delay(Level):
    def __init__(self, strt_level, input_rate, average_time):
        super().__init__(strt_level, input_rate, None)
        self._output_rate = self.exp_delay
        self._average_time = average_time

    def exp_delay(self, t):
        return self.lelvel_equasion(t) / self._average_time

class DeepExPDelay(Node):
    def __init__(self, deep, input_rate, average_time):
        super().__init__()
        self._delaylist = []
        delay = Exp_Delay(0,input_rate,average_time)
        self._delaylist.append(delay)
        for i in range(deep - 1):
            new_delay = Exp_Delay(0, 'DLE' + str(i), average_time)
            delay.conect_with(new_delay, 'delay' , 'DLE' + str(i))
            delay = new_delay
            self._delaylist.append(delay)

    def lelvel_equasion(self, t):
        return sum(map(lambda exp: exp.lelvel_equasion(t), self._delaylist))

    def get_out_value(self, t, type=None):
        if type == 'info':
            return self.lelvel_equasion(t)

        return self.render_answer(self._delaylist[-1].get_out_value(t), t)

    def plug(self, thread, name=None):
        return self._delaylist[0].plug(thread=thread, name = name)

'''
TS = Source('3')
#Test = Exp_Delay(0,'TS',3)

Test = DeepExPDelay(3,'TS',3)

TS.conect_with(Test,'order', 'TS')


mp.plot([TS.get_out_value(step * delta) for step in range(100)], label = 'вход')
mp.plot([Test.get_out_value(step * delta) for step in range(100)], label = 'выход')
mp.legend()
mp.show()
'''

'''
RRR = Source('Piecewise((t, t < 5), (1/t, True) )')
#SRR = Source('5')
#----------#
SSD = Source('1')
DFD = Source('1')

UOR = Level(0, 'RRR', 'SSR')
IAR = Level(0, 'SRR', 'SSR')
RSR = Level(0, 'RRR / DRR', 'RSR / DRR')

SSR = Chouse('Min(STR,NIR)')
#----------#
PDR = Chouse('RRR + 1/DIR * ( (IDR - IAR) + (LDR - LAR) + (UOR - UNR))')


STR = Halt('UOR / DFR')
NIR = Halt('IAR / DT')
DFR = Halt('DHR + DUR * IDR / IAR')
IDR = Halt('AIR * RSR')
#----------#
UNR = Halt('RSR * (DHR +DUR)')
LDR = Halt('RSR * (DCR + DMR + DFD + DTR)')
LAR = Halt('CPR + PMR + UOD + MTR')

DHR = Constant('1')
DUR = Constant('1')
DRR = Constant('1')
DT  = Constant('1')
AIR = Constant('1')
DIR = Constant('1')

File = Targer('UOR')
ToCosumers = Targer('IAR')
#------------------------#


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





'''
'''
mp.plot([IAR.get_out_value(step * delta, 'info') for step in range(100)])
mp.plot([UOR.get_out_value(step * delta, 'info') for step in range(100)])

mp.show()

mp.plot([ToCosumers.get_result(step * delta) for step in range(100)])
mp.show()
'''






RRR = Source('3')
SRR = Source('Piecewise( (2, t > 2), (2, t < 1), (10,True) )')

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


steps = 50

t_axis = [step * delta for step in range(steps)]

fig, ax1 = mp.subplots()


# Запасы розницы
ax1.plot(t_axis,[IAR.get_out_value(step * delta, 'info') for step in range(steps)], label='Запасы розницы')
# Заказы, еще не выполненные розничным звеном (единицы)
ax1.plot(t_axis,[UOR.get_out_value(step * delta, 'info') for step in range(steps)], label='Еще не выполненные заказы')
mp.legend()

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis


# Поток заказов
ax2.plot(t_axis,[RRR.get_out_value(step * delta) for step in range(steps)], label="Поток заказов", color='green')
# Товары от опта
ax2.plot(t_axis,[SRR.get_out_value(step * delta) for step in range(steps)], label="Товары от оптовой базы", color='red')


# Продоно
ax2.plot(t_axis,[ToCosumers.get_result(step) for step in range(steps)], label="Отгрузка товаров", color='black')

mp.legend(loc='lower right')

mp.show()


mp.show()