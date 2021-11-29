from sympy import symbols, parse_expr


time = symbols('t')
delta = 0.1


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
        self._operation_expr = parse_expr(operation)
        self._operation = lambda t: self._operation_expr.subs({time: t})

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
        if constant_value is str:
            self._value = parse_expr(constant_value)
        else:
            self._value = constant_value

    def get_out_value(self, t, type=None):
        return self._value


class Source(Node):
    def __init__(self, output):
        super().__init__()
        self.parse_free_sybs(output)
        self._output_exp = parse_expr(output)
        self._output = lambda t: self._output_exp.subs({time: t})

    def get_out_value(self, t, type=None):
        return self.render_answer(self._output(t), t)


class Targer(Node):
    def __init__(self, input):
        super().__init__()
        self.parse_free_sybs(input)
        self._input_rate_exp = parse_expr(input)
        self._input_rate = lambda t: self._input_rate_exp.subs({time: t})

    def get_result(self, t):
        return self.render_answer(self._input_rate(t), t)


class Level(Node):
    def __init__(self, strt_level, input_rate, output_rate):
        super().__init__()
        self.parse_free_sybs(strt_level, input_rate, output_rate)
        self._strt_level = parse_expr(strt_level)

        self._input_rate_exp = parse_expr(input_rate)
        self._input_rate = lambda t: self._input_rate_exp.subs({time: t})

        self._output_rate_exp = parse_expr(output_rate)
        self._output_rate = lambda t: self._output_rate_exp.subs({time: t})

        self._data_table = {}

    def lelvel_equasion(self, t):
        t = int(round(t / delta, 0))
        if t == 0:
            self._data_table[0] = self.render_answer(self._strt_level, 0)


        if t not in self._data_table:
            answer = list(self._data_table.values())[-1]
            for cur_t_index in range(list(self._data_table)[-1] + 1, t + 1):
                temp = self._input_rate((cur_t_index - 1) * delta) - self._output_rate((cur_t_index - 1) * delta)
                temp = self.render_answer(temp, (cur_t_index - 1) * delta)

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
    def __init__(self, start, deep, input_rate, average_time):
        super().__init__()
        self.parse_free_sybs(input_rate, start)

        self._delaylist = []
        delay = Exp_Delay(start, input_rate, average_time)
        self._delaylist.append(delay)
        for i in range(deep - 1):
            new_delay = Exp_Delay('0', 'DLE' + str(i), average_time)
            delay.conect_with(new_delay, 'temp', 'DLE' + str(i))
            delay = new_delay
            self._delaylist.append(delay)

    def lelvel_equasion(self, t):
        return sum(map(lambda exp: exp.lelvel_equasion(t), self._delaylist))

    def get_out_value(self, t, type=None):
        if type == 'temp':
            return self.render_answer(self._delaylist[-1].get_out_value(t, 'temp'), t)
        return self.lelvel_equasion(t)

    def plug(self, thread, name=None):
        return self._delaylist[0].plug(thread=thread, name=name)