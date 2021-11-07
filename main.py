from sympy import symbols, Symbol, Function, integrate, exp, Piecewise
from sympy.parsing.sympy_parser import parse_expr



class Thread():
    def __init__(self, out_node,in_node, type):
        self._in_node = in_node
        self._out_node = out_node
        self.type = type

    @property
    def value(self):
        return self._out_node.get_out_value(self.type)

class Node():
    def __init__(self):
        self._input_thread = {}
        self._output_thread = {}

    def _plug(self, thread,name = None):
        if name is None:
            name = self._get_free_name()
        self._input_thread[name] = thread
        return name

    def _get_free_name(self):
        index = 0
        while ('in_' + str(index) in self._input_thread):
            index += 1
        return 'in_' + str(index)

    def conect_with(self, other_node, thread):
        new_thread = Thread(self, other_node ,thread)
        letter = other_node._plug(new_thread)
        self._output_thread[letter] = new_thread

    def get_out_value(self, type = None):
        return None

    def exchange_letter(self, expr):
        for symb in expr.free_symbols:
            if (symb in self._input_thread):
                expr.sub({symb: self._input_thread[symb]})
        return expr

class Constant(Node):
    def __init__(self, constant_value):
        super().__init__()
        self._value = constant_value

    def get_out_value(self, type = None):
        return self._value

class Level(Node):
    def __init__(self, strt_level, input_rate, output_rate):
        super().__init__()
        self._strt_level = strt_level
        try:
            self._value_letter = list(input_rate.free_symbols)[0]
        except:
            self._value_letter = symbols('t')
        self._input_rate = input_rate
        self._output_rate = output_rate

    def lelvel_equasion(self):
        return self._strt_level + integrate(self._input_rate - self._output_rate, (self._value_letter, 0, self._value_letter))

class Exp_Delay(Level):
    def __init__(self, strt_level, input_rate, average_time):
        super().__init__(strt_level, input_rate, None)
        self._average_time = average_time
        self._output_rate = self.exp_delay()

    def lelvel_equasion(self):
        teil_exp = self._strt_level + integrate(self._input_rate, (self._value_letter, 0 , self._value_letter) )
        sub_letter = symbols('x')
        return teil_exp - 1/self._average_time * integrate(exp(-1/self._average_time * (self._value_letter- sub_letter)) * teil_exp.subs({self._value_letter: sub_letter}), (sub_letter,0,self._value_letter))

    def lelvel_equasion_(self):
        teil_exp = self._strt_level + integrate(self._input_rate, (self._value_letter, 0 , self._value_letter) )
        x = symbols('x')
        s = symbols('s')
        r_exp = self._average_time * exp(integrate( self._average_time.subs({self._value_letter: s}) ,(s,x,self._value_letter)) )

        return teil_exp - 1 * integrate( r_exp * teil_exp.subs({self._value_letter: x}), (x,0,self._value_letter))

    def exp_delay(self):
        return self.lelvel_equasion()/self._average_time


UOR = Level(0,parse_expr('3'),parse_expr('3'))
r1 = Exp_Delay
