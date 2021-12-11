import io
import os

from sympy import symbols
import matplotlib.pyplot as mp
from model_nodes import Halt, Chouse, Constant, Source, Targer, Level, DeepExPDelay, delta

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

    def made_default_constant(self, *names, default_value='1'):
        for name in names:
            self[name] = Constant(default_value)

    def made_exp_delay(self, name, name_temp, deep, cons, input_thread, start, prefer = '0'):
        self[name] = DeepExPDelay(start, deep, input_thread, cons, prefer)
        self[name_temp] = Halt(name + 'temp')
        self[name].conect_with(self[name_temp], 'temp', name + 'temp')

def init_nc():
    nc = FacadeModel()

    nc['UOR'] = Level('RSR * (DHR + DUR)', 'RRR', 'SSR')
    nc['IAR'] = Level('AIR * RSR', 'SRR', 'SSR')
    nc['RSR'] = Level('RRR', 'RRR / DRR', 'RSR / DRR')

    nc['SSR'] = Chouse('Piecewise(( STR, STR < NIR),(NIR, True))')
    nc['PDR'] = Chouse('RRR + 1/DIR * ((IDR - IAR) + (LDR - LAR) + (UOR - UNR) )')

    nc['STR'] = Halt('UOR / DFR')
    nc['NIR'] = Halt('IAR / DT')
    nc['DFR'] = Halt('DHR + DUR * IDR / IAR')
    nc['IDR'] = Halt('AIR * RSR')
    nc['UNR'] = Halt('RSR * (DHR + DUR)')
    nc['LAR'] = Halt('CPR + PMR + UOD + MTR')
    nc['LDR'] = Halt('RSR * (DCR + DMR + DFD + DTR)')

    nc.made_exp_delay('CPR', 'PSR', 1, 'DCR', 'PDR', 'DCR * RRR')
    nc.made_exp_delay('PMR', 'RRD', 1, 'DMR', 'PSR', 'DMR * RRR')
    nc.made_exp_delay('MTR', 'SRR', 1, 'DTR', 'SSD', 'DTR * RRR')


    File = Targer('UOR')
    ToCosumers = Targer('IAR')
    ##############


    nc['LDD'] = Halt('RSD * (DCD + DMD + DFF + DTD)')
    nc['UND'] = Halt('RSD * (DHD + DUD)')
    nc['IDD'] = Halt('AID  * RSD')
    nc['DFD'] = Halt('DHD + DUD * IDD/ IAD')
    nc['STD'] = Halt('UOD / DFD')
    nc['NID'] = Halt('IAD/DT')
    nc['LAD'] = Halt('CPD + PMD + UOF + MTD')

    nc['RSD'] = Level('RRR', 'RRD/DRD', 'RSD/DRD')
    nc['UOD'] = Level('RRR * (DHD + DUD)', 'RRD', 'SSD')
    nc['IAD'] = Level('AID * RRR', 'SRD', 'SSD')

    nc['SSD'] = Chouse('Piecewise(( STD, STD < NID),(NID, True))')
    nc['PDD'] = Chouse('RRD + 1/DID * ((IDD - IAD)+(LDD - LAD)+(UOD - UND))')

    nc.made_exp_delay('MTD', 'SRD', 1, 'DTD', "SSF", 'DTD * RRR')
    nc.made_exp_delay('PMD', 'RRF', 1, 'DMD', "PSD", 'DMD * RRR')
    nc.made_exp_delay('CPD', 'PSD', 1, 'DCD', "PDD", 'DCD * RRR')


    nc['LAF'] = Halt('CPF + OPF')
    nc['LDF'] = Halt('RSF * (DCF + DPF)')
    nc['MWF'] = Halt('RRF + 1/DIF * ((IDF - IAF) + (LDF - LAF) + (UOF - UNF))')
    nc['UNF'] = Halt('RSF * (DHF + DUF)')
    nc['IDF'] = Halt("AIF * RSF")
    nc['DFF'] = Halt('DHF + DUF * IDF / IAF')
    nc['STF'] = Halt('UOF/DFF')
    nc['NIF'] = Halt('IAF/DT')

    nc['RSF'] = Level('RRR', 'RRF/DRF', 'RSF/DRF')
    nc['UOF'] = Level('RRR * (DHF + DUF)', 'RRF', 'SSF')
    nc['IAF'] = Level('AIF  * RSF', 'SRF', 'SSF')

    nc.made_exp_delay('OPF', 'SRF', 1, 'DPF', "MOF", 'DPF * RRR')
    nc.made_exp_delay('CPF', 'MOF', 1, 'DCF', "MDF", 'DCF * RRR')

    nc['SSF'] = Chouse('Piecewise(( STF, STF < NIF),(NIF, True))')
    nc['MDF'] = Chouse('Piecewise(( MWF, MWF < ALF),(ALF, True))')
    ##############

    #входящий поток таваров (т/н)
    nc['RRR'] = Source('Piecewise(( 1000, t < 1), (1100, True) )')




    #минимальное запаздывание выполнение заказа розничным звеном (н)
    nc['DHR'] = Constant(1)
    #минимальное запаздывание выполнение заказа оптовым звеном (н)
    nc['DHD'] = Constant(1)
    #минимальное запаздывание выполнение заказа производством (н)
    nc['DHF'] = Constant(1)



    #запаздывание выполнения заказов рознечным звеном в связи с отсутсвием товаров на складе (н)
    nc['DUR'] = Constant(0.4)
    #запаздывание выполнения заказов отовым звеном в связи с отсутсвием товаров на складе (н)
    nc['DUD'] = Constant(0.6)
    #запаздывание выполнения заказов произдводством в связи с отсутсвием товаров на складе (н)
    nc['DUF'] = Constant(1)


    #количество недель, за которое средний темп поставок будет покрыт желаймым запасом на рознечном звене(н)
    nc['AIR'] = Constant(8)
    #количество недель, за которое средний темп поставок будет покрыт желаймым запасом на оптовом звене(н)
    nc['AID'] = Constant(6)
    #количество недель, за которое средний темп поставок будет покрыт желаймым запасом на производстве(н)
    nc['AIF'] = Constant(4)


    #усредненные требования к розничному звену (н)
    nc['DRR'] = Constant(8)
    #усредненные требования к оптовому звену (н)
    nc['DRD'] = Constant(8)
    #усредненные требования к производству (н)
    nc['DRF'] = Constant(8)


    #запаздывание регулирования запасов в рознечном звене(н)
    nc['DIR'] = Constant(4)
    #запаздывание регулирования запасов в оптовом звене(н)
    nc['DID'] = Constant(4)
    #запаздывание регулирования запасов в производстве(н)
    nc['DIF'] = Constant(4)

    #запаздывание оформление заказов в розничном звене(н)
    nc['DCR'] = Constant(3)
    #запаздывание оформление заказов в оптовом звене(н)
    nc['DCD'] = Constant(2)
    #запаздывание оформление заказов в производстве(н)
    nc['DCF'] = Constant(1)

    #почтовые запаздывание в оптовом сегменте(н)
    nc['DMR'] = Constant(0.5)
    #почтовые запаздывание в розничном сегменте(н)
    nc['DMD'] = Constant(0.5)

    #транспортное запаздывание в розничном сегменте(н)
    nc['DTR'] = Constant(1)
    #транспортное запаздывание в оптовом сегменте(н)
    nc['DTD'] = Constant(2)


    #запаздывание на подготовку производства предприятий
    nc['DPF'] = Constant(6)
    #Максимальная производящая мощность
    nc['ALF'] = Constant(20000)
    nc['DT'] = Constant(str(delta))


    nc.auto_connect()
    return nc


def animation_graphik(nc,nodes_name, lables, colors,y_lab ,max_lenght = 2):

    mp.ion()

    fig, ax = mp.subplots()
    mp.autoscale()

    tic = [step * delta for step in range(max_lenght)]

    dataset = [[nc[node_name].get_out_value(step * delta) for step in range(max_lenght)] for node_name in nodes_name]

    for set_index in range(len(dataset)):
        ax.plot(tic,dataset[set_index], label = lables[set_index], color = colors[set_index])

    ax.set_ylabel(y_lab)
    ax.set_xlabel('время (недели)')
    mp.gcf().set_size_inches(18, 6)

    mp.legend()

    stable = []

    for delay in range(0, 10000000, 10):
        tic.append( (delay + max_lenght) * delta)
        if (len(tic) > max_lenght):
            tic.pop(0)

        for set_index in range(len(dataset)):
            dataset[set_index].append(nc[nodes_name[set_index]].get_out_value((delay + max_lenght) * delta))
            if(len(dataset[set_index]) > max_lenght):
                dataset[set_index].pop(0)

        for set_index in range(len(dataset)):
            ax.plot(tic, dataset[set_index], label=lables[set_index], color=colors[set_index])



        if delay > 51:
            for nm , lablel, color in  zip(nodes_name,lables, colors):
                boop = True
                if nm not in stable:
                    for i in range(50):
                        a = (nc[nm].get_out_value((delay - i) * delta) - nc[nm].get_out_value((delay - i - 1) * delta))/(delta)
                        if abs(a) > nc[nm].get_out_value(0) / 2000:
                            boop = False
                    if boop:
                        stable.append(nm)
                        print(delay * delta)
                        ax.axvline(delay * delta,linestyle = '--' ,color = color)


        fig.canvas.draw()
        fig.canvas.flush_events()
        if len(stable) == len(nodes_name):
            break


    # Отключить интерактивный режим по завершению анимации
    mp.ioff()
    mp.show()



class Experement:
    def __init__(self, name, value, change):
        self.value = value
        self.change = change
        self.nc = init_nc()
        self.name = name
        self.nodes_target = ['SSF', 'SSD', 'SSR', 'RRR', 'RRD', 'RRF', 'IAF', 'IAD', 'IAR', 'UOR', 'UOD', 'UOF']
        self.nodes_name = ['Производство',
                           'Оптовые продажи',
                           'Розничные продажи',
                           'Заказы от розницы',
                           'Заказы от опта',
                           'Запасы на  производстве',
                           'Запасы на оптовой базе',
                           'Запасы на розничных складах',
                           'Незавершенные заказы потребителей',
                           'Незавершенные заказы розницы',
                           'Незавершенные заказы опта']
        self._max_delay = 10000
        self._radius = 50
        os.makedirs('Эксперементы/' + self.name, exist_ok=True)

    def get_pic_value(self):
        stable = {}
        for delay in range(0, self._max_delay, 10):
            if delay > 50 + 1:
                for nm  in self.nodes_target:
                    boop = True
                    if nm not in stable:
                        for i in range(50):
                            a = (self.nc[nm].get_out_value((delay - i) * delta) - self.nc[nm].get_out_value(
                                (delay - i - 1) * delta)) / (delta)
                            if abs(a) > self.nc[nm].get_out_value(0) / 2000:
                                boop = False
                        if boop:
                            stable[nm] = delay * delta

        return stable

    def made_change(self):
        self.nc[self.value] = Constant( self.change(self.nc[self.value].get_out_value(0)))
        self.nc.auto_connect()
        return self

    def graphik(self, name, nodes_name, lables, colors,y_lab):
        stable = self.get_pic_value()
        max_v = max(stable.values())

        fig, ax = mp.subplots()
        mp.autoscale()

        tic = [step * delta for step in range( int(max_v/delta) + 10)]

        dataset = [[self.nc[node_name].get_out_value(step * delta) for step in range(int(max_v/delta) + 10)] for node_name in nodes_name]

        for set_index in range(len(dataset)):
            ax.plot(tic, dataset[set_index], label=lables[set_index], color=colors[set_index])

        ax.set_ylabel(y_lab)
        ax.set_xlabel('время (недели)')
        mp.gcf().set_size_inches(18, 6)

        mp.legend()

        for nm, color in zip(nodes_name, colors):
            ax.axvline(stable[nm], linestyle='--', color=color)

        mp.savefig('Эксперементы/' + self.name + '/' + name + ".png")

    def made_graphik_array(self):
        self.graphik('1',
                    ['RRR', 'SSF', 'SSD', 'SSR'],
                    ['Заказы', 'Производство', 'Оптовые продажи', 'Розничные продажи'],
                    ['red', 'blue', 'green', 'black', 'orange'],
                    'товары в неделю (ед./неделя)'
                    )

        self.graphik( '2',
                      ['RRR', 'RRD', 'RRF'],
                      ['Заказы потребителей', 'Заказы от розницы', 'Заказы от опта'],
                      ['red', 'black', 'green', 'black'],
                      'заказы на товары (ед.)'
                      )

        self.graphik('3',
                     ['IAF', 'IAD', 'IAR'],
                     ['Запасы на  производстве', 'Запасы на оптовой базе', 'Запасы на розничных складах'],
                     ['blue', 'green', 'black', 'black'],
                     'товары (ед.)'
                     )

        self.graphik('4',
            ['UOR', 'UOD', 'UOF'],
            ['Незавершенные заказы потребителей', 'Незавершенные заказы розницы', 'Незавершенные заказы опта'],
            ['red', 'blue', 'green', ],
            'заказы на товар (ед.)'
        )

class ExperementPlotter:

    def __init__(self, name, value, default):
        self._name = name
        self._value = value
        self._default = default

    def made_expr_array(self):
        data = []
        a = Experement(self._name, self._value, lambda x:  x / 4).made_change()
        a.made_graphik_array()
        data.append(a.get_pic_value())
        data.append(Experement(self._name, self._value, lambda x:  x / 2).made_change().get_pic_value())
        data.append(Experement(self._name, self._value, lambda x:  x * 2).made_change().get_pic_value())
        data.append(Experement(self._name, self._value, lambda x:  x * 4).made_change().get_pic_value())

        return data

    def render(self):
        data = self.made_expr_array()
        file = io.open('templateTable.html', mode='r', encoding="utf-8")
        html_text = file.read()
        file.close()
        html_text = html_text.replace('{name_data}', self._name)
        html_text = html_text.replace('{name_param}', self._value)
        for i in range(4):
            for pn in self._default:
                v = data[i][pn] - self._default[pn]
                html_text = html_text.replace('{'+pn + '_d_' + str(i+1) +'}', ('+' if v > 0 else '') + str(v))
                html_text = html_text.replace('{'+pn + '_%_' + str(i+1) +'}', ('+' if v > 0 else '') + str( round(v/self._default[pn] * 100, 2) ))

            v = max(data[i].values()) - max(self._default.values())
            html_text = html_text.replace('{_d_' + str(i + 1) + '}',('+' if v > 0 else '') +  str(v))
            html_text = html_text.replace('{_%_' + str(i + 1) + '}',('+' if v > 0 else '') + str(round(v / max(self._default.values()) * 100, 2)))
        os.makedirs('Эксперементы/' + self._name, exist_ok=True)
        file = open('Эксперементы/' + self._name +'/' + self._name + '.html', 'w')
        file.write(html_text)
        file.close()


e = Experement("Изначальная модель", None, None)
e.made_graphik_array()
default = e.get_pic_value()
ExperementPlotter('запаздывание подготовки производства предприятий', 'DPF', default).render()

ExperementPlotter('минимальное запаздывание выполнение заказа розничным звеном', 'DHR', default).render()
ExperementPlotter('минимальное запаздывание выполнение заказа оптовым звеном', 'DHD', default).render()
ExperementPlotter('минимальное запаздывание выполнение заказа производством', 'DHF', default).render()

ExperementPlotter('запаздывание выполнения заказов рознечным звеном в связи с отсутсвием товаров на складе', 'DUR', default).render()
ExperementPlotter('запаздывание выполнения заказов отовым звеном в связи с отсутсвием товаров на складе', 'DUD', default).render()
ExperementPlotter('запаздывание выполнения заказов произдводством в связи с отсутсвием товаров на складе', 'DUF', default).render()

ExperementPlotter('количество недель, за которое средний темп поставок будет покрыт желаймым запасом на рознечном звене', 'AIR', default).render()
ExperementPlotter('количество недель, за которое средний темп поставок будет покрыт желаймым запасом на оптовом звене', 'AID', default).render()
ExperementPlotter('количество недель, за которое средний темп поставок будет покрыт желаймым запасом на производстве', 'AIF', default).render()


ExperementPlotter('усредненные требования к розничному звену', 'DRR', default).render()
ExperementPlotter('усредненные требования к оптовому звену', 'DRD', default).render()
ExperementPlotter('зусредненные требования к производству', 'DRF', default).render()

ExperementPlotter('запаздывание регулирования запасов в рознечном звене', 'DIR', default).render()
ExperementPlotter('запаздывание регулирования запасов в оптовом звене', 'DID', default).render()
ExperementPlotter('апаздывание регулирования запасов в производстве', 'DIF', default).render()

ExperementPlotter('запаздывание оформление заказов в розничном звене', 'DCR', default).render()
ExperementPlotter('запаздывание оформление заказов в оптовом звене', 'DCD', default).render()
ExperementPlotter('запаздывание оформление заказов в производстве', 'DCF', default).render()

ExperementPlotter('почтовые запаздывание в оптовом сегмент', 'DMR', default).render()
ExperementPlotter('почтовые запаздывание в розничном сегменте', 'DMD', default).render()

ExperementPlotter('транспортное запаздывание в розничном сегменте', 'DTR', default).render()
ExperementPlotter('транспортное запаздывание в оптовом сегменте', 'DTD', default).render()


#красные тона - для вспомогательных построений

#производство синим
#опт зеленым
#ретейл черным

nc = init_nc()
'''
animation_graphik(nc,
    ['RRR', 'SSF', 'SSD', 'SSR'],
    ['Заказы', 'Производство', 'Оптовые продажи', 'Розничные продажи'],
    ['red', 'blue', 'green', 'black', 'orange'], 'товары в неделю (ед./неделя)'
)


animation_graphik(nc,
    ['RRR', 'RRD', 'RRF'],
    ['Заказы потребителей', 'Заказы от розницы', 'Заказы от опта'],
    ['red', 'black', 'green', 'black'], 'заказы на товар (ед.)'
)

animation_graphik(nc,
    ['IAF', 'IAD', 'IAR'],
    ['Запасы на  производстве', 'Запасы на оптовой базе', 'Запасы на розничных складах'],
    ['blue', 'green', 'black', 'black'], 'товар (ед.)'
)


animation_graphik(nc,
    ['UOR', 'UOD', 'UOF'],
    ['Незавершенные заказы потребителей', 'Незавершенные заказы розницы', 'Незавершенные заказы опта'],
    ['red', 'blue', 'green', ], 'заказы на товар (ед.)'
)
'''

