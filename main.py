from sympy import symbols, Symbol, Function, integrate, exp, Piecewise, simplify
from sympy.core.tests.test_sympify import numpy
from sympy.parsing.sympy_parser import parse_expr
import matplotlib.pyplot as mp
import matplotlib.animation as animation


delta = 0.01
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
        self.free_symbs = []

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

    def parse_free_sybs(self, *exprs):
        for expr in exprs:
            for symb in parse_expr(expr).free_symbols:
                if symb not in self.free_symbs:
                    self.free_symbs.append(symb)

class Halt(Node):

    def __init__(self, operation):
        super().__init__()
        self.parse_free_sybs(operation)
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
        self.parse_free_sybs(constant_value)
        self._value = parse_expr(constant_value)

    def get_out_value(self, t, type=None):
        return self._value

class Source(Node):
    def __init__(self, output):
        super().__init__()
        self.parse_free_sybs(output)
        self._output = lambda t: parse_expr(output).subs({time: t})

    def get_out_value(self, t, type=None):
        answer = self._output(t)
        answer = answer.subs({symb: self._input_thread[symb].value((t) * delta) for symb in self._input_thread if symb in answer.free_symbols})
        return answer

class Targer(Node):
    def __init__(self, input):
        super().__init__()
        self.parse_free_sybs(input)
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
        self.parse_free_sybs(input_rate, output_rate)
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
        if type == 'temp':
            return self.render_answer(self._output_rate(t), t)
        return self.lelvel_equasion(t)

class Exp_Delay(Level):
    def __init__(self, strt_level, input_rate, average_time):
        super().__init__(strt_level, input_rate, '0')
        self.parse_free_sybs(input_rate)
        self._output_rate = self.exp_delay
        self._average_time = average_time

    def exp_delay(self, t):
        return self.lelvel_equasion(t) / self._average_time

class DeepExPDelay(Node):
    def __init__(self, deep, input_rate, average_time):
        super().__init__()
        self.parse_free_sybs(input_rate)

        self._delaylist = []
        delay = Exp_Delay(0,input_rate,average_time)
        self._delaylist.append(delay)
        for i in range(deep - 1):
            new_delay = Exp_Delay(0, 'DLE' + str(i), average_time)
            delay.conect_with(new_delay, 'temp' , 'DLE' + str(i))
            delay = new_delay
            self._delaylist.append(delay)

    def lelvel_equasion(self, t):
        return sum(map(lambda exp: exp.lelvel_equasion(t), self._delaylist))

    def get_out_value(self, t, type=None):
        if type == 'temp':
            return self.render_answer(self._delaylist[-1].get_out_value(t, 'temp'), t)
        return self.lelvel_equasion(t)

    def plug(self, thread, name=None):
        return self._delaylist[0].plug(thread=thread, name = name)

class FacadeModel():
    def __init__(self):
        self._nodes = {}

    def __setitem__(self, key, value):
        self._nodes[symbols(key)] = value

    def __getitem__(self, item):
        return self._nodes[symbols(item)]

    def auto_connect(self):
        for node in self._nodes:
            for symb in self._nodes[node].free_symbs:
                if symb in self._nodes:
                    self._nodes[symb].conect_with(self._nodes[node], 'default', str(symb))

    def made_default_constant(self, *names, default_value = '1'):
        for name in names:
            self[name] = Constant(default_value)

    def made_exp_delay(self, name, name_temp, deep, cons, input_thread):
        self[name] = DeepExPDelay(deep,input_thread, cons)
        self[name_temp] = Halt(name + 'temp')
        self[name].conect_with(self[name_temp], 'temp', name + 'temp')

nc = FacadeModel()


nc['UOR'] = Level(0, 'RRR', 'SSR')
nc['IAR'] = Level(0, 'SRR', 'SSR')
nc['RSR'] = Level(0, 'RRR / DRR', 'RSR / DRR')

nc['SSR'] = Chouse('Min(STR,NIR)')
nc['PDR'] = Chouse('RRR + 1/DIR * ((IDR - IAR) + (LDR - LAR) + (UOR - UNR) )')

nc['STR'] = Halt('UOR / DFR')
nc['NIR'] = Halt('IAR / DT')
nc['DFR'] = Halt('DHR + DUR * IDR / (IAR + 0.0001)')
nc['IDR'] = Halt('AIR * RSR')
nc['UNR'] = Halt('RSR * (DHR + DUR)')
nc['LAR'] = Halt('CPR + PMR + UOD + MTR')
nc['LDR'] = Halt('RSR * (DCR + DMR + DFD + DTR)')


nc.made_exp_delay('CPR', 'PSR', 1, 1,'PDR')
nc.made_exp_delay('PMR', 'RRD', 1, 1,'PSR')
nc.made_exp_delay('MTR', 'SRR', 1, 1,'SSD')


nc['DHR'] = Constant('1')
nc['DUR'] = Constant('1')
nc['DRR'] = Constant('1')
nc['AIR'] = Constant('1')
nc['DIR'] = Constant('1')
nc['DCR'] = Constant('1')
nc['DMR'] = Constant('1')
nc['DTR'] = Constant('1')

File = Targer('UOR')
ToCosumers = Targer('IAR')
##############

nc.made_default_constant('DID', 'DRD', 'DUD', 'DHD', 'AID', 'DMD', 'DCD', 'DTD', default_value= '1')


nc['LDD'] = Halt('RSD * (DCD + DMD + DFF + DTD)')
nc['UND'] = Halt('RSD * (DHD + DUD)')
nc['IDD'] = Halt('AID  * RSD')
nc['DFD'] = Halt('DHD + DUD * IDD/ (IAD+ 0.0001)')
nc['STD'] = Halt('UOD / DFD')
nc['NID'] = Halt('IAD/DT')
nc['LAD'] = Halt('CPD + PMD + UOF + MTD')


nc['RSD'] = Level(0, 'RRD/DRD', 'RSD/DRD')
nc['UOD'] = Level(0, 'RRD', 'SSD')
nc['IAD'] = Level(0, 'SRD', 'SSD')


nc['SSD'] = Chouse('Min(STD, NID)')
nc['PDD'] = Chouse('RRD + 1/DID * ((IDD - IAD)+(LDD - LAD)+(UOD - UND))')


nc.made_exp_delay('MTD','SRD',3,1, "SSF")
nc.made_exp_delay('PMD','RRF',3,1, "PSD")
nc.made_exp_delay('CPD','PSD',3,1, "PDD")


nc.made_default_constant('DHF','AIF', 'DUF', 'DRF','DCF', 'DPF',default_value= '1')
nc['DIF'] = Constant('1')
nc['DT'] = Constant(str(delta))
nc['ALF'] = Constant('50000')


nc['LAF'] = Halt('CPF + OPF')
nc['LDF'] = Halt('RSF * (DCF + DPF)')
nc['MWF'] = Halt('RRF + 1/DIF * ((IDF - IAF) + (LDF - LAF) + (UOF - UNF))')
nc['UNF'] = Halt('RSF * (DHF + DUF)')
nc['IDF'] = Halt("AIF * RSF")
nc['DFF'] = Halt('DHF + DUF * IDF / ( IAF + 0.0001)')
nc['STF'] = Halt('UOF/DFF')
nc['NIF'] = Halt('IAF/DT')

nc['RSF'] = Level(0,'RRF/DRF','RSF/DRF')
nc['UOF'] = Level(0,'RRF','SSF')
nc['IAF'] = Level(0,'SRF','SSF')

nc.made_exp_delay('OPF','SRF',3,1, "MOF")
nc.made_exp_delay('CPF','MOF',3,1, "MDF")

nc['SSF'] = Chouse('Min(STF, NIF)')
nc['MDF'] = Chouse('Min(MWF, ALF)')
##############




nc['RRR'] = Source('1000')
nc['DHR'] = Constant('1')
nc['DHD'] = Constant('1')
nc['DHF'] = Constant('1')
nc['DUR'] = Constant('0.4')
nc['DUD'] = Constant('0.6')
nc['DUF'] = Constant('1')
nc['AIR'] = Constant('8')
nc['AID'] = Constant('6')
nc['AIF'] = Constant('4')
nc['DRR'] = Constant('8')
nc['DRD'] = Constant('8')
nc['DRF'] = Constant('8')
nc['DIR'] = Constant('4')
nc['DID'] = Constant('4')
nc['DIF'] = Constant('4')
nc['DCR'] = Constant('3')
nc['DCD'] = Constant('2')
nc['DCF'] = Constant('1')
nc['DMR'] = Constant('0.5')
nc['DMD'] = Constant('0.5')
nc['DTR'] = Constant('1')
nc['DTD'] = Constant('2')


nc.auto_connect()

steps = 140
'''

t_axis = [step * delta for step in range(steps)]
fig, ax1 = mp.subplots()


#ax1.plot(t_axis,[nc['RRD'].get_out_value(step * delta) for step in range(steps)], label='Заказы')



def init():
    return one, two, free, four

def animate(i):
    one.set_data((10 + i) * delta , nc['RRR'].get_out_value((10 + i) * delta))
    two.set_data((10 + i) * delta, nc['SSF'].get_out_value((10 + i) * delta))
    free.set_data((10 + i) * delta, nc['SSD'].get_out_value((10 + i) * delta))
    four.set_data((10 + i) * delta, nc['SSR'].get_out_value((10 + i) * delta))
    return one, two, free, four

mp.legend()

ani = animation.FuncAnimation(fig, animate, interval=1000, init_func=init, blit=True, save_count=10)


mp.show()
'''





mp.ion()

# Создание окна и осей для графика
fig, ax = mp.subplots()

# Установка отображаемых интервалов по осям
ax.set_ylim(0, 10000)

# Отобразить график фукнции в начальный момент времени

ax.plot([step * delta for step in range( 10)], [nc['RRR'].get_out_value(step * delta) for step in range(10)], label='Заказы' , color = 'red')
ax.plot([step * delta for step in range(10)], [nc['SSF'].get_out_value(step * delta) for step in range(10)], label='Производство', color = 'blue')
ax.plot([step * delta for step in range(10)], [nc['SSD'].get_out_value(step * delta) for step in range(10)], label='Оптовые продажи', color = 'green')
ax.plot([step * delta for step in range(10)], [nc['SSR'].get_out_value(step * delta) for step in range(10)], label='Розничные продажи', color = 'black')
mp.legend()



# У функции gaussian будет меняться параметр delay (задержка)
for delay in range(0, 2000, 10):
    ax.set_xlim(0, delay * delta)

    ax.plot([step * delta for step in range(10 + delay)], [nc['RRR'].get_out_value(step * delta) for step in range(10 + delay)],label='Заказы', color = 'red')
    ax.plot([step * delta for step in range(10 + delay)], [nc['SSF'].get_out_value(step * delta) for step in range(10 + delay)],label='Производство', color = 'blue')
    ax.plot([step * delta for step in range(10 + delay)], [nc['SSD'].get_out_value(step * delta) for step in range(10 + delay)], label='Оптовые продажи', color = 'green')
    ax.plot([step * delta for step in range(10 + delay)], [nc['SSR'].get_out_value(step * delta) for step in range(10 + delay)],label='Розничные продажи', color = 'black')


    # Отобразить новые данный
    fig.canvas.draw()
    fig.canvas.flush_events()



# Отключить интерактивный режим по завершению анимации
mp.ioff()
mp.show()