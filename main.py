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


nc = FacadeModel()

nc['UOR'] = Level('RSR * (DHR + DUR)', 'RRR', 'SSR')
nc['IAR'] = Level('AIR * RSR', 'SRR', 'SSR')
nc['RSR'] = Level('RRR', 'RRR / DRR', 'RSR / DRR')

nc['SSR'] = Chouse('Min(STR,NIR)')
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

nc['SSD'] = Chouse('Min(STD, NID)')
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

nc['SSF'] = Chouse('Min(STF, NIF)')
nc['MDF'] = Chouse('Min(MWF, ALF)')
##############


nc['RRR'] = Source('Piecewise(( 1000, t < 3), ( 1000, t > 5) ,(2000, True) )')

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
nc['DPF'] = Constant('6')
nc['ALF'] = Constant('1500')
nc['DT'] = Constant(str(delta))


nc.auto_connect()

#print(nc['OPF'].get_out_value(0))

def animation_graphik(nc,nodes_name, lables, colors, max_lenght = 2):
    mp.ion()
    fig, ax = mp.subplots()
    mp.autoscale()

    tic = [step * delta for step in range(max_lenght)]

    dataset = [[nc[node_name].get_out_value(step * delta) for step in range(max_lenght)] for node_name in nodes_name]

    for set_index in range(len(dataset)):
        ax.plot(tic,dataset[set_index], label = lables[set_index], color = colors[set_index])

    mp.legend()

    for delay in range(0, 20000, 10):
        tic.append( (delay + max_lenght) * delta)
        if (len(tic) > max_lenght):
            tic.pop(0)

        for set_index in range(len(dataset)):
            dataset[set_index].append(nc[nodes_name[set_index]].get_out_value((delay + max_lenght) * delta))
            if(len(dataset[set_index]) > max_lenght):
                dataset[set_index].pop(0)

        for set_index in range(len(dataset)):
            ax.plot(tic, dataset[set_index], label=lables[set_index], color=colors[set_index])

        fig.canvas.draw()
        fig.canvas.flush_events()

    # Отключить интерактивный режим по завершению анимации
    mp.ioff()
    mp.show()




animation_graphik(nc,
    ['RRR', 'SSF', 'SSD', 'SSR'],
    ['Заказы', 'Производство', 'Оптовые продажи', 'Розничные продажи'],
    ['red', 'blue', 'green', 'black']
)


animation_graphik(nc,
    ['RRR', 'RRD', 'RRF'],
    ['Заказы от потребителя', 'Заказы от розницы', 'Заказы от опта'],
    ['red', 'blue', 'green']
)



